import os
import hashlib
import binascii

def check(dirname):
  thehash = hashlib.sha256()
  for filename in os.listdir(dirname):
    with open(dirname + '/' + filename, 'r') as file:
      data = file.read()
      thehash.update(data)
  return thehash.digest()

def ischeck(dirname, val):
  thesum = check(dirname)
  theval = binascii.unhexlify(val)
  if thesum == theval:
    return True
  return False

def copyfiles(dirname):
  for filename in os.listdir(dirname):
    os.rename(dirname  + '/' + filename, '/' + filename)
