#!/usr/bin/python3
# ocean 5V on gpio=23

import os
import time
import socket
import sys
import mip
import binascii

import wifi
from myprint import cantprint, canprint, myprint
from machine import Pin
from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg
from reportserver import reportserver
from checksum import check, ischeck, copyfiles

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
    myprint("batlow: " + str(batlow) + ":" + str(setbatlow))
    mywritereg = writereg()
    mywritereg.write(2, setbatlow)
  if setbatcharged > 0 and setbatcharged != batcharged:
    myprint("batcharged: " + str(batcharged) + ":" + str(setbatcharged))
    mywritereg = writereg()
    mywritereg.write(4, setbatcharged)

def stopatt(wait):
  mywritereg = writereg()
  mywritereg.write(8, wait)
  myreg = readreg()
  val = myreg.read(8)
  if val != wait:
    myprint("stopatt read doesn't give right value")
  # JFC not sure what to do... os.system("sudo init 0")

#
# main part...
#
pin_red = Pin(REDLED, Pin.OUT, 0)
pin_green = Pin(GREENLED, Pin.OUT, 0)
pin_blue = Pin(BLUELED, Pin.OUT, 0)
pin_ocean = Pin(OCEANGPIO, Pin.OUT, 0)

pin_red.off()
pin_green.off()
pin_blue.off()
pin_ocean.off()

pin_usb = Pin('WL_GPIO2', Pin.IN)
usb = pin_usb.value()
if usb == 1:
    print("USB connected")
    try:
        print(binascii.hexlify(check("/lib")))
    except Exception as e:
        print("exception in conf.connectwifi()!")
        myprint(str(e))
    canprint()
else:
    cantprint()

conf = wifi.Picow()
# wait until we have an IP
i = 1
while i < 3:
  try:
    conf.connectwifi()
    myprint("after conf.connectwifi(()")
  except Exception as e:
    myprint("exception in conf.connectwifi()!")
    myprint(str(e))
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
  myprint("NO Network!")
else:
  pin_blue.on()
  myprint("Connected")

myinfo = nodeinfo()
if myinfo.read(conf):
  # Use some default values
  myprint("myinfo.read() Failed!")
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False
  try:
    myinfo.readsavedinfo()
  except Exception as e:
    myprint('myinfo.readsaveinfo failed: Exception: ' + str(e))
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
    myprint("reading i2c failed")
    myprint(str(e))
    reg = False 
  try:
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg, conf)
  except Exception as e:
    myprint("report to server failed")
    myprint(str(e))
  myprint("myinfo.read() Failed maintenance mode!")
  # if we have i2c switch off for ~2 minutes
  if reg:
    try:
      stopatt(2)
    except Exception as e:
      myprint("stopatt failed")
  time.sleep(120)
  machine.reset() 

if myinfo.TIME_ACTIVE > 0:
  myprint("on for " + str(myinfo.TIME_ACTIVE) + " Minutes")
  try:
    pin_ocean.on()
    time.sleep(60*myinfo.TIME_ACTIVE)
  except Exception as e:
    myprint("pin_ocean.on failed")
    myprint(str(e))
  # JFC time.sleep(60*myinfo.TIME_ACTIVE)
  myprint("Done")

# end make sure to stop
pin_ocean.off()

# update register
if net:
  try:
    myreg.init()
    myreg.read(0)
  except Exception as e:
    myprint("reading i2c failed")
    myprint(str(e))
    reg = False 
  try:
    myreportserver = reportserver()
    if reg:
      myreportserver.report(myinfo, myreg, conf)
      updatereg(myinfo, myreg)
    myreportserver.reportip(myinfo, conf)
  except Exception as e:
    myprint("report to server failed")
    myprint(str(e))
    net = False

if reg:
  pin_red.on()

# update software
update = False
if net:
  try:
    ver = myinfo.readsavedversion()
    if ver == "":
      update = True
    if ver != myinfo.GIT_VER:
      # install in /lib
      mip.install("github:jfclere/picow/ocean.json")
      if ischeck("/lib", myinfo.GIT_VER):
        update = True
      else:
         myprint("software update check not OK!")
  except Exception as e:
    myprint("software update failed")
    myprint(str(e))

if update:
  myprint("copy files")
  try:
    copyfiles("/lib")
  except Exception as e:
    myprint("software update failed")
    myprint(str(e))
    update = False    
if update:
  myprint("saving version")
  myinfo.saveconf()
  
# stop and wait
if reg:
  try:
    stopatt(myinfo.WAIT_TIME)
  except Exception as e:
    myprint("stopatt failed")
    myprint(str(e))
    reg = False 

# wait until we are stopped or not.
myprint("Waiting for " +  str(myinfo.WAIT_TIME) + " Seconds") 
time.sleep(myinfo.WAIT_TIME)
machine.reset() 
