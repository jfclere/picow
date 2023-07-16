import time
import network
import socket
import ssl
import base64

# Read configuration.
class Picow():
 def __init__(self):
   file = open('picow.conf', 'r')
   self.ssid = file.readline().strip()
   self.password = file.readline().strip()
   self.hostname = file.readline().strip()
   self.port = int(file.readline().strip())
   self.userpassword = file.readline().strip()
   file.close()
   self.wlan = network.WLAN(network.STA_IF)

 # read lets-encrypt-r3.der
 def getcadata(self):
   file = open('lets-encrypt-r3.der', 'rb')
   cadata = file.read()
   file.close()
   return bytes(cadata)

 # connect to wifi
 def connectwifi(self):
  self.wlan.active(True)
  self.wlan.connect(self.ssid, self.password)

  # Wait for connect or fail
  max_wait = 30
  while max_wait > 0:
    if self.wlan.status() < 0 or self.wlan.status() >= 3:
      break
    max_wait -= 1
    time.sleep(1)

  # Handle connection error
  if self.wlan.status() != 3:
    raise RuntimeError('network connection failed')

 # Get the IP addess
 def getip(self):
   if self.wlan.status() != 3:
     raise RuntimeError('network not connected')
   else:
     print('connected')
     status = self.wlan.ifconfig()
     return status[0] 

 # disconnect from wifi
 def disconnectwifi(self):
   self.wlan.disconnect()
   self.wlan.active(False)
   self.wlan.deinit()

 # connect and send message to the server
 def sendserver(self, mess):

  ai = socket.getaddrinfo(self.hostname, self.port)
  # print("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  # print("Connect address:", addr)
  s.connect(addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  s = ssl.wrap_socket(s, cadata=cadata)
  # print(s)

  # write it
  s.write(b"PUT /webdav/temp.txt HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  autho=b"Authorization: Basic " + base64.b64encode(bytes(self.userpassword, 'utf-8'))
  # print(autho)
  s.write(bytes(autho, 'utf-8'))
  s.write(b"\r\n")
  contentlength = "Content-Length: " + str(len(mess))
  # print(contentlength)
  s.write(bytes(contentlength, 'utf-8'))
  s.write(b"\r\n")
  s.write(b"Expect: 100-continue\r\n")
  s.write(b"\r\n")

  # Print the response (b'HTTP/1.1 100 Continue\r\n\r\n')
  # print(s.read(25))

  # Write the content of the temp.txt file
  s.write(mess)

  resp = s.read(512)

  # print(resp)

  # done close the socket
  s.close()
