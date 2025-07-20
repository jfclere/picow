#!/usr/bin/python

import time
import binascii
import machine
import math
import sys
import os
from myprint import myprint

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
  ETAG=""

  # read the machine_id (/etc/machine-id)
  # read server info ($HOME/.netrc)
  def __init__(self):
    self.machine_id=str(binascii.hexlify(machine.unique_id()),"utf-8")
    try:
      text_file = open("machine-id");
      self.machine_id = text_file.readline().rstrip()
      text_file.close()
    except Exception as e:
      myprint('nodeinfo.__init__ Exception: ' + str(e))

    self.server="jfclere.myddns.me"
    try:
      text_file = open(".netrc")
    except Exception as e:
      myprint('nodeinfo.__init__ Exception: ' + str(e))
      return
    try:
      txt = text_file.readline()
    except Exception as e:
      myprint('nodeinfo.__init__ Exception: ' + str(e))
      text_file.close()
      return
    x = txt.split(" ")
    if x[0] == "machine":
      self.server=x[1].rstrip()
    try:
      txt = text_file.readline()
    except Exception as e:
      myprint('nodeinfo.__init__ Exception: ' + str(e))
      text_file.close()
      return
    x = txt.split(" ")
    if x[0] == "login":
      self.login=x[1].rstrip()
    try:
      txt = text_file.readline()
    except Exception as e:
      myprint('nodeinfo.__init__ Exception: ' + str(e))
      text_file.close()
      return
    x = txt.split(" ")
    if x[0] == "password":
      self.password=x[1].rstrip()
    text_file.close()

  # cut content of response in lines
  def readcontent(self, c):
    c = c.decode('ascii')
    s = c.split("\n")
    return s

  # get our configuration from server
  def read(self, wifi, wdt):
    myprint('nodeinfo.read')
    try:
      s = wifi.getfromserver('/machines/' + self.machine_id, wdt)
      if wdt is not None:
        wdt.feed()
      if not wifi.readwait(s, 50000, wdt):
        myprint('nodeinfo.read Timeout!')
        return True
      resp = s.read(512)
      if wdt is not None:
        wdt.feed()
      if len(resp) < 20:
        myprint('nodeinfo.read too small!')
        return True
      string = str(resp, "utf-8")
      # myprint("resp: " + string)
      headers = string.split("\r\n")
      i = 0
      l = 0
      status = 0
      indata = False
      for header in headers:
        # myprint("header: *" + header + "*")
        if "HTTP/" in header:
          # Status to read.
          cl = header.split(" ")
          # myprint(cl[1])
          status = int(cl[1])
          continue
        if "Content-Length:" in header:
          # Length to read.
          cl = header.split(": ")
          # myprint(cl[1])
          l = int(cl[1])
          continue
        if "ETag:" in header:
          # store etag
          etag = header.split(": ")
          # myprint(etag[1])
          self.ETAG=etag[1]
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
          # myprint("nodeinfo.read received: " + header)
          # myprint("nodeinfo.read received: " + str(len(header)))
          # myprint("nodeinfo.read received: " + str(l))
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
        return False
      return True
    except Exception as e:
      myprint('nodeinfo.read Exception: ' + str(e))
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
      myprint('nodeinfo.saveconf Exception: ' + str(e))
      return True
    return False

  # read saved info
  def readsavedinfo(self):
    f = open("savedconfig.txt", "r")
    i = 0
    for line in f:
      info=line.rstrip()
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
    f.close()

  # read saved version id
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
      myprint('nodeinfo.readsavedversion Exception: ' + str(e))
      return version
    return version

if __name__=='__main__':

  info = nodeinfo()
  myprint('server: ' + info.server)
  myprint('machine_id: ' + info.machine_id)
  if info.read():
    myprint("Failed")
  else:
    myprint(info.REMOTE_DIR)
    myprint(info.WAIT_TIME)
    myprint(info.BAT_LOW)
    myprint(info.GIT_VER)
    myprint(info.BATCHARGED)
    myprint(info.TIME_ACTIVE)
    info.save_conf()
    myprint("saved version: " + info.read_saved_version())
    myprint("Success")
