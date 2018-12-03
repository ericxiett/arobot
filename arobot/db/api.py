import uuid

import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from arobot.common import states
from arobot.common.config import CONF
from arobot.db import models
import logging

LOG = logging.getLogger(__name__)


class API(object):
    def __init__(self):
        super(API, self).__init__()
        self._init_db_connect()

    def _init_db_connect(self):
        url = CONF.get('DEFAULT', 'db_connection')
        self.engine = sqlalchemy.create_engine(url)

    def get_ipmi_conf_by_sn(self, sn):
        session = sessionmaker(bind=self.engine)()
        try:
            ipmi_conf = session.query(models.IPMIConf).filter_by(
                sn=sn).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            ipmi_conf = None
        session.close()
        return ipmi_conf

    def ipmi_conf_create(self, ipmi_conf):
        session = sessionmaker(bind=self.engine)()
        ipmi_id = str(uuid.uuid4())
        session.add(
            models.IPMIConf(
                id=ipmi_id,
                sn=ipmi_conf.get('sn'),
                state=states.IPMI_CONF_RAW
            )
        )
        session.commit()
        session.close()
        return ipmi_id

    def get_all_ipmi_raw(self):
        session = sessionmaker(bind=self.engine)()
        all_raws = session.query(models.IPMIConf).filter_by(
            state=states.IPMI_CONF_RAW).all()
        session.close()
        return all_raws

    def get_all_ipmi(self):
        session = sessionmaker(bind=self.engine)()
        all_configs = session.query(models.IPMIConf).all()
        session.close()
        return all_configs

    def update_ipmi_conf_by_sn(self, sn, values):
        session = sessionmaker(bind=self.engine)()
        count = session.query(models.IPMIConf).filter_by(
            sn=sn).update(values)

        if count <= 0:
            # create new record and update
            ipmi_id = str(uuid.uuid4())
            session.add(models.IPMIConf(id=ipmi_id, sn=sn, state=states.IPMI_CONF_RAW))
            session.query(models.IPMIConf).filter_by(
                sn=sn).update(values)

        session.commit()
        session.close()

    def add_raid_conf(self, conf):
        """
        add RAID configuration to database
        :param conf: a dict object
        example:
        {
            "config": {
                "RAW": {},
                "RAID 0": {}
            },
            "sn": xxxxx
        }
        :return: ok: if RAID has been properly configured
        :return: err: possible errors
        """
        session = None
        err = None
        try:
            session = sessionmaker(bind=self.engine)()
            raid_id = str(uuid.uuid4())
            raid_conf = conf.get('config')

            if not isinstance(raid_conf, str) and not isinstance(raid_conf, unicode):
                raid_conf = json.dumps(raid_conf)

            session.add(
                models.RAIDConf(
                    id=raid_id,
                    sn=conf.get('sn'),
                    config=raid_conf
                )
            )
            session.commit()
        except Exception as e:
            LOG.error(e)
            err = e
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    err = e
                    LOG.error(" Failed closing session %s " % Exception)

        ok = False if err else True
        return ok, err

    def get_raid_config_by_sn(self, sn):
        """
        get raid configuration by given serial number
        :param sn:  serial number
        :return:  object if there is one
                  None if there is none
        """

        session = None
        err = None
        raid_config = None
        try:
            session = sessionmaker(bind=self.engine)()
            raid_config = session.query(models.RAIDConf).filter_by(sn=sn).one()
        except Exception as e:
            # exception will be thrown if no candidates
            LOG.error(e)
            err = e
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    err = e
                    LOG.error(" Failed closing session %s " % Exception)

        return raid_config, err

    def save_raid_opt(self, opt):
        session = None
        err = None

        try:
            session = sessionmaker(bind=self.engine)()
            session.add(models.RAIDOpt(
                id=str(uuid.uuid4()),
                sn=opt.get('sn', None),
                ssd=opt.get('ssd', 0),
                sas=opt.get('sas', 0),
                sata=opt.get('sata', 0),
                config=opt['config']
            ))
            session.commit()
        except Exception as e:
            LOG.error(e)
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    LOG.error('failed closing session', e)

    def save_all_raid_opts(self, opts):
        session = None
        err = None

        try:
            session = sessionmaker(bind=self.engine)()
            for opt in opts:
                session.add(models.RAIDOpt(
                    id=str(uuid.uuid4()),
                    sn=opt.get('sn', None),
                    ssd=opt.get('ssd', 0),
                    sas=opt.get('sas', 0),
                    sata=opt.get('sata', 0),
                    config=opt['config']
                ))
            session.commit()
        except Exception as e:
            LOG.error(e)
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    LOG.error('failed closing session', e)

    def get_all_raid_config(self):
        """
        get all existing RAID configurations
        :return: raid_configs : RAID configuration list
        :return: e: exceptions
        """

        session = None
        err = None
        raid_configs = None
        try:
            session = sessionmaker(bind=self.engine)()
            raid_configs = session.query(models.RAIDConf).all()
        except Exception as e:
            LOG.error(e)
            err = e
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    err = e
                    LOG.error(" Failed closing session %s " % Exception)

        return raid_configs, err
