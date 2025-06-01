
# import picosleep
import time
import machine
import sys
from machine import Pin
import myadc
import os

pin_adc = myadc.myadc(1)

while True:
  val = pin_adc.readval()
  # 4.7k + 47k (should be ~ 11)
  val = val *11.95 # my resistors are crappy!!!
  mess = "\nBat Val  : " + str(round(val, 2)) + "V" + "\n"
  print(mess)
  time.sleep(1)
