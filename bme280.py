from machine import Pin, I2C

DEVICE = 0x76
#i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
i2c.scan()

# Try to read something
REG_ID     = 0xD0
(chip_id, chip_version) = i2c.readfrom_mem(DEVICE, REG_ID, 2)
print("Chip ID     :" + str(chip_id))
print("Version     :" + str(chip_version))
