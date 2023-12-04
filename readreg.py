#!/usr/bin/python3
# Tell ATtiny to power off for a while.
from machine import Pin, I2C

DEVICE = 0x04 # Default device I2C address
class readreg:

  def __init__(self):
    self.i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
    self.i2c.scan()

  def read(self, wait):
    # we can 0, 2, 4, 6, 8 or 16
    if wait == 0 or wait == 2 or wait == 4 or wait == 6 :
      # read val, batlow, batcharged
      self.i2c.writeto(DEVICE, wait)
      reply0 = int(self.i2c.readfrom(DEVICE,1))
      reply1 = int(self.i2c.readfrom(DEVICE,1))
      val = reply0 + (reply1 * 256)
      return(val)
    elif wait == 8 :
      # read stopfor (long)
      self.i2c.writeto(DEVICE, wait)
      reply0 = int(self.i2c.readfrom(DEVICE,1))
      reply1 = int(self.i2c.readfrom(DEVICE,1))
      reply2 = int(self.i2c.readfrom(DEVICE,1))
      reply3 = int(self.i2c.readfrom(DEVICE,1))
      val = ((reply3 * 256 + reply2)*256 + reply1) * 256 + reply0
      return(val)
    elif wait == 16:
      # read testmode
      self.i2c.writeto(DEVICE, wait)
      val = self.i2c.readfrom(DEVICE,1)
      return(hex(val))
