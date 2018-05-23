import configparser

CONF_FILE = '/etc/arobot/arobot.conf'


def get_config(conf_file):
    config = configparser.ConfigParser()
    config.read_file(open(conf_file))
    return config


CONF = get_config(CONF_FILE)
