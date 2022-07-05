import time
import machine
import network
import webrepl
# import esp
# esp.osdebug(0)
# import ntptime

ssid = 'Continuums'
passw = 'ONETWOTHREEFOUR'

print('\n\n\n\n[OK] boot success')

print('[INF] connecting to network')
print('[INF] SSID = ', ssid, 'PASSW = ', passw)
wlan = network.WLAN(network.STA_IF)  # type: ignore
wlan.active(True)
wlan.connect(ssid, passw)

wait_count = 0

while not wlan.isconnected() and wait_count<10:
   print('[INF] Waiting to connect network @ ',time.time(),', Retries : ',wait_count)
   time.sleep(1)
   wait_count = wait_count+1

r = machine.reset
wr = webrepl.start
wr()
# ntptime.settime()
print('[CFG] ',wlan.ifconfig())
if wlan.isconnected():
   print('[OK] ESP32 init SUCCESS\n\n\n\n')
else:
   print('[OK] ESP32 init FAIL\n\n\n\n')

