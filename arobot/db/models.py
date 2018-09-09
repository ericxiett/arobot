import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

from arobot.common import states

Base = declarative_base()


class IPMIConf(Base):
    __tablename__ = 'ipmi_conf'

    id = Column(String(36), primary_key=True, nullable=False)
    sn = Column(String(64), nullable=False)
    address = Column(String(64), nullable=True)
    netmask = Column(String(64), nullable=True)
    gateway = Column(String(64), nullable=True)
    state = Column(String(20), default=states.IPMI_CONF_RAW, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)


class RAIDConf(Base):
    __tablename__ = 'raid_conf'

    id = Column(String(36), primary_key=True, nullable=False)
    sn = Column(String(64), unique=True, nullable=False)
    config = Column(Text)


class RAIDOpt(Base):

    # this name is a little misleading
    __tablenme__ = 'raid_opt'

    id = Column(String(36), primary_key=True, nullable=False)
    sn = Column(String(64), unique=True, nullable=True)
    ssd = Column(Integer)
    sata = Column(Integer)
    sas = Column(Integer)
    config = Column(Text)



