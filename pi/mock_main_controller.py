import random
import time
import paho.mqtt.client as mqtt

mqtt_server = ('xetronixlnx.local', 1883, 5)

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))


client = mqtt.Client('mock_main_controller')
client.on_connect = on_connect

client.connect(mqtt_server[0], mqtt_server[1], mqtt_server[2])

client.loop_start()

def curr_time():
   return int(time.time())

def getRandRange(a,b):
   return random.randint(a,b)


while True:
   client.publish('flsw/sts','1,1')
   client.publish('sensor/data',str(getRandRange(400,800))+','+str(getRandRange(0,50))+','+str(getRandRange(0,100)))

   client.publish('humifr/relay_sts','0,0')
   print('PUB @ ',time.time())
   time.sleep(3)