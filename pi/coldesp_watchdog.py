#! /usr/bin/python

#to fix runn as service
# import os
# os.chdir('/home/pi/codebase/local/sadabahar007/pi/')

import time
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from termcolor import colored

from sqlalchemy import create_engine, false
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from db_handler import ParamsDb


database_name = 'database.db'
engine_address = 'sqlite:///'+database_name
engine = create_engine(engine_address)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


mqtt_server = ('xetronixlnx.local', 1883, 5)

esp_noconn_time_limit = 300
esp_conn_sts = True
first_req = False

notif_repeat_dur = 1800
notif_pub_time = 0

def curr_time():
   return int(time.time())

last_esp_msg_time = curr_time()

def inf():
   infs = '[INFO @ '+str(curr_time())+']'
   return infs
def err():
   errs = '[ERROR @ '+str(curr_time())+']'
   return errs

def strdatetime():
   return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

def pauseNotif():
   pause_notif = session.query(ParamsDb.val).filter(ParamsDb.parm=='pause_notif').all()[0][0]
   if pause_notif == 'True':
      return True
   elif pause_notif =='False':
      return False

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe('espid/resp/ht_sens')

def on_message(client, userdata, msg):
   global last_esp_msg_time, esp_conn_sts
   global first_req
   if msg.topic == 'espid/resp/ht_sens':
      print(inf(),'data : ',msg.payload.decode())
      last_esp_msg_time = curr_time()
      esp_conn_sts = True
      first_req = True

client = mqtt.Client('coldesp_watchdog')
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_server[0], mqtt_server[1], mqtt_server[2])
client.loop_start()

def espWatcher():
   global esp_conn_sts
   time.sleep(10)
   while True:
      try:
         if first_req:
            if curr_time() >= last_esp_msg_time+esp_noconn_time_limit:
               esp_conn_sts = False
               # print(colored(inf()+'NO CONNN!!!','red'))
               time.sleep(1)
      except:
         print(colored(err()+'espWatcher()','red'))
      finally:
         time.sleep(0.5)

def notifHandler():
   global notif_pub_time, notif_repeat_dur
   while True:
      try:
         if not esp_conn_sts:
            if curr_time()> notif_pub_time + notif_repeat_dur: 
               if not pauseNotif():
                  print(colored(inf()+'NOTIF','cyan'))
                  client.publish('alphasadabahar007/notifreq/espoff',strdatetime())
                  notif_pub_time = curr_time()
               else:
                  print(colored(inf()+'NOTIF PAUSED IN DB','magenta'))
      except:
         print(colored(err()+'notifHandler()','red'))
      finally:
         time.sleep(1)

threading.Thread(target=espWatcher,daemon=True).start()
threading.Thread(target=notifHandler,daemon=True).start()

while True:
   client.publish('espid/req/ht_sens',curr_time())
   print('\n')
   print(inf(),'PUB REQ')
   time.sleep(10)
   first_req = True