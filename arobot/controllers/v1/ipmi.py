import time

import os
from pecan import rest,expose
from arobot.common import states
from arobot.common.log_utils import LOG
from arobot.db import api
from arobot.common.config import CONF

class IPMIConfController(rest.RestController):
    def __init__(self):
        super(IPMIConfController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def hello(self):
        return {'msg': 'Hello!'}

    @expose('json')
    def get(self, sn):
        LOG.info('Got ipmi configuration get request, sn: %s', sn)

        ipmi_conf = self.dbapi.get_ipmi_conf_by_sn(sn)
        LOG.info('node %s ipmi conf: %s', sn, ipmi_conf)
        if ipmi_conf is not None and \
                ipmi_conf.state == states.IPMI_CONF_CONFED:
            return {
                'return_value': '1',
                'sn': sn,
                'ipmi_address': ipmi_conf.address,
                'ipmi_netmask': ipmi_conf.netmask,
                'ipmi_gateway': ipmi_conf.gateway
            }
        else:
            return {
                'return_value': '0',
                'sn': sn,
                'message': 'Device not found'
            }

    @expose('json')
    def put(self, sn):
        LOG.info('Config ipmi success, sn: %s', sn)
        ipmi_conf = self.dbapi.get_ipmi_conf_by_sn(sn)
        LOG.info(ipmi_conf)
        if ipmi_conf is not None and ipmi_conf.state == states.IPMI_CONF_CONFED:
            values = {"state": states.IPMI_CONF_SUCCESS}
            update_result = self.dbapi.update_ipmi_conf_by_sn(sn, values)
            shutdown_delay = CONF.get('ipmi', 'shutdown_delay')
            #sleep
            time.sleep(shutdown_delay)
            ip = ipmi_conf.address
            password = CONF.get('ipmi', 'password')
            try:
                os.system("echo %s && ipmitool -I lan -H %s -U root -P '%s' power off " % (ip, ip, password))
            except OSError, error:
                LOG.error(error)
        else:
            LOG.error("Config ipmi failed.Can't find ipmi_conf for sn: %s",sn)