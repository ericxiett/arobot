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
    def post(self, **kwargs):
        LOG.info("New RAID configuration received %s", kwargs)
        ok, err = self.dbapi.add_raid_conf(kwargs)

        if ok:
            return {
                "return_value": '1',
                'sn': kwargs.get('sn'),
                'message': 'raid configuration added correctly'
            }
        else:
            return {
                'return_value': '0',
                'sn': kwargs.get('sn'),
                'message': str(err)
            }

