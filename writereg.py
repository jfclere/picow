#!/usr/bin/python3
# Write in the ATtiny registers
from struct import unpack
from machine import Pin, I2C

DEVICE = 0x04 # Default device I2C address
class writereg:


  def __init__(self):
    self.i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
    self.i2c.scan()

  def write(self, wait, val):
    # we can 0, 2, 4, 6, 8 or 16
    if wait == 2 or wait == 4 :
      # write batlow, batcharged
      mybytes = val.to_bytes(2, 'little')
      data = unpack('BB', mybytes)
      data = [ mybytes[0], mybytes[1] ]
      self.i2c.writeto_mem(DEVICE, wait, bytearray(data))
      return(data)
    elif wait == 8 :
      # write stopfor (long)
      mybytes = val.to_bytes(8, 'little')
      data = unpack('BBBBBBBB', mybytes)
      data = [ mybytes[0], mybytes[1], mybytes[2], mybytes[3], mybytes[4], mybytes[5], mybytes[6], mybytes[7] ]
      self.i2c.writeto_mem(DEVICE, wait,  bytearray(data))
      return(data)
    elif wait == 16:
      # write testmode
      mybytes = val.to_bytes(1, 'little')
      data = unpack('B', mybytes)
      data = [ mybytes[0] ]
      self.i2c.writeto_mem(DEVICE, wait, data)
      return(data)
