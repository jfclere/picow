#!/usr/bin/python

import time
import math
import sys
import os

#
# This class read the info the server has for us
#
# REMOTE_DIR where to store the information in the server
# WAIT_TIME time to wait before restarting
# BAT_LOW low battery (won't start below the value)
# GIT_VER git version of the repo to use (auto update)
# BATCHARGED disconnect charging device once the battery reaches that value
# TIME_ACTIVE time the pump will run

class nodeinfo:
  REMOTE_DIR="pisolar"
  WAIT_TIME=500
  BAT_LOW=500
  GIT_VER="5fe4895"
  BATCHARGED=773
  TIME_ACTIVE=2
  MAINT_MODE=False

  # read the machine_id (/etc/machine-id)
  # read server info ($HOME/.netrc)
  def __init__(self):
    self.machine_id="a470a4070ed946d2ad6b98a9cf130f7b"
    try:
      text_file = open("machine-id");
      self.machine_id = text_file.readline().rstrip()
      text_file.close()
    except Exception as e:
      print('nodeinfo.__init__ Exception: ' + str(e))

    self.server="jfclere.myddns.me"
    try:
      text_file = open(".netrc")
      txt = text_file.readline()
      text_file.close()
    except Exception as e:
      print('nodeinfo.__init__ Exception: ' + str(e))
      return
    x = txt.split(" ")
    if x[0] == "machine":
      self.server=x[1].rstrip()

  # cut content of response in lines
  def readcontent(self, c):
    c = c.decode('ascii')
    s = c.split("\n")
    return s

  # get our configuration from server
  def read(self, wifi):
    print('nodeinfo.read')
    try:
      s = wifi.getfromserver('/machines/' + self.machine_id)
      resp = s.read(512)
      string = str(resp, "utf-8")
      print("resp: " + string)
      headers = string.split("\r\n")
      i = 0
      l = 0
      status = 0
      indata = False
      for header in headers:
        print("header: *" + header + "*")
        if "HTTP/" in header:
          # Status to read.
          cl = header.split(" ")
          print(cl[1])
          status = int(cl[1])
          continue
        if "Content-Length:" in header:
          # Length to read.
          cl = header.split(": ")
          print(cl[1])
          l = int(cl[1])
          continue
        if l>0 and not indata:
          # We skip until empty line
          if len(header) == 0:
            indata = True
          continue
        if indata:
          if status != 200:
            continue # ignore response
          # Read the information
          print("nodeinfo.read received: " + header)
          print("nodeinfo.read received: " + str(len(header)))
          print("nodeinfo.read received: " + str(l))
          if len(header) == l:
            data = header.split("\n")
            for info in data:
              if i == 0:
                self.REMOTE_DIR=info
              if i == 1:
                self.WAIT_TIME=int(info)
              if i == 2:
                self.BAT_LOW=int(info)
              if i == 3:
                self.GIT_VER=info
              if i == 4:
                self.BATCHARGED=int(info)
              if i == 5:
                self.TIME_ACTIVE=int(info)
              i = i + 1
          continue
      s.close()
      return False
      if (status == 404):
        # 404 means mainteance
        self.MAINT_MODE=True
        r.close()
        return False
      r.close()
      return True
    except Exception as e:
      print('nodeinfo.read Exception: ' + str(e))
      return True

  # save configuration receive from server
  def saveconf(self):
    try:
      f = open("savedconfig.txt", "w")
      f.write(self.REMOTE_DIR)
      f.write("\n")
      f.write(str(self.WAIT_TIME))
      f.write("\n")
      f.write(str(self.BAT_LOW))
      f.write("\n")
      f.write(self.GIT_VER)
      f.write("\n")
      f.write(str(self.BATCHARGED))
      f.write("\n")
      f.write(str(self.TIME_ACTIVE))
      f.write("\n")
      f.close()
    except Exception as e:
      print('nodeinfo.saveconf Exception: ' + str(e))
      return True
    return False

  # read save version id
  def readsavedversion(self):
    version=""
    try:
      f = open("savedconfig.txt", "r")
      i = 0
      for line in f:
        if i == 3:
          version=line.rstrip()
          break
        i = i + 1
      f.close()
    except Exception as e:
      print('nodeinfo.readsavedversion Exception: ' + str(e))
      return version
    return version

if __name__=='__main__':

  info = nodeinfo()
  print('server: ' + info.server)
  print('machine_id: ' + info.machine_id)
  if info.read():
    print("Failed")
  else:
    print(info.REMOTE_DIR)
    print(info.WAIT_TIME)
    print(info.BAT_LOW)
    print(info.GIT_VER)
    print(info.BATCHARGED)
    print(info.TIME_ACTIVE)
    info.save_conf()
    print("saved version: " + info.read_saved_version())
    print("Success")