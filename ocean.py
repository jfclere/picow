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

OCEANGPIO=19 ## 23 Controls the on-board SMPS Power Save pin!!!
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

pin_red.off()
pin_green.off()
pin_blue.off()
pin_ocean.off()

# wait until we have an IP
i = 1
while i < 3:
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
if i == 3:
  # We don't have network
  net = False
  machine.reset() 

if not net:
  print("NO Network!")
else:
  pin_blue.on()
  print("Connected")

myinfo = nodeinfo()
if myinfo.read(conf):
  # Use some default values
  print("myinfo.read() Failed!")
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False
else:
  pin_green.on()

reg = True
myreg = readreg()
if myinfo.MAINT_MODE:
  # Maintenance mode required
  try:
    myreg.init()
    myreg.read(0)
  except Exception as e:
    print("reading i2c failed")
    print(str(e))
    reg = False 
  try:
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg, conf)
  except Exception as e:
    print("report to server failed")
    print(str(e))
  print("myinfo.read() Failed maintenance mode!")
  # if we have i2c switch off for ~2 minutes
  if reg:
    try:
      stopatt(2)
    except Exception as e:
      print("stopatt failed")
  time.sleep(120)
  machine.reset() 

if myinfo.TIME_ACTIVE > 0:
  print("on for " + str(myinfo.TIME_ACTIVE) + " Minutes")
  try:
    pin_ocean.on()
    time.sleep(60*myinfo.TIME_ACTIVE)
  except Exception as e:
    print("pin_ocean.on failed")
    print(str(e))
  # JFC time.sleep(60*myinfo.TIME_ACTIVE)
  print("Done")

# end make sure to stop
pin_ocean.off()

# update register
if net:
  try:
    myreg.init()
    myreg.read(0)
  except Exception as e:
    print("reading i2c failed")
    print(str(e))
    reg = False 
  try:
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg, conf)
    updatereg(myinfo, myreg)
  except Exception as e:
    print("report to server failed")
    print(str(e))
    net = False

if reg:
  pin_red.on()

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
if reg:
  try:
    stopatt(myinfo.WAIT_TIME)
  except Exception as e:
    print("stopatt failed")
    print(str(e))
    reg = False 

# wait until we are stopped or not.
time.sleep(60*myinfo.WAIT_TIME)
while True:
  print("Done having fun looping!")
  time.sleep(1000)
  conf.sendstatustoserver("/machines/report-/machines/report-68fa56d97f7c4ad18b377cc5780ee6ff-loop")
