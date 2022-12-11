import time
import network
import socket
import ssl
import base64

import bme280

# Read configuration.
class Picow():
 def __init__(self):
   file = open('picow.conf', 'r')
   self.ssid = file.readline().strip()
   self.password = file.readline().strip()
   self.hostname = file.readline().strip()
   self.port = int(file.readline().strip())
   self.userpassword = file.readline().strip()
   file.close
 # connect to wifi
 def connectwifi(self):
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(self.ssid, self.password)

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
 # connect and send message to the server
 def sendserver(self, mess):

  ai = socket.getaddrinfo(self.hostname, self.port)
  print("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  print("Connect address:", addr)
  s.connect(addr)
  s = ssl.wrap_socket(s)
  print(s)

  # write it
  s.write(b"PUT /webdav/temp.txt HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  autho=b"Authorization: Basic " + base64.b64encode(bytes(self.userpassword, 'utf-8'))
  print(autho)
  s.write(bytes(autho, 'utf-8'))
  s.write(b"\r\n")
  contentlength = "Content-Length: " + str(len(mess))
  print(contentlength)
  s.write(bytes(contentlength, 'utf-8'))
  s.write(b"\r\n")
  s.write(b"Expect: 100-continue\r\n")
  s.write(b"\r\n")

  # Print the response (b'HTTP/1.1 100 Continue\r\n\r\n')
  print(s.read(25))

  # Write the content of the temp.txt file
  s.write(mess)

  print(s.read(512))

  # done close the socket
  s.close()
