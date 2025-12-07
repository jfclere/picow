import time
import wifi
import ntptime
import sys
from myprint import cantprint, canprint, myprint
from machine import Pin, I2C
from ht16k33 import HT16K33Segment

# For localtime
# Micropython esp8266
# This code returns the Central European Time (CET) including daylight saving
# Winter (CET) is UTC+1H Summer (CEST) is UTC+2H
# Changes happen last Sundays of March (CEST) and October (CET) at 01:00 UTC
# Ref. formulas : http://www.webexhibits.org/daylightsaving/i.html
#                 Since 1996, valid through 2099

def cettime():
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    return(cet)

# main piece...

pin_usb = Pin('WL_GPIO2', Pin.IN)
usb = pin_usb.value()
if usb == 1:
    print("USB connected")
    canprint()
else:
    cantprint()

conf = wifi.Picow()

conf.connectwifi()

myprint("Connected")

myprint(cettime())
ntptime.host = 'ch.pool.ntp.org'
try:
    ntptime.settime()
    myprint("Synchronized")
    myprint(cettime())
except Exception as err:
    myprint(err)

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
display = HT16K33Segment(i2c)
display.set_brightness(2)


synchronized = True
colon_state = True
while True:
    ct = cettime()
    count = ct[3] * 100 + ct[4]
    bcd = int(str(count), 16)
    display.set_number((bcd & 0xF000) >> 12, 0)
    display.set_number((bcd & 0x0F00) >> 8, 1)
    display.set_number((bcd & 0xF0) >> 4, 2)
    display.set_number((bcd & 0x0F), 3)
    display.set_colon(colon_state).draw()
    colon_state = not colon_state

    if ct[4] % 10 == 0 and not synchronized:
        # get host time every 10 minutes.
        try:
            ntptime.settime()
        except Exception as err:
            myprint(err)
        myprint("Synchronized at " + str(t.hour) + ":" + str(t.minu))
        synchronized = True
    if ct[4] % 10 != 0:
        synchronized = False
    time.sleep(1)
