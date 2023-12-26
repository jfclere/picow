import machine

# Read bat value using adc0
class myadc():
 def __init__(self):
    self.analog_value = machine.ADC(0)

 def readval(self):
    i = 0
    med = 0
    reading = self.analog_value.read_u16() # skip the first read
    while i < 10:
        reading = self.analog_value.read_u16()
        val = (reading * 3.3 / 65536) * 2
        # print("ADC: ",val)
        med = med + val
        i += 1
    return med / 10
