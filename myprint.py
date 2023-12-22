def myprint(string):
  global canprint
  if canprint:
    print(string)

def cantprint():
  global canprint
  canprint = False
def canprint():
  global canprint
  canprint = True
