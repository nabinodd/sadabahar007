import time
from sqlalchemy import create_engine, Column, Integer, Text, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker,scoped_session

database_name = 'database.db'
engine_address = 'sqlite:///'+database_name
engine = create_engine(engine_address)

session_factory = sessionmaker(bind = engine)
session = scoped_session(session_factory)
Base = declarative_base()
meta = MetaData()

params_db = Table(
   'params_db',meta,
   Column('sn',Integer,nullable = False,primary_key = True, unique = True),
   Column('parm',Text,nullable = False),
   Column('val',Text,nullable = False)
)

class ParamsDb(Base):
   __tablename__ = 'params_db'
   sn = Column(Integer,nullable=False,primary_key=True, unique=True)
   parm = Column(Text,nullable = False)
   val = Column(Text,nullable = False)

   def __init__(self,parm,val):
         self.parm = parm
         self.val = val

meta.create_all(engine)

session.add(ParamsDb(parm = 'humifr_act_thres',val='60'))
session.add(ParamsDb(parm= 'humifr_act_dur',val='120'))     
session.commit()
print('COMMITTED @ ',time.time())