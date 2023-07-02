# import picosleep
import time
import wifi
import bme280
import adc
# main piece...
conf = wifi.Picow()
print("ssid: " + conf.ssid + " password: " + conf.password + " hostname: " + conf.hostname + " port: " + str(conf.port))

conf.connectwifi()

sleeptime = 10

while True:
    # the string we want to write
    mess = bme280.readtemp()

    val = adc.readval()
    mess = mess + "\nBat Val  : " + str(round(val, 2)) + "V"
    mess = bytes(mess, 'utf-8')
    print(mess)
    conf.sendserver(mess)

    #picosleep.seconds(sleeptime)
    time.sleep(sleeptime)
