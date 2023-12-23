# import picosleep
import time
import machine
import sys
from machine import Pin
import bme280
import adc
import os

import wifi
from nodeinfo import nodeinfo
from myprint import myprint, canprint, cantprint
# main piece...

econnect = False
sleeptime = 60
red = 22
green = 21
blue = 20

# a file was created to tell us to sleep.
try:
    f = open("sleep.txt", "r")
    f.close()
    os.remove("sleep.txt")
    # stop and reset after sleeptime
    time.sleep(1) # not os.sync() for the moment...
    machine.deepsleep(sleeptime*1000)
except:
    f = open("sleep.txt", "a")
    f.close()

pin_red = Pin(red, Pin.OUT, 0)
pin_green = Pin(green, Pin.OUT, 0)
pin_blue = Pin(blue, Pin.OUT, 0)

pin_usb = Pin('WL_GPIO2', Pin.IN)
usb = pin_usb.value()
if usb == 1:
    print("USB connected")
    try:
        os.remove("sleep.txt")
    except Exception as e:
        print("exception removing sleep.txt)!")
        print(str(e))
    canprint()
else:
    cantprint()

conf = wifi.Picow()
try:
    conf.connectwifi()
    econnect = False
    pin_blue.on()
    myprint("after conf.connectwifi(()")
except Exception as e:
    econnect = True
    myprint("exception in conf.connectwifi()!")
    myprint(str(e))

if not econnect:
    # the string we want to write
    mess = "empty message"
    try:
        mess = bme280.readtemp()
        val = adc.readval()
        mess = mess + "\nBat Val  : " + str(round(val, 2)) + "V"
    except Exception as e:
        myprint("exception while building message")
        myprint(str(e))
    mess = bytes(mess, 'utf-8')
    myinfo = nodeinfo()
    if myinfo.read(conf):
        # we retry in a minute...
        myprint("myinfo.read() Failed!")
        myinfo.WAIT_TIME = 60
    else:
        pin_green.on()
        url =  "/webdav/" + myinfo.REMOTE_DIR + "/temp.txt"
        try:
            conf.sendserver(mess, url)
            pin_red.on()
            myprint("after conf.sendserver()!")
        except:
            econnect = True
            myprint("exception in conf.sendserver()!")
    sleeptime =  myinfo.WAIT_TIME
else:
    myprint("Not connected!")

myprint("Sleeping: " + str(sleeptime))
if usb == 1:
    time.sleep(sleeptime)
    pin_red.off()
    pin_blue.off()
    pin_green.off()
machine.reset()
