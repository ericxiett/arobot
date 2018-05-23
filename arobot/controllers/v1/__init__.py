from pecan import rest, expose

from arobot.controllers.v1 import ipmi


class Controller(rest.RestController):

    ipmi_conf = ipmi.IPMIConfController()

    @expose
    def index(self):
        return 'Welcome to the controller.'
