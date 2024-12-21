# picow
pico pi w stuff...

# to install use a picopython for pico w (https://micropython.org/download/rp2-pico-w/) or build it.
copy the picow.conf and wifi.py to the pico
```bash
ampy --port /dev/ttyACM0 put wifi.py
ampy --port /dev/ttyACM0 put picow.conf
ampy --port /dev/ttyACM0 put wpa_supplicant.conf
ampy --port /dev/ttyACM0 put your_main.py main.py
```
The picow.conf file contains:
```
hostname
port
user:password
```
# to start it use minicom
```
minicom -o -D /dev/ttyACM0
Welcome to minicom 2.8

OPTIONS: I18n 
Compiled on May 26 2022, 00:00:00.
Port /dev/ttyACM0, 17:50:56

Press CTRL-A Z for help on special keys


>>> 
MPY: soft reboot
MicroPython v1.19.1-724-gfb7d21153 on 2022-12-04; Raspberry Pi Pico W with RP2040
Type "help()" for more information.
>>> import wifi
ssid: xxxxxxxxxx password: xxxxxxxxxxxxxx hostname: jfclere.myddns.me port: 443
connected
ip = 192.168.1.116
Address infos: [(2, 1, 0, '', ('85.1.53.36', 443))]
Connect address: ('85.1.53.36', 443)
<_SSLSocket 2000b2b0>
b'HTTP/1.1 200 OK\r\nDate: Sun, 04 Dec 2022 16:58:42 GMT\r\nServer: Apache/2.4.54 (Fedora Linux) OpenSSL/3.0.5\r\nUpgrade: h2\r\nConnection: Upgrade, close\r\nLast-Modified: Mon, 20 Sep 2021 09:54:56 GMT\r\nETag: "26e-5cc6a45f79658"\r\nAccept-Ranges: byte'
>>> 
```

# Note on deepsleep()

## deepsleep() can prevent UBS to work.
If you reach a point you can't interrupt main.py from running you will have to erase the flash. I have used:

https://github.com/raspberrypi/pico-examples/blob/master/flash/nuke/nuke.c

Build it.

Use the standard process to copy the flash_nuke.uf2 in the USB mass storage.

Once the flash is cleaned just put back the standard uf2 micropython im the USB

I have reached 1.7 mA using a 3.7V LiPo Battery (mine has 3000mAh so enough for a long demo).

## deepsleep() doesn't switch off something you configure/using after (re)boot.
If you use wifi, gpio, i2c or adc after boot the deepsleep() will leave those on, in most of those cases the deepsleep() will just cause a reboot.

The reboot switch off everything so I have use a file to enter the deepsleep mode.

Writing in the flash does not prevent deepsleep() to work so all good.

# Note on ADC

Remember the Vref is 3.3V so you need a divider to measure a LIPO battery.
