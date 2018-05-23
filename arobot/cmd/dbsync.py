import sqlalchemy
import sys

from arobot.common.config import CONF
from arobot.db import models


def main():
    url = CONF.get('DEFAULT', 'db_connection')
    print('url: %s' % url)
    engine = sqlalchemy.create_engine(url, echo=True)
    # Clean
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    sys.exit(main())
