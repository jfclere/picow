import time
import network
import socket
import ssl

# Read configuration.
class Picow:
 def __init__(self):
  file = open('picow.conf', 'r')
  self.ssid = file.readline().strip()
  self.password = file.readline().strip()
  self.hostname = file.readline().strip()
  self.port = int(file.readline().strip())
  file.close
def readconf():
    return Picow()

conf = readconf()
print("ssid: " + conf.ssid + " password: " + conf.password + " hostname: " + conf.hostname + " port: " + str(conf.port))


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(conf.ssid, conf.password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
 if wlan.status() < 0 or wlan.status() >= 3:
  break
 max_wait -= 1
 print('waiting for connection...')
 time.sleep(1)

# Handle connection error
if wlan.status() != 3:
 raise RuntimeError('network connection failed')
else:
 print('connected')
 status = wlan.ifconfig()
 print( 'ip = ' + status[0] )

ai = socket.getaddrinfo(conf.hostname, conf.port)
print("Address infos:", ai)
addr = ai[0][-1]

# Create a socket and make a HTTP request
s = socket.socket()
print("Connect address:", addr)
s.connect(addr)
s = ssl.wrap_socket(s)
print(s)
s.write(b"GET / HTTP/1.0\r\n\r\n")

# Print the response
print(s.read(512))
