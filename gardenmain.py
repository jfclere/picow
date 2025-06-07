
# resistors to the battery
# 4.7k + 47k (should be ~ 11)
#  val = val *11.95 # my resistors are crappy!!!
# the vref is 3.3 for the picow intern vref
# it is on adc1
BATFACTOR = 11.95
PINBAT = 27
BATHIGH = 11.60

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
# delay between changes (to prevent useless switching
DELAYCHANGE = 20000 # 20 seconds

# import picosleep
import time
import machine
import sys
from machine import Pin
import os

# import our stuff
import myadc
from myprint import cantprint, canprint, myprint

bat_adc = myadc.myadc(1)
hyd_adc = myadc.myadc(0)
sol_adc = myadc.myadc(2)

# switch the board led on
led = Pin('LED', Pin.OUT)
led.on()

PANLED = 21
HYDLED = 22

pin_pan = Pin(PANLED, Pin.OUT, 0)
pin_hyd = Pin(HYDLED, Pin.OUT, 0)

pin_pan.off()
pin_hyd.on()

# works only on picow (WL_ is wifi!)
try:
  pin_usb = Pin('WL_GPIO2', Pin.IN)
  usb = pin_usb.value()
  if usb == 1:
    print("USB connected")
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
      canprint()
    else:
      cantprint()
  except:
    print("Something more was wrong...")

# next time to change the panel connection
deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
charging = True
while True:
  pin_hyd.toggle()
  led.toggle()
  valb = bat_adc.readval()
  # 4.7k + 47k (should be ~ 11)
  valb = valb * BATFACTOR # my resistors are crappy!!!
  mess = "Bat Val  : " + str(round(valb, 2)) + "V "
   
  val = hyd_adc.readval()
  mess = mess + "Hyd Val  : " + str(round(val, 2)) + " "
  val = sol_adc.readval()

  # 4.7k + 47k (should be ~ 11)
  val = val * SOLFACTOR # my resistors are crappy!!!
  mess = mess + "Sol Val  : " + str(round(val, 2)) + "V"

  # after the deadline: if more that BATHIGH disconnect the pannel
  if time.ticks_diff(deadline, time.ticks_ms()) < 0:
    # refresh deadline
    deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
    if valb > BATHIGH :
      pin_pan.on()
      if charging:
        myprint(mess)
      charging = False
    else:
      pin_pan.off()
      if not charging:
        myprint(mess)
      charging = True
  time.sleep(1)

pin_pan.off()
pin_hyd.off()
led.off()
