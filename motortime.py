#!/usr/bin/env python3

# forward backlash in steps (something like 3 minutes)
BACKLASH = 25

import time, motor
class hourmin:
  def __init__(self): 
    self.hour = 0
    self.minu = 0

class motortime:
   def __init__(self):
     # reset to 00:00 if we don't have save
     self.step = self.restore()
     if self.step < 0:
       motor.reset()
       self.step = 0;
       self.store(0);
       # backlash to get 00:00
       motor.step_forward8(0.005, BACKLASH)

   def store(self, step):
     file = open('step.txt', 'w')
     string = str(step)
     file.write(string)
     file.close()

   def restore(self):
     try:
       file = open('step.txt', 'r')
       content = file.read()
       print(content)
       file.close()
       return int(content)
     except Exception as err:
       print("OS error:", err)
       print("restore failed resetting to 00:00")
       return -1

   def hourminu(self):
     currenttime = time.localtime()
     hour = currenttime[3]
     minu = currenttime[4]
     t = hourmin()
     t.hour = int(hour)
     if t.hour >= 12:
       t.hour = t.hour % 12
     t.minu = int(minu)
     return t

   def off(self):
     # Nothing for the moment...
     return

   def display(self, val):

     # At 00:00 make we go forward... and backward to be a 00:00
     # 6108 corresponds to 11:58
     if val.hour == 0 and val.minu == 0 and self.step >= 6108:
       # move 5 minutes forward and 10 backward (impossible mechanically)
       motor.step_forward8(0.005, 42)
       motor.step_backward8(0.005, 84)
       self.step = 0;
       self.store(0);
       # backlash to get 00:00
       motor.step_forward8(0.005, BACKLASH)
       return
     if val.hour == 0 and val.minu == 0 and self.step == 0:
       return

     # calculate the step we need
     mysteps = val.hour * motor.STEPS_PER_REVOLUTION
     # Calculate the minutes we 512 step per hour
     myminu = val.minu // 2
     rest = val.minu % 2
     mysteps = mysteps + myminu * 8 + myminu * 9 + rest * 8
     mysteps = mysteps - self.step 
     if mysteps == 0:
       return
     if mysteps > 0:
       print(mysteps)
       print(val.hour, val.minu)
       motor.step_forward8(0.005, mysteps)
     else:
       print(mysteps)
       print(val.hour, val.minu)
       motor.step_backward8(0.005, -mysteps)
     self.step = self.step + mysteps
     if self.step == motor.STEPS_PER_REVOLUTION * 12:
       self.step = 0
     if self.step > motor.STEPS_PER_REVOLUTION * 12:
        print(self.step)
     self.store(self.step)

# main for picow

print( "__main__")

myout = motortime()

while True:
  val = myout.hourminu()
  myout.display(val)
  time.sleep(1)
myout.off()
