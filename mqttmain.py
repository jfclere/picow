# sub.py
import time
import wifi
from umqttsimple import MQTTClient
import bme280
import myadc
import ussl

server="192.168.1.124"
ClientID = f'raspberry-sub-{time.time_ns()}'
user = "admin"
password = "admin"
topic = "topic/test"

pin_adc = myadc.myadc()

def connect():
    print('Connected to MQTT Broker "%s"' % (server))
    client = MQTTClient(ClientID, server, 8883, user, password, ssl=True, ssl_params={'cadata':getcadata(), 'cert_reqs':ussl.CERT_REQUIRED})
    client.connect()
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...' % (server))
    time.sleep(5)
    client.reconnect()

def getcadata():
   file = open('cacert.der', 'rb')
   cadata = file.read()
   file.close()
   return bytes(cadata)


try:
    client = connect()
except OSError as e:
    reconnect()

conf = wifi.Picow()

conf.connectwifi()

sleeptime = 10

while True:
  mess = "empty message"
  try:
    mess = bme280.readtemp()
    val = pin_adc.readval()
    mess = mess + "\nBat Val  : " + str(round(val, 2)) + "V"
  except Exception as e:
    print("exception while building message")
    print(str(e))
  print('send message %s on topic %s' % (mess, topic))
  client.publish(topic, mess, qos=0)
  time.sleep(sleeptime)
