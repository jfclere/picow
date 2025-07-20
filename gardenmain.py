
# resistors to the battery
# 4.7k + 47k (should be ~ 11)
#  val = val *11.95 # my resistors are crappy!!!
# the vref is 3.3 for the picow intern vref
# it is on adc1
BATFACTOR = 12.30 # measured via IN219
PINBAT = 27
BATHIGH = 14.4
BATLOW = 10.0

# water sensor IDUINO
# https://cdn.manomano.com/pim-dam-img/350/48640213/dfe24ab828c121029632ef8efd87a759d3e2c3ef.pdf
# so a adc should be used
# it is powered with 3.3V
# it is on adc0
PINWAT = 26

# solar panel
# it is on adc2
SOLFACTOR = 11.95
PINSOL = 28

# delay between changes (to prevent useless switching)
# the valve is controled via IRF520
# VIN to 12V of the battery
# GND near it is the same as the GND near VCC and SIG
DELAYCHANGE = 20000 # 20 seconds

# Deepsleep time
SLEEPTIME = 60

# import picosleep
import time
import sys
from machine import Pin, WDT
import os

# import our stuff
import myadc
from myprint import cantprint, canprint, myprint, isusb
import wifi
from nodeinfo import nodeinfo

# trace logic
def mytrace(mess):
  f = open("trace.txt", "a")
  f.write(mess)
  f.write("\n")
  f.close()

# a file was created to tell us to sleep.
try:
    f = open("sleep.txt", "r")
    f.close()
    os.remove("sleep.txt")
    # stop and reset after sleeptime
    time.sleep(1) # not os.sync() for the moment...
    machine.deepsleep(SLEEPTIME*1000)
except:
    # we will sleep on the next restart
    f = open("sleep.txt", "a")
    f.close()

bat_adc = myadc.myadc(1)
# Read the battery charge and write debug file
valb = bat_adc.readval()
# 4.7k + 47k (should be ~ 11)
valb = valb * BATFACTOR # my resistors are crappy!!!
mess = "Bat : " + str(round(valb, 2))
mytrace(mess)

hyd_adc = myadc.myadc(0)
sol_adc = myadc.myadc(2)

# switch the board led on
led = Pin('LED', Pin.OUT)
led.on()
mess = "LED board on"
mytrace(mess)

PANLED = 21
HYDLED = 22

pin_pan = Pin(PANLED, Pin.OUT, 0)
pin_hyd = Pin(HYDLED, Pin.OUT, 0)

pin_pan.off()
pin_hyd.off()

# works only on picow (WL_ is wifi!)
try:
  pin_usb = Pin('WL_GPIO2', Pin.IN)
  usb = pin_usb.value()
  if usb == 1:
    print("USB connected")
    try:
        # Don't sleep in USB connected.
        os.remove("sleep.txt")
    except Exception as e:
        print("exception removing sleep.txt)!")
        print(str(e))
    canprint()
  else:
    cantprint()
except:
  print("Something was wrong...")
  try:
    SIE_STATUS=const(0x50110000+0x50)
    CONNECTED=const(1<<16)
    SUSPENDED=const(1<<4)
    if (machine.mem32[SIE_STATUS] & (CONNECTED | SUSPENDED))==CONNECTED:
      print("USB connected")
      try:
          # Don't sleep in USB connected.
          os.remove("sleep.txt")
      except Exception as e:
          print("exception removing sleep.txt)!")
          print(str(e))
      canprint()
    else:
      cantprint()
  except:
    print("Something more was wrong...")

mess = "After USB " + str(isusb())
mytrace(mess)
# Read the battery charge and go in sleep mode if not charged.
valb = bat_adc.readval()
# 4.7k + 47k (should be ~ 11)
valb = valb * BATFACTOR # my resistors are crappy!!!
mess = "Bat : " + str(round(valb, 2))
myprint(mess)
mytrace(mess)
if valb < BATLOW:
  if not isbus():
    # We will deepsleep for while waiting for the battery to charge.
    f = open("sleep.txt", "a")
    f.close()
    myprint("Going in deepsleep")
    machine.reset()
  else:
     myprint("NOT going in deepsleep USB connected!")

# connect to the wifi
econnect = False
conf = wifi.Picow()
i = 1
while i < 3:
  try:
    conf.connectwifi()
  except Exception as err:
    myprint("exception in conf.connectwifi()!")
    myprint(str(err))
    time.sleep(1)
    i += 1
    continue
  break
if i == 3:
  econnect = True
  mess = "No wifi!"
  myprint(mess)
  mytrace(mess)

# read where to send data
myinfo = nodeinfo()
conf.setserver(myinfo.server, 443, myinfo.login + ":" + myinfo.password)
if myinfo.read(conf):
  # Use some default values
  mess = "myinfo.read() Failed!"
  myprint(mess)
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False
  try:
    myinfo.readsavedinfo()
  except Exception as e:
    myprint('myinfo.readsaveinfo failed: Exception: ' + str(e))
etag = myinfo.ETAG

# watchdog timer 8388 is the max value
wdt = WDT(timeout=8000)  # enable it with a timeout of 8s
# next time to change the panel connection
deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
charging = True
while True:
  wdt.feed()
  led.toggle()
  valb = bat_adc.readval()
  # 4.7k + 47k (should be ~ 11)
  valb = valb * BATFACTOR # my resistors are crappy!!!
  if valb < BATLOW:
    # reset will trigger the deepsleep
    mess = "Reset bat low"
    mytrace(mess)
    machine.reset()
  mess = "Bat : " + str(round(valb, 2)) + "\n"
   
  val = hyd_adc.readval()
  mess = mess + "Hyd : " + str(round(val, 2)) + "\n"
  val = sol_adc.readval()

  # 4.7k + 47k (should be ~ 11)
  val = val * SOLFACTOR # my resistors are crappy!!!
  mess = mess + "Sol : " + str(round(val, 2)) + "\n"

  # after the deadline: if more that BATHIGH disconnect the pannel
  if time.ticks_diff(deadline, time.ticks_ms()) < 0:
    # refresh deadline
    deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
    if valb > BATHIGH :
      myprint("CHARGED: " + str(valb))
      pin_pan.on()
      if charging:
        myprint(mess)
      charging = False
    else:
      pin_pan.off()
      if not charging:
        myprint(mess)
      charging = True
    # send mess to the server
    mytrace(mess)
    url =  "/webdav/" + myinfo.REMOTE_DIR + "/value.txt"
    try:
      if econnect:
        # try reconnect
        conf.disconnectwifi()
        conf.connectwifi()
        econnect = False
      if not myinfo.read(conf):
        # check the etag for change.
        if etag != myinfo.ETAG:
          myprint("ETAG: " + etag + " New: " + myinfo.ETAG)
          etag = myinfo.ETAG
          pin_hyd.on()
          mess = mess + "Wat : 9.99\n"
          for _ in range(myinfo.TIME_ACTIVE):
            wdt.feed()
            time.sleep(1)
          pin_hyd.off()
      wdt.feed()
      conf.sendserver(mess, url)
      mess = "After sendserver"
      mytrace(mess)
    except Exception as e:
      econnect = True
      mess = "exception in conf.sendserver(): "
      mess = mess + str(e)
      myprint(mess)
      mytrace(mess)
  time.sleep(1)

pin_pan.off()
pin_hyd.off()
led.off()
