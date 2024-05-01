# sub.py
import time
import wifi
from umqttsimple import MQTTClient
import bme280
import myadc
import ussl
import binascii
import machine

server="192.168.1.124"
port=8883
ClientID = f'raspberry-sub-{time.time_ns()}'
user = "admin"
password = "admin"

pin_adc = myadc.myadc()

topic = "topic/" + str(binascii.hexlify(machine.unique_id()),"utf-8") + "/bme280"

print('Using MQTT Broker "%s"' % (server))
print('Using topic "%s"' % (topic))

def connect():
    print('Connected to MQTT Broker "%s"' % (server))
    client.connect()
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting to "%s"...' % (server))
    try:
        client.disconnect()
    except OSError as e:
        print("Reconnecting error")
        print(str(e))
        machine.reset()
    time.sleep(5)
    client.connect()

def getcadata():
   file = open('cacert.der', 'rb')
   cadata = file.read()
   file.close()
   return bytes(cadata)

conf = wifi.Picow()
server = conf.hostname
port = conf.port
userpass = conf.userpassword.split(":")
user = userpass[0]
password = userpass[1]
client = MQTTClient(ClientID, server, port, user, password, ssl=True, ssl_params={'cadata':getcadata(), 'cert_reqs':ussl.CERT_REQUIRED})

try:
    conf.connectwifi()
except Exception as e:
    print("exception in connectwifi()")
    print(str(e))
    time.sleep(10)
    machine.reset()

sleeptime = 10

try:
    client = connect()
except Exception as e:
    print("exception while connecting")
    print(str(e))
    try:
        reconnect()
    except Exception as e:
        print("exception while reconnecting")
        print(str(e))
        machine.reset()

print('Using MQTT Broker "%s"' % (server))
print('Using topic "%s"' % (topic))
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
  try:
    client.publish(topic, mess, qos=0)
  except Exception as e:
    print("exception while publishing message")
    print(str(e))
    reconnect()
  time.sleep(sleeptime)
