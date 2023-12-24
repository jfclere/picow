# import picosleep
import time
import binascii
from machine import Pin

import wifi
from nodeinfo import nodeinfo
from myprint import myprint, canprint, cantprint

led = Pin('LED', Pin.OUT)
pir = Pin(18, Pin.IN)
ledr = Pin(19, Pin.OUT)
sleeptime = 1
isUSBconnected = bool(machine.mem32[0x50110000 + 0x50] & (1<<16))
if isUSBconnected:
    sleeptime = 5
    canprint()
else:
    cantprint()

machine_id=str(binascii.hexlify(machine.unique_id()),"utf-8")
myprint("ID: " + machine_id);
starttime = time.localtime()
day = starttime[7]
myprint("Start day " + str(day))

conf = wifi.Picow()
try:
    conf.connectwifi()
    myprint("after conf.connectwifi(()")
except Exception as e:
    myprint("exception in conf.connectwifi()!")
    myprint(str(e))
    time.sleep(1)
    machine.reset()

myinfo = nodeinfo()

# wait trying to detect a move...
while True:
    myalarm = False
    if pir.value():
        myprint('Motion Detected')
        myalarm = True
    else:
        # Send a day I am up to the server
        now = time.localtime()
        nowday = now[7]
        if day != nowday:
            myprint('Day change Detected')
            myalarm = True
            day = nowday
    if myalarm:     
        # get the file in the server to trigger the alarm
        try:
            ledr.on()
            status = conf.sendstatustoserver('/machines/report-' + myinfo.machine_id + '-' + 'MOVES')
            if status != 404:
                myprint("Status not 404!")
        except Exception as e:
            myprint("Can't report")
            myprint(str(e))
            time.sleep(1)
            # We can't report or something the like...
            machine.reset()
    ledr.off()
    time.sleep(1)
    led.toggle()

while True:
    myprint('Something was wrong!')
    led.toggle()
    time.sleep(sleeptime)

machine.reset()
