import machine

# Read bat value using adc
# Not needed AGND (33)
# Not needed ADC_VREF (35)
# Use for example ADC0 (31) and the 3.3V as reference.
# for 12V bat: 100k + 10k resistors.
class myadc:
 def __init__(self, num):
    self.analog_value = machine.ADC(num)

 def readval(self):
    i = 0
    med = 0
    reading = self.analog_value.read_u16() # skip the first read
    while i < 10:
        reading = self.analog_value.read_u16()
        val = reading * (3.3 / 65536.0)
        # print("ADC: ",val)
        med = med + val
        i += 1
    return med / 10
