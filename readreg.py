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
      mybytes = wait.to_bytes(1, 'little')
      data = [ mybytes[0] ]
      self.i2c.writeto(DEVICE, bytearray(data))
      replyb = self.i2c.readfrom(DEVICE,2)
      reply0 = int(replyb[0])
      reply1 = int(replyb[1])
      val = reply0 + (reply1 * 256)
      return(val)
    elif wait == 8 :
      # read stopfor (long)
      mybytes = wait.to_bytes(1, 'little')
      data = [ mybytes[0] ]
      self.i2c.writeto(DEVICE, bytearray(data))
      replyb = self.i2c.readfrom(DEVICE,4)
      reply0 = int(replyb[0])
      reply1 = int(replyb[1])
      reply2 = int(replyb[2])
      reply3 = int(replyb[3])
      val = ((reply3 * 256 + reply2)*256 + reply1) * 256 + reply0
      return(val)
    elif wait == 16:
      # read testmode
      mybytes = wait.to_bytes(1, 'little')
      data = [ mybytes[0] ]
      self.i2c.writeto(DEVICE, bytearray(data))
      val = self.i2c.readfrom(DEVICE,1)
      return(hex(val))
