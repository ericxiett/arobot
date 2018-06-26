import socket
import time
import threading
import os
from pecan import rest, expose
from arobot.common import states
from arobot.common.log_utils import LOG
from arobot.db import api
from arobot.common.config import CONF
from arobot.cmd.arobotcli import get_ironic_client


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
            LOG.info("update ipmi_conf state to success.")

            ip = ipmi_conf.address
            username = CONF.get('ipmi', 'username')
            password = CONF.get('ipmi', 'password')
            LOG.info("start a sub thread ...")
            args = {
                'ip': ip,
                'username': username,
                'password': password,
                'frequency': '5',
                'port': '623',
                'sn': sn
            }
            ## start and subthread to check ipmi config and then do power off.
            t = threading.Thread(target=check_ipmi_and_shutdown, args=args ,name=sn)
            t.start()
            LOG.info("start thread success...")
        else:
            LOG.error("Config ipmi failed.Can't find ipmi_conf for sn: %s", sn)


def check_ipmi_and_shutdown(args):
    print ("")
    print("thread name = {}, thread id = {}".format(threading.current_thread().name, threading.current_thread().ident))
    ip = args.get('ip')
    username = args.get('username')
    password = args.get('password')
    frequency = args.get('frequency')
    port = args.get('port')
    sn = args.get('sn')
    LOG.info("IPMI config. start function:check_ipmi_and_shutdown")
    flag = check_connection(ip, port, frequency)
    LOG.info("IPMI config. check_connection return value : %s", flag)
    if flag:
        ##  ipmi address connection success.
        ##  do power off now.
        LOG.info("IPMI config success. power off server   sn = %s", sn)
        os.system(
            "echo %s && ipmitool -I lanplus -H %s -U %s -P '%s' power off " % (ip, ip, username, password))
    else:
        LOG.error("Config ipmi failed. ipmi address can't connect  sn=: %s", sn)


def check_connection(ip, port, frequency):
    sock = socket.socket()
    LOG.info("IPMI config. start function check_connection")
    while frequency >= 0:
        try:
            sock.connect((ip, port))
            LOG.info("Connected to %s on port %s", ip, port)
            return True
        except socket.error, e:
            LOG.info("Connection to %s on port %s failed: %s,"
                     " wait and try  %s times more ", ip, port, e, frequency)
            frequency -= 1
            time.sleep(3)
    return False
