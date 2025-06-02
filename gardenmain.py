
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
import myadc
import os

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

# next time to change the panel connection
deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
while True:
  pin_hyd.toggle()
  val = bat_adc.readval()
  # 4.7k + 47k (should be ~ 11)
  val = val * BATFACTOR # my resistors are crappy!!!
  mess = "Bat Val  : " + str(round(val, 2)) + "V "
  # after the deadline: if more that BATHIGH disconnect the pannel
  if time.ticks_diff(deadline, time.ticks_ms()) < 0:
    # refresh deadline
    deadline = time.ticks_add(time.ticks_ms(), DELAYCHANGE)
    if val > BATHIGH :
      pin_pan.on()
    else:
      pin_pan.off()
   
  val = hyd_adc.readval()
  mess = mess + "Hyd Val  : " + str(round(val, 2)) + " "
  val = sol_adc.readval()
  # 4.7k + 47k (should be ~ 11)
  val = val * SOLFACTOR # my resistors are crappy!!!
  mess = mess + "Sol Val  : " + str(round(val, 2)) + "V"
  print(mess)
  time.sleep(1)

pin_pan.off()
pin_hyd.off()
led.off()
