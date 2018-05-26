import ConfigParser

CONF_FILE = '/etc/arobot/arobot.conf'


def get_config(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config


CONF = get_config(CONF_FILE)
