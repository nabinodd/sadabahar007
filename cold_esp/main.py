import machine
import time
import uasyncio as asyncio
import dht

from lib.mqtt_as import MQTTClient, config

fname = 'main.py] '
inf = '[INFO/'+fname
err = '[ERROR/'+fname

ht_sens_pin = 21
ht_sens = dht.DHT11(machine.Pin(ht_sens_pin))  # type: ignore

sampling_delay = 1
new_ht_data_req = False
ht_data_reqtimest =''

SERVER = 'coldpi.local'
config['server'] = SERVER
config['ssid'] = 'Bhuvahsys Technologies'
config['wifi_pw'] = 'oNETWOTHREEFOUr'

def readSensor():
   ht_sens.measure()
   tmpr = ht_sens.temperature()
   humi = ht_sens.humidity()
   return(tmpr,humi)

async def conn_han(client):
   print(inf,'SUBS INIT @ ', time.time())
   await client.subscribe('espid/req/ht_sens', 1)   
   print(inf,'SUBS SUCCESS @ ', time.time(),'\n')
   time.sleep(1)
   # await asyncio.sleep(1)  # type: ignore

def on_message(topic,msg,retained):
   global new_ht_data_req, ht_data_reqtimest

   # print(topic,msg,retained, ' @ ',time.time())

   if topic == b'espid/req/ht_sens':
      ht_data_reqtimest = msg.decode()
      print(inf,'ht_sens_reqtimest : ',ht_data_reqtimest,' @ ',time.time(),'\n')
      new_ht_data_req = True

   else:
      print(inf,'ignoring ',topic,msg,retained, ' @ ',time.time())

config['subs_cb'] = on_message
config['connect_coro'] = conn_han

client = MQTTClient(config)


async def mqttReqRespHandler():
   global new_ht_data_req

   if new_ht_data_req:
      dta = readSensor()
      tmpr = dta[0]
      humi = dta[1]
      ht_data_resp = str(ht_data_reqtimest)+','+str(tmpr)+','+str(humi)
      new_ht_data_req = False
      await client.publish('espid/resp/ht_sens',ht_data_resp)
      print(inf,'HT_SENS RESP PUB ',ht_data_resp,' @ ',time.time(),'\n')


async def main():
   print(inf,'init MQTT CONN @ ',time.time())
   await client.connect()
   print(inf,'MQTT CONN SUCCESS @ ',time.time(),'\n')
   time.sleep(1)

   while True:         
      if new_ht_data_req:
         await mqttReqRespHandler()
      await asyncio.sleep(1)  # type: ignore

try:
   asyncio.run(main())  # type: ignore

except OSError:
   print(err,'OSERROR CAUSED!!!! @ ',time.time())
   time.sleep(1)
   machine.reset()