from pecan import rest, expose

from arobot.common.log_utils import LOG
from arobot.db import api


class RAIDConfController(rest.RestController):

    def __init__(self):
        super(RAIDConfController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def hello(self):
        return {'msg': 'Hello!'}

    @expose('json')
    def get(self, sn):
        """
        get raid configuration by serial number
        :param sn:  serial number
        :return:
        an object with following structure:
        {
            "is_ok": True/False,
            # RAID configuration parameters
        }
        """

        config, err = self.dbapi.get_raid_config_by_sn(sn)

        if err or config is None:
            LOG.error("error fetching configuration by given sn %s" % sn)
            return {
                'is_ok': "false"
            }
        else:
            LOG.info("successfully get configuration by given serial number")
            return {
                'is_ok': "true",
                'config': config.config,
                'sn': config.sn
            }

    @expose('json')
    def post(self, **kwargs):
        LOG.info("New RAID configuration received %s", kwargs)
        ok, err = self.dbapi.add_raid_conf(kwargs)

        if ok:
            LOG.info("RAID successfully configured on %s" % kwargs.get('sn'))
            return {
                "return_value": '1',
                'sn': kwargs.get('sn'),
                'message': 'raid configuration added correctly'
            }
        else:
            LOG.error("RAID configuration failed on %s" % kwargs.get('sn'))
            return {
                'return_value': '0',
                'sn': kwargs.get('sn'),
                'message': str(err)
            }

