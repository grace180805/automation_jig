# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# Complete project details at https://RandomNerdTutorials.com

# try:
#   import usocket as socket
# except:
#   import socket
# 
# from machine import Pin
# import network

# import esp
# esp.osdebug(None)
# 
# import gc
# gc.collect()
# 
# ssid = 'AARnDW'
# password = 'znTEL3GhNj'
# 
# station = network.WLAN(network.STA_IF)
# 
# station.active(True)
# station.connect(ssid, password)
# 
# while station.isconnected() == False:
#   pass
# 
# print('Connection successful')
# print(station.ifconfig())
# 
# led = Pin(2, Pin.OUT)


# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/
from servo import Servo
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp

esp.osdebug(None)
import gc
gc.collect()

ssid = 'AARnDW'
password = 'znTEL3GhNj'
mqtt_server = b'78fec312d8054d7a91db5a68da9c9c29.s1.eu.hivemq.cloud'
mqtt_user = 'automation'
mqtt_pass = 'Abc-1234'

#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'#'
topic_pub = b'/automation/lock'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())