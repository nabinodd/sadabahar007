from codecs import BOM_LE
import time
from datetime import datetime


from sqlalchemy import DateTime, create_engine, Column, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session

inf = '[INFO/db_handler] '
err = '[ERROR/db_handler] '

database_name = 'database.db'
engine_address = 'sqlite:///'+database_name
engine = create_engine(engine_address)

session_factory = sessionmaker(bind = engine)
session = scoped_session(session_factory)
Base = declarative_base()

class ParamsDb(Base):
	__tablename__ = 'params_db'
	sn = Column(Integer,nullable=False,primary_key=True, unique=True)
	parm = Column(Text,nullable = False)
	val = Column(Text,nullable = False)

	def __init__(self,parm,val):
		self.parm = parm
		self.val = val


if __name__ == '__main__':
	while True:
		print('Running DB_HANDLER @ ', time.time())
		# queryByTimeRange(st_time,end_time)
		time.sleep(1)

