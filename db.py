# from config import login_pg, pass_pg, host_pg

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import visitors
from sqlalchemy.types import DateTime
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import create_engine

class Visitor(object):
    def __init__(self, status, num_in_day, id, work_place, name_service, reg_time, start_time, finish_time):
        self.status = status
        self.num_in_day = num_in_day
        self.id = id
        self.work_place = work_place
        self.name_service = name_service
        self.reg_time = reg_time
        self.start_time = start_time
        self.finish_time = finish_time

    def __repr__(self):
        return "<Visitor('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.status, self.num_in_day, self.id, self.work_place, self.name_service, self.reg_time, self.start_time, self.finish_time)

def setup_db(login, passwd, host):
    engine = create_engine(f'postgresql+psycopg2://{login}:{passwd}@{host}/', echo=True)
    metadata = MetaData()
    oo_visitors = Table('visitors', metadata,
        Column('status', String),
        Column('num_in_day', Integer),  
        Column('id', Integer, primary_key=True),
        Column('work_place', String),  
        Column('name_service', String),
        Column('reg_time', DateTime(timezone=True)),
        Column('start_time', DateTime(timezone=True)),
        Column('finish_time', DateTime(timezone=True))
    )

    metadata.create_all(engine)
    mapper(Visitor, oo_visitors)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session