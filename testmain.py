# import picosleep
import time
import wifi
# main piece...
conf = wifi.Picow()
print("ssid: " + conf.ssid + " password: " + conf.password + " hostname: " + conf.hostname + " port: " + str(conf.port))

conf.connectwifi()

sleeptime = 10

conf.getfromserver("main.py")
