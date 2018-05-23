import logging

LOG_FILE = '/var/log/arobot/arobot.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s'
                           '[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_FILE)

LOG = logging.getLogger(__name__)
