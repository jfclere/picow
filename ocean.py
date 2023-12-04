#!/usr/bin/python3
# ocean 5V on gpio=23

import os
import time
import socket
import wifi
from machine import Pin
from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg
from reportserver import reportserver

OCEANGPIO=23
REDLED = 22
GREENLED = 21
BLUELED=20

# update register of the ATtiny
def updatereg(nodeinfo, readreg):
  batlow = readreg.read(2)
  batcharged = readreg.read(4)
  setbatlow = nodeinfo.BAT_LOW
  setbatcharged = nodeinfo.BATCHARGED
  if setbatlow > 0 and setbatlow != batlow:
    print("batlow: " + str(batlow) + ":" + str(setbatlow))
    mywritereg = writereg()
    mywritereg.write(2, setbatlow)
  if setbatcharged > 0 and setbatcharged != batcharged:
    print("batcharged: " + str(batcharged) + ":" + str(setbatcharged))
    mywritereg = writereg()
    mywritereg.write(4, setbatcharged)

def stopatt(wait):
  mywritereg = writereg()
  mywritereg.write(8, wait)
  myreg = readreg()
  val = myreg.read(8)
  if val != wait:
    print("stopatt read doesn't give right value")
  # JFC not sure what to do... os.system("sudo init 0")

# main part...    

conf = wifi.Picow()

pin_red = Pin(REDLED, Pin.OUT, 0)
pin_green = Pin(GREENLED, Pin.OUT, 0)
pin_blue = Pin(BLUELED, Pin.OUT, 0)
pin_ocean = Pin(OCEANGPIO, Pin.OUT, 0)

# wait until we have an IP
i = 1
while i < 30:
  try:
    conf.connectwifi()
    print("after conf.connectwifi(()")
  except Exception as e:
    print("exception in conf.connectwifi()!")
    print(str(e))
    # JFC not sure what to do... need fix sys.print_exception(e)
    time.sleep(1)
    i += 1
    continue
  break
net = True 
if i == 30:
  # We don't have network
  net = False
  pin_blue.on()

if not net:
  print("NO Network!")
else:
  print("Connected")

myinfo = nodeinfo()
if myinfo.read():
  # Use some default values
  print("myinfo.read() Failed!")
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False

if myinfo.MAINT_MODE:
  # Maintenance mode required
  try:
    myreg = readreg()
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg)
  except: 
    print("report to server failed")
  print("myinfo.read() Failed maintenance mode!")
  # in fact if we don't have a conf what should we do???

if myinfo.TIME_ACTIVE > 0:
  print("on for " + str(myinfo.TIME_ACTIVE) + " Minutes")
  pin_ocean.on()
  time.sleep(60*myinfo.TIME_ACTIVE)
  print("Done")

# end make sure to stop
pin_ocean.off()

# update register
if net:
  try:
    myreg = readreg()
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg)
    updatereg(myinfo, myreg)
  except: 
    print("report to server failed")
    net = False

# update software
# if net:
#   try:
#     ver = myinfo.readsavedversion()
#     if ver != myinfo.GIT_VER:
#       cmd = "/home/pi/pisolar/gitver.sh " + myinfo.GIT_VER
#       if os.system(cmd):
#         print(cmd + " Failed")
#       else:
#         myinfo.saveconf()
#   except: 
#     print("software update failed")
# 

# stop and wait
stopatt(myinfo.WAIT_TIME)
