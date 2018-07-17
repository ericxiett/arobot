from pecan.deploy import deploy
from arobot.common.config import CONF
import os


CONFIG_PATH = 'pecan_config_path'

# fix pecan configuration name
config_path = CONF.get('DEFAULT', CONFIG_PATH)
application = deploy(os.path.abspath(config_path))

