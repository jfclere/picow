import time
import network
import socket
import ssl
import base64

# Read configuration.
class Picow():
 def __init__(self):
   file = open('picow.conf', 'r')
   self.hostname = file.readline().strip()
   self.port = int(file.readline().strip())
   self.userpassword = file.readline().strip()
   file.close()

 # read lets-encrypt-r3.der
 def getcadata(self):
   file = open('lets-encrypt-r3.der', 'rb')
   cadata = file.read()
   file.close()
   return bytes(cadata)

  # Read wpa_supplicant.conf
 def readpassconf(self, ident):
   with open('wpa_supplicant.conf', 'r') as f:
     while True:
       line = f.readline()
       if not line:
         break
       line = line.strip()
       if line.startswith('ssid='):
         ssid = line.split('"')
       else:
         continue
       line = f.readline()
       if not line:
         break
       line = line.strip()
       if line.startswith('psk='):
         psk = line.split('"')
         if ssid[1] == ident:
           return psk[1]
   return None

 # connect to wifi
 def connectwifi(self):
  self.wlan = network.WLAN(network.STA_IF)
  self.wlan.active(True)
  nets = self.wlan.scan()
  password = None
  for net in nets:
    ssid = net[0].decode('ascii')
    print("connectwifi trying: " + ssid)
    password = self.readpassconf(ssid)
    if password:
      break

  if not password:
    raise RuntimeError('cannot find ssid/psk in wpa_supplicant.conf')
  self.wlan.connect(ssid, password)

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

 # stop wifi for deep sleep
 def swichoffwifi(self):
   # cause problems with deepsleep
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
  s.write(b"PUT /webdav/rp2040/temp.txt HTTP/1.1\r\n")
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


 # connect and receive a file from server
 def getfromserver(self, name):

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

  # write request
  s.write(b"GET /webdav/")
  s.write(bytearray(name, 'utf8'))
  s.write(b" HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  s.write(b"\r\n")

  resp = s.read(512)
  string = str(resp, "utf-8")
  headers = string.split("\r\n")
  l = 0
  size = 0
  indata = False
  f = open(name, "w")
  for header in headers:
    if "Content-Length:" in header:
      # Length to read.
      cl = header.split(": ")
      print(cl[1])
      l = int(cl[1])
      continue
    if l>0 and not indata:
      # We skip until empty line
      if len(header) == 0:
        indata = True
        continue
    if indata:
      # Store the line in a file
      print("data: " + header)
      f.write(header)
      size = size + len(header)
      if size == l:
        break # Done!
  while size < l:
    resp = s.read(512)
    f.write(resp)
    size = size + len(resp)
  f.close()
  # done close the socket
  s.close()
