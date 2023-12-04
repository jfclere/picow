#!/usr/bin/python

import time
import math
import sys
import os
import requests
import socket

from nodeinfo import nodeinfo
from readreg import readreg

#
# This report information to the server
#

class reportserver:

  # report our information to the server
  def report(self, nodeinfo, readreg):
    try:
      val = readreg.read(0)
      val = str(val)
      r = requests.get('https://' + nodeinfo.server + '/machines/report-' + nodeinfo.machine_id + '-' + val)
      if (r.status_code != 404):
        return True
      val = readreg.read(6)
      val = str(val)
      r = requests.get('https://' + nodeinfo.server + '/machines/reportold-' + nodeinfo.machine_id + '-' + val)
      if (r.status_code != 404):
        return True
      # report ip
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      val = s.getsockname()[0]
      s.close()
      r = requests.get('https://' + nodeinfo.server + '/machines/reportip-' + nodeinfo.machine_id + '-' + val)
      if (r.status_code != 404):
        return True
    except Exception as e:
      print('Exception: ' + str(e))
      return True
    return False 

if __name__=='__main__':

  info = nodeinfo()
  print('server: ' + info.server)
  print('machine_id: ' + info.machine_id)
  if info.read():
    print("Failed no info!")
    exit()
  else:
    print(info.REMOTE_DIR)
    print(info.WAIT_TIME)
    print(info.BAT_LOW)
    print(info.GIT_VER)
    print(info.BATCHARGED)
    print(info.TIME_ACTIVE)

  reg = readreg()

  report = reportserver()
  if report.report(info, reg):
    print("Failed can't report")
  print("Done")
