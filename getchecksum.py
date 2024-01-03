#!/usr/bin/python3
#
import requests
import hashlib
import binascii

r = requests.get('https://raw.githubusercontent.com/jfclere/picow/main/ocean.json')
data = r.json()

thehash = hashlib.sha256()
for key in data:
  print(key,":", data[key])
  if key == "urls":
    for file in data[key]:
      print("file:", file[0])
      print("url:", file[1])
      url = file[1].replace("github:", "https://raw.githubusercontent.com/")
      print("url:", url)
      last = url.rfind("/")
      val = url[0:last] + "/main/" + url[last:]
      print("url:", val)
      r = requests.get(val)
      # print("content:", r.content)
      thehash.update(r.content)
print(binascii.hexlify(thehash.digest()))
