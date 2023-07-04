# import picosleep
import time
import wifi
import machine

# main piece...
conf = wifi.Picow()

econnect = False
sleeptime = 10

while True:
    # the string we want to write
    try:
        conf.connectwifi()
        econnect = False
        print("after conf.connectwifi(()")
    except:
        econnected = True
        print("exception in conf.connectwifi()!")

    if not econnect:
        mess = "Hello!"
        mess = bytes(mess, 'utf-8')
        try:
            conf.sendserver(mess)
            print("after conf.sendserver()!")
        except:
            econnect = True
            print("exception in conf.sendserver()!")
        conf.disconnectwifi()
    else:
        print("Not connected!")

    time.sleep(sleeptime)
    # machine.lightsleep(sleeptime*1000)
