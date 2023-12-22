#!/usr/bin/python

import socket

from nodeinfo import nodeinfo
from readreg import readreg
from myprint import myprint

#
# This report information to the server
#

class reportserver:

  # report our information to the server
  def report(self, nodeinfo, readreg, wifi):
    try:
      val = readreg.read(0)
      val = str(val)
      status = wifi.sendstatustoserver('/machines/report-' + nodeinfo.machine_id + '-' + val)
      if (status != 404):
         return True
      val = readreg.read(6)
      val = str(val)
      status = wifi.sendstatustoserver('/machines/reportold-' + nodeinfo.machine_id + '-' + val)
      if (status != 404):
         return True
      # report ip
      val = wifi.getip()
      status = wifi.sendstatustoserver('/machines/reportip-' + nodeinfo.machine_id + '-' + val)
      if (status != 404):
         return True
    except Exception as e:
      myprint('reportserver.report() Exception: ' + str(e))
      return True
    return False 

  def reportip(self, nodeinfo, wifi):
    try:
      # report ip
      val = wifi.getip()
      status = wifi.sendstatustoserver('/machines/reportip-' + nodeinfo.machine_id + '-' + val)
      if (status != 404):
         return True
    except Exception as e:
      myprint('reportserver.report() Exception: ' + str(e))
      return True
    return False 
