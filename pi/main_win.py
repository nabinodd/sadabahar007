import time
import threading

import paho.mqtt.client as mqtt

import PyQt5.QtWidgets as qtw
# import PyQt5.QtCore as qtc

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from ui.main_win_base import Ui_MainWindow
from db_handler import ParamsDb

database_name = 'database.db'
engine_address = 'sqlite:///'+database_name
engine = create_engine(engine_address)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

mqtt_server = ('coldpi.local', 1883, 5)
# mqtt_server = ('localhost', 1883, 5)

new_mqtt_data = False


co2 = ''
tmpr = ''
humi = ''

flup_sts = ''
fldwn_sts = ''

humifr_relay_sts = ''

def client_loop():
   global client
   while True:
      time.sleep(0.1)

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe('sensor/data')
   client.subscribe('flsw/sts')
   client.subscribe('humifr/relay_sts')

def on_message(client, userdata, msg):
   global co2, tmpr, humi, new_mqtt_data
   global flup_sts, fldwn_sts, humifr_relay_sts

   if msg.topic == 'sensor/data':
      dta = msg.payload.decode()
      dtz = dta.split(',')
      co2 = dtz[0]
      tmpr = dtz[1]
      humi = dtz[2]
      new_mqtt_data = True

   if msg.topic == 'flsw/sts':
      fl_dta= msg.payload.decode()
      fl_dtz = fl_dta.split(',')
      flup_sts = fl_dtz[0]
      fldwn_sts = fl_dtz[1]
      new_mqtt_data =True

   if msg.topic == 'humifr/relay_sts':
      humif_dta = msg.payload.decode()
      humif_dtz = humif_dta.split(',')
      humifr_relay_sts = humif_dtz[0]
      # humifr_r2_sts = humif_dtz[1]
      new_mqtt_data = True

client = mqtt.Client('main_win')
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_server[0], mqtt_server[1], mqtt_server[2])
client.loop_start()


class Main_win_ui(qtw.QMainWindow):

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.m_win = Ui_MainWindow()
      self.m_win.setupUi(self)
      # self.resize(width,height)    

      hact_thres = session.query(ParamsDb.val).filter(ParamsDb.parm=='humifr_act_thres').all()[0][0]
      hact_dur = session.query(ParamsDb.val).filter(ParamsDb.parm=='humifr_act_dur').all()[0][0]


      self.m_win.l_edt_humifr_act_thres.setText(hact_thres)
      self.m_win.l_edt_humifr_act_dur.setText(hact_dur)
      self.m_win.pb_humifr_act_thres_set.clicked.connect(self.setHumiActThres)
      self.m_win.pb_humifr_act_dur_set.clicked.connect(self.setHumiActDuration)

      threading.Thread(target=self.updateData,daemon=True).start()

   def updateData(self):
      global new_mqtt_data
      togglecolor = True
      while True:
         togglecolor = not togglecolor
         if new_mqtt_data:
            self.m_win.lbl_co2_val.setText(co2)
            self.m_win.lbl_tmpr_val.setText(tmpr)
            self.m_win.lbl_humi_val.setText(humi)

            flupsts = 'ON' if flup_sts == 'True' else 'OFF'
            fldwnsts = 'ON' if fldwn_sts == 'True' else 'OFF'
            humifr_relaysts = 'ON' if humifr_relay_sts == 'True' else 'OFF'
            running_color = "background-color: blue;" if togglecolor else "background-color: green;"
            self.m_win.lbl_running.setStyleSheet(running_color)
            self.m_win.lbl_flup_val.setText(flupsts)
            self.m_win.lbl_fldwn_val.setText(fldwnsts)
            self.m_win.lbl_humifr_val.setText(humifr_relaysts)
   

            new_mqtt_data = False
         time.sleep(0.8)

   def setHumiActThres(self):
      inp_val = self.m_win.l_edt_humifr_act_thres.text()
      s = session.query(ParamsDb).get(1)
      s.val = inp_val
      session.commit()
      client.publish('database/update_act_thres',s.val)

   def setHumiActDuration(self):
      inp_val = self.m_win.l_edt_humifr_act_dur.text()
      s = session.query(ParamsDb).get(2)
      s.val = inp_val
      session.commit()
      client.publish('database/update_act_dur',s.val)

if __name__ == "__main__":
   client.loop_start()
   app = qtw.QApplication([])
   width = app.primaryScreen().size().width()
   height = app.primaryScreen().size().height()
   main_win_widget = Main_win_ui()
   main_win_widget.show()
   app.exec()
