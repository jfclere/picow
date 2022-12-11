# import picosleep
import time
import wifi
import bme280
# main piece...
conf = wifi.Picow()
print("ssid: " + conf.ssid + " password: " + conf.password + " hostname: " + conf.hostname + " port: " + str(conf.port))

conf.connectwifi()

sleeptime = 10

while True:
    # the string we want to write
    mess = bytes(bme280.readtemp(), 'utf-8')
    print(mess)
    conf.sendserver(mess)

    #picosleep.seconds(sleeptime)
    time.sleep(sleeptime)
