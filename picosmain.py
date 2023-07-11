# import picosleep
import time
import wifi
import machine
import sys
from machine import Pin

# main piece...
conf = wifi.Picow()

econnect = False
deepsleep = True
sleeptime = 60
red = 22
green = 21
blue = 20

pin_red = Pin(red, Pin.OUT, 0)
pin_green = Pin(green, Pin.OUT, 0)
pin_blue = Pin(blue, Pin.OUT, 0)

pin_usb = Pin('WL_GPIO2', Pin.IN)
usb = pin_usb.value()
if usb == 1:
    print("USB connected")
    pin_green.on()
    deepsleep = False

while True:
    # the string we want to write
    if usb == 1:
        pin_green.on()
    try:
        conf.connectwifi()
        econnect = False
        pin_blue.on()
        if not deepsleep:
            print("after conf.connectwifi(()")
    except Exception as e:
        econnect = True
        if not deepsleep:
            print("exception in conf.connectwifi()!")
            print(str(e))
            sys.print_exception(e)

    if not econnect:
        mess = "Hello!"
        mess = bytes(mess, 'utf-8')
        try:
            conf.sendserver(mess)
            pin_red.on()
            if not deepsleep:
                print("after conf.sendserver()!")
        except:
            econnect = True
            if not deepsleep:
                print("exception in conf.sendserver()!")
    else:
        if not deepsleep:
            print("Not connected!")

    try:
        conf.disconnectwifi()
    except:
        if not deepsleep:
            print("exception in conf.disconnectwifi()!")

    pin_red.off()
    pin_blue.off()
    pin_green.off()
    if not deepsleep:
        print("Sleeping: " + str(sleeptime))
        time.sleep(sleeptime)
    else:
        machine.lightsleep(sleeptime*1000)
