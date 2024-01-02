# import picosleep
import time
import wifi
# main piece...
conf = wifi.Picow()

conf.connectwifi()

sleeptime = 10

mess="test"
conf.sendstatustoserver("/notfound/test")
conf.sendserver(mess, "/webdav/temp.txt")
conf.getfilefromserver("temp.txt")
