from pecan import rest, expose

from arobot.controllers.v1 import ipmi, raid


class Controller(rest.RestController):

    ipmi_conf = ipmi.IPMIConfController()
    raid_conf = raid.RAIDConfController()

    @expose()
    def index(self):
        return 'Welcome to the controller.'
