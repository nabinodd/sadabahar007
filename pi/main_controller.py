#! /usr/bin/python
import os
os.chdir('/home/pi/codebase/local/sadabahar007/pi/')
import time
import serial
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

#get activation threshold and run duration from database
hact_thres = int(session.query(ParamsDb.val).filter(ParamsDb.parm=='humifr_act_thres').all()[0][0])
hact_dur = int(session.query(ParamsDb.val).filter(ParamsDb.parm=='humifr_act_dur').all()[0][0])

# mqtt_server = ('xetronixlnx.local', 1883, 5)
# mqtt_server = ('coldpi.local', 1883, 5)

mqtt_server = ('localhost', 1883, 5)


notif_repeat_dur = 1800  #notification repeat duration in seconds
notif_pub_time = 0

co2 = 0.0
tmpr = 0.0
humi = 0.0

flup_on_sts = False
fldwn_on_sts = False

humifr_relay1_sts = False
humifr_relay2_sts = False

humifr_act_thres = hact_thres
humifr_strt_time = 0
humifr_stop_time = 0
humifr_act_durn = hact_dur
humifr_running = False

relay_cmd = False
send_relay_cmd = False

def pauseNotif():
   pause_notif = session.query(ParamsDb.val).filter(ParamsDb.parm=='pause_notif').all()[0][0]
   if pause_notif == 'True':
      return True
   elif pause_notif =='False':
      return False

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe('database/update_act_thres')
   client.subscribe('database/update_act_dur')

def on_message(client, userdata, msg):
   global sensor_data_zth,new_mqtt_data
   global humifr_act_thres, humifr_act_durn

   if msg.topic == 'database/update_act_thres':
      humifr_act_thres = int(msg.payload.decode())

   if msg.topic == 'database/update_act_dur':
      humifr_act_durn = int(msg.payload.decode())


client = mqtt.Client('main_service')
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server[0], mqtt_server[1], mqtt_server[2])

client.loop_start()


def inf():
   infs = '[INFO @ '+str(curr_time())+']'
   return infs

def err():
   errs = '[ERROR @ '+str(curr_time())+']'
   return errs

def curr_time():
   return int(time.time())

def strdatetime():
   return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

anano = serial.Serial('/dev/ttyUSB0', 9600, timeout = 3)
sprt_delay = 0.1
data_available = False

def nanoComm(serialport):
   global co2, tmpr, humi, flup_on_sts, fldwn_on_sts, hold_serial
   global humifr_relay1_sts, humifr_relay2_sts
   global send_relay_cmd, relay_cmd, data_available
   while True:
         try:
            anano.write(b'2\r\n') #request relay sts
            time.sleep(sprt_delay)
            rel_dta = anano.readline()
            # time.sleep(sprt_delay)
            
            anano.write(b'3\r\n') #request sensor data
            time.sleep(sprt_delay)
            sens_dta = anano.readline()
            # time.sleep(sprt_delay)

            anano.write(b'1\r\n') #request flsws sts
            time.sleep(sprt_delay)
            flsw_dta = anano.readline()
            # time.sleep(sprt_delay)

            rel_data = rel_dta.decode('ascii')
            rel_dataz = rel_data.split(',')

            humifr_relay1_sts = bool(int(rel_dataz[0]))
            humifr_relay2_sts = bool(int(rel_dataz[1]))

            sens_data = sens_dta.decode('ascii')
            sens_dataz = sens_data.split(',')
            co2 = float(sens_dataz[0])
            tmpr = float(sens_dataz[1])
            humi = float(sens_dataz[2])

            flsw_data = flsw_dta.decode('ascii')
            flsw_dataz = flsw_data.split(',')
            flup_on_sts = bool(int(flsw_dataz[0]))
            fldwn_on_sts = bool(int(flsw_dataz[1]))

            # print(inf(),'co2 = ',co2,' Tmpr = ',tmpr,' Humi = ',humi)
            # print(inf(),'u_switch = ',flup_on_sts, ' d_switch = ',fldwn_on_sts)
            # print(inf(),'hfr1 = ',humifr_relay1_sts, ' hfr2 = ',humifr_relay2_sts,'\n')

            if send_relay_cmd:
               if relay_cmd:
                  anano.write(b'4\r\n')
                  print(inf(),'relay ON')
                  time.sleep(sprt_delay)
                  send_relay_cmd = False
            
               elif not relay_cmd:
                  anano.write(b'5\r\n')
                  print(inf(),'relay OFF')
                  time.sleep(sprt_delay)
                  send_relay_cmd = False
            data_available = True
         
         except:
            print(err(),'/dev/ttyUSB0')
            time.sleep(0.5)
            data_available = False

         time.sleep(0.5)

nanomon_thr = threading.Thread(target=nanoComm,args=(anano,),daemon=True)
nanomon_thr.start()
# nanomon_thr.join()

def humiMonitor():
   global humifr_strt_time, humifr_act_durnn, humifr_running
   global humifr_stop_time, send_rel_on, send_rel_off
   global send_relay_cmd, relay_cmd
   while True:
      if data_available:
         if float(humi) < humifr_act_thres:
            if not humifr_running:
               humifr_strt_time = curr_time()
               humifr_running = True
               send_relay_cmd = True
               relay_cmd = True
               print(colored(inf()+'Humidifier started','green'))

         if curr_time()> humifr_strt_time + humifr_act_durn:           
            if humifr_running:
               humifr_stop_time = curr_time()
               humifr_running = False
               send_relay_cmd = True
               relay_cmd = False
               print(colored(inf()+'Humidifier Stopped','magenta'))

      time.sleep(0.1)

humi_mon_thr = threading.Thread(target=humiMonitor,daemon=True)
humi_mon_thr.start()

def flswMonitor():
   global notif_pub_time
   while True:
      if data_available:
         if not fldwn_on_sts:
            if curr_time()> notif_pub_time + notif_repeat_dur:
               # print(colored(inf()+'ALERT!!!!!!!!!!!!!','red'))
               if not pauseNotif():
                  client.publish('alphasadabahar007/notifreq',strdatetime())
                  print(inf(),'notification published')
                  notif_pub_time = curr_time()
      time.sleep(0.5)

flsw_mon_thr = threading.Thread(target=flswMonitor,daemon=True)
flsw_mon_thr.start()

# def publisher():
try:
   while True:
      sensor_dta = str(co2)+','+str(tmpr)+','+str(humi)
      flsw_sts = str(flup_on_sts)+','+str(fldwn_on_sts)
      relay_sts = str(humifr_relay1_sts)+','+str(humifr_relay2_sts)
   
      client.publish('sensor/data',sensor_dta)
      client.publish('flsw/sts',flsw_sts)
      client.publish('humifr/relay_sts',relay_sts)
      time.sleep(0.5)
   
except KeyboardInterrupt:
   # time.sleep(1)
   print(inf(),'Exitting>>>>>>>>>>>><<<<<<<<<<<')
   exit()

