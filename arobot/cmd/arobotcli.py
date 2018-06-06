# -*- coding: utf-8 -*-
import argparse
import datetime
import os
import sys

import xlrd as xlrd
import xlwt as xlwt
from ironicclient import client
import json

from arobot.common import states
from arobot.common.config import CONF
from arobot.db import api as dbapi

DEFAULT_IRONIC_API_VERSION = '1.22'

VALID_FIELDS = ['index', 'sn', 'ipmi_addr', 'ipmi_netmask', 'ipmi_gateway']

def get_ironic_client():
    args = {
        'token': 'noauth',
        'endpoint': CONF.get('ironic', 'api_url'),
        'os_ironic_api_version': DEFAULT_IRONIC_API_VERSION,
        'max_retries': 30,
        'retry_interval': 2
    }
    return client.Client(1, **args)


def list_devices_raw():
    # Get devices from ironic
    icli = get_ironic_client()
    node_list = icli.node.list()
    db_api = dbapi.API()
    print('id            ', 'sn              ', 'state     ')
    node_num = 0
    for node in node_list:
        node_info = icli.node.get(node.uuid)
        sn = node_info.extra['serial_number']
        db_record = db_api.get_ipmi_conf_by_sn(sn)
        if not db_record:
            id = db_api.ipmi_conf_create({'sn': sn})
            print(id, sn, states.IPMI_CONF_RAW)
            node_num += 1
        elif db_record.state == states.IPMI_CONF_RAW:
            print(db_record.id, db_record.sn, db_record.state)
            node_num += 1

    print('There is total %d devices that should be configured.' % node_num)


def export_tpl():

    # Init workbook
    style0 = xlwt.easyxf('font: name Times New Roman,'
                         ' bold on', num_format_str='#,##0.00')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('ipmi conf')
    for col in range(len(VALID_FIELDS)):
        ws.write(0, col, VALID_FIELDS[col], style0)

    db_api = dbapi.API()
    all_raw_devices = db_api.get_all_ipmi_raw()
    row = 1
    for rd in all_raw_devices:
        ws.write(row, VALID_FIELDS.index('index'), row)
        ws.write(row, VALID_FIELDS.index('sn'), rd.sn)
        row += 1

    wb.save('ipmi_conf.xls')
    print('Generate ipmi_conf excel template ipmi_conf.xls successfully!')


def export_raid_xls():
    """
    export raid configuration in database to excel sheet
    notice that if configuration does not save in database successfully,
    it will not be able to be exported
    :return:
    """
    style0 = xlwt.easyxf('font: name Times New Roman,'
                         ' bold on; align: horiz center', num_format_str='#,##0.00')
    style1 = xlwt.easyxf('font: name Times New Roman,'
                         '; align: horiz center', num_format_str='#,##0.00')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('raid conf')

    RAID_FILEDS = ['index', 'sn', 'RAID 0', 'RAID 1', 'RAID 5', 'RAW']

    for col in range(len(RAID_FILEDS)):
        ws.write(0, col, RAID_FILEDS[col], style0)

    db_api = dbapi.API()
    all_raid_configs, _ = db_api.get_all_raid_config()
    row = 1
    for rd in all_raid_configs:
        ws.write(row, RAID_FILEDS.index('index'), row, style1)
        ws.write(row, RAID_FILEDS.index('sn'), rd.sn, style1)
        config = json.loads(rd.config)

        for key, val in config.items():
            if RAID_FILEDS.index(str(key)) >= 0:
                ws.write(row, RAID_FILEDS.index(key), ";".join([json.dumps(obj) for obj in val]), style1)

        row += 1


    # ws.col(0).width = 256*20
    wb.save('raid_config.xls')
    print('Generate raid_config excel template raid_config.xls successfully!')


def update_conf(conf):
    print('conf file: %s' % conf)
    # If conf file existed
    if not os.path.exists(conf):
        print('Please input configured file!')
        exit(1)

    book = xlrd.open_workbook(conf)
    sh = book.sheet_by_name('ipmi conf')
    # Validate fields of row 0
    for col in range(len(VALID_FIELDS)):
        if sh.cell_value(0, col) != VALID_FIELDS[col]:
            print('Invalid field: ', sh.cell_value(0, col),
                  ', should be ', VALID_FIELDS[col])
            exit(1)

    db_api = dbapi.API()
    icli = get_ironic_client()
    node_list = icli.node.list()
    for row in range(1, sh.nrows):
        confed_sn = sh.cell_value(row, VALID_FIELDS.index('sn'))
        confed_addr = sh.cell_value(row, VALID_FIELDS.index('ipmi_addr'))
        confed_netmask = sh.cell_value(row, VALID_FIELDS.index('ipmi_netmask'))
        confed_gateway = sh.cell_value(row, VALID_FIELDS.index('ipmi_gateway'))
        if db_api.get_ipmi_conf_by_sn(confed_sn):
            print('Bingo! %s IPMI conf will be updated...')
            print('sn ', confed_sn, ', ipmi addr ', confed_addr,', ipmi netmask ',
                  confed_netmask, ', ipmi gateway ', confed_gateway)
            conf_info = {
                'address': confed_addr,
                'netmask': confed_netmask,
                'gateway': confed_gateway,
                'state': states.IPMI_CONF_CONFED,
                'updated_at': datetime.datetime.now()
            }
            db_api.update_ipmi_conf_by_sn(confed_sn, conf_info)

            # Update driver info of nodes in ironic
            for node in node_list:
                node_info = icli.node.get(node.uuid)
                if node_info.extra['serial_number'] == confed_sn:
                    patches = [
                        {
                            'op': 'add',
                            'path': '/driver_info/ipmi_address',
                            'value': confed_addr
                        }
                    ]
                    icli.node.update(node.uuid, patches)


def main():
    parser = get_argparser()
    args = parser.parse_args()
    if args.list_devices_raw:
        list_devices_raw()
    elif args.export_tpl:
        export_tpl()
    elif args.update_conf:
        update_conf(args.update_conf)


def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-devices-raw',
                        help='Display devices basic info that is not processed',
                        action='store_true')
    parser.add_argument('--export-tpl', help='Export template of devices info',
                        action='store_true')
    parser.add_argument('--update-conf', metavar='infile',
                        help='Update devices info configured by user')
    parser.add_argument('--execute', metavar='device-or-all',
                        help='Execute automation tasks')
    parser.add_argument('--list-devices',
                        help='Display devices configurations',
                        action='store_true')
    return parser


if __name__ == '__main__':
    sys.exit(main())
