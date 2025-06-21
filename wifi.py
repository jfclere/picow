import time
import network
import socket
import select
import ssl
import base64
import ntptime
from myprint import myprint

SOCKTIMEOUT = 120.0

# Read configuration.
class Picow():
 def __init__(self):
   try:
     file = open('picow.conf', 'r')
     self.hostname = file.readline().strip()
     self.port = int(file.readline().strip())
     self.userpassword = file.readline().strip()
     file.close()
   except:
     self.hostname = "jfclere.myddns.me"
     self.port = 443
     self.userpassword = "admin:admin"

 def setserver(self, hostname, port, userpassword):
   self.hostname = hostname
   self.port = port
   self.userpassword = userpassword

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

 # do we see access points
 def hasAP(self):
  nets = self.wlan.scan()
  if len(nets) <=  0:
    return False
  return True

 # connect to wifi
 def connectwifi(self):
  self.wlan = network.WLAN(network.STA_IF)
  self.wlan.active(True)
  nets = self.wlan.scan()
  password = None
  for net in nets:
    ssid = net[0].decode('ascii')
    myprint("connectwifi trying: " + ssid)
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

  # print address
  myprint(self.getip())
  myprint(self.wlan.ifconfig())

  # Set time and date (for TLS?)
  try:
    ntptime.host = "de.pool.ntp.org"
    ntptime.settime()
  except:
    try:
      ntptime.host = "ntp.metas.ch"
      ntptime.settime()
    except:
      raise RuntimeError('can\'t set time')


  # check address resolver
  ## ai = socket.getaddrinfo("jfclere.myddns.me", 443)
  # myprint("Address infos:", ai)
  ## addr = ai[0][-1]
  ## myprint("Address infos:", ai)
  ## myprint("Address :", addr)

  ## self.sendstatustoserver("/machines/report-/machines/report-68fa56d97f7c4ad18b377cc5780ee6ff-titi")


 # Get the IP addess
 def getip(self):
   if self.wlan.status() != 3:
     raise RuntimeError('network not connected')
   else:
     myprint('connected')
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

# wait for data or timeout
 def readwait(self, s, mytime):
  poller = select.poll()
  poller.register(s, select.POLLIN)
  res = poller.poll(mytime)  # time in milliseconds
  if not res:
    #timeout
    myprint("timeout!")
    s.close()
    return False
  return True

 # connect and send message to the server
 # mess the mess
 # name the URL
 def sendserver(self, mess, name):

  myprint("sendserver: " + name)

  ai = socket.getaddrinfo(self.hostname, self.port)
  # myprint("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  # myprint("Connect address:", addr)
  s.settimeout(SOCKTIMEOUT)
  s.connect(addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  s = ssl.wrap_socket(s, cadata=cadata)
  # myprint(s)

  # write it
  s.write(b"PUT " + name + " HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  autho=b"Authorization: Basic " + base64.b64encode(bytes(self.userpassword, 'utf-8'))
  # myprint(autho)
  s.write(bytes(autho, 'utf-8'))
  s.write(b"\r\n")
  contentlength = "Content-Length: " + str(len(mess))
  # myprint(contentlength)
  s.write(bytes(contentlength, 'utf-8'))
  s.write(b"\r\n")
  s.write(b"Expect: 100-continue\r\n")
  s.write(b"\r\n")

  # Print the response (b'HTTP/1.1 100 Continue\r\n\r\n')
  # myprint(s.read(25))

  # Write the content of the temp.txt file
  s.write(mess)

  if not self.readwait(s, 50000):
    raise Exception("getfilefromserver: timeout")

  resp = s.read(512)

  # myprint(resp)

  # done close the socket
  s.close()


 # connect and return a socket to the server
 # connect and receive a file from server
 def getfromserver(self, name):

  myprint("getfromserver: " + name)

  ai = socket.getaddrinfo(self.hostname, self.port)
  # myprint("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  # myprint("Connect address:", addr)
  s.settimeout(SOCKTIMEOUT)
  s.connect(addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  s = ssl.wrap_socket(s, cadata=cadata)
  # myprint(s)

  # write request
  s.write(b"GET /")
  s.write(bytearray(name, 'utf8'))
  s.write(b" HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  s.write(b"\r\n")
  return s

 # connect and receive a file from server
 def getfilefromserver(self, name):
  s = self.getfromserver("/webdav/" + name)

  if not self.readwait(s, 50000):
    raise Exception("getfilefromserver: timeout")

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
      myprint(cl[1])
      l = int(cl[1])
      continue
    if l>0 and not indata:
      # We skip until empty line
      if len(header) == 0:
        indata = True
        continue
    if indata:
      # Store the line in a file
      myprint("data: " + header)
      f.write(header)
      size = size + len(header)
      if size == l:
        break # Done!
  while size < l:
    if not self.readwait(s, 50000):
      f.close()
      raise Exception("getfilefromserver: timeout")
    resp = s.read(512)
    f.write(resp)
    size = size + len(resp)
  f.close()
  # done close the socket
  s.close()

 # connect and send a get (STATUS) to server
 def sendstatustoserver(self, name):

  myprint("sendstatustoserver: " + self.hostname + ":" + str(self.port) + " " + name);
  
  status = self.wlan.ifconfig()
  # myprint("status: " + status[0])
  # status[3] = '8.8.8.8'
  #if status[2] == status[3]:
  #  myprint("status: " + status[2])
  #  myprint("status: " + status[3])
  #  self.wlan.ifconfig((status[0], status[1], status[2], '8.8.8.8'))
  # myprint("status: " + str(self.wlan.status()))
  # myprint("status: " + str(self.wlan.isconnected()))
  #status = self.wlan.ifconfig()
  # myprint("status: (3)" + status[3])
  ai = socket.getaddrinfo('jfclere.myddns.me', self.port)
  # myprint("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  ## s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s = socket.socket()
  s.settimeout(SOCKTIMEOUT)
  s.connect(addr)
  # myprint(s)
  # myprint("Connect address:", addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  s = ssl.wrap_socket(s, cadata=cadata)
  # myprint(s)

  # write request
  s.write(b"GET ")
  s.write(bytearray(name, 'utf8'))
  s.write(b" HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  s.write(b"\r\n")

  myprint("waiting response...")
  if not self.readwait(s, 50000):
    return 0
  resp = s.read(512)
  string = str(resp, "utf-8")
  headers = string.split("\r\n")
  for header in headers:
    myprint("header: " + header)
    if "HTTP/" in header:
      # Length to read.
      cl = header.split(" ")
      myprint(cl[1])
      l = int(cl[1])
      s.close()
      return l
  # done close the socket
  s.close()
  return 0
