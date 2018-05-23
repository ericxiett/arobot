from pecan import rest,expose

from arobot.common import states
from arobot.common.log_utils import LOG
from arobot.db import api

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

