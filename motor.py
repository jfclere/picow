"""
This is picow code for micro python.
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-28byj-48-stepper-motor-uln2003-driver
"""


import time
from machine import Pin

# Define GPIO pins for ULN2003 driver
# Red is a +5V always...
# Orange IN1
# Yellow IN2
# Pink IN3
# Blue IN4

IN1 = 21
IN2 = 20
IN3 = 19
IN4 = 18

# configure pins
pin1 = Pin(IN1, Pin.OUT, 0)
pin2 = Pin(IN2, Pin.OUT, 0)
pin3 = Pin(IN3, Pin.OUT, 0)
pin4 = Pin(IN4, Pin.OUT, 0)
led = Pin('LED', Pin.OUT)

# Define constants
# the specs say:
# Steps/revolution 	32
# Gears 	64:1 reduction
STEPS_PER_REVOLUTION = 512
#DEG_PER_STEP = 1.8
#STEPS_PER_REVOLUTION = int(360 / DEG_PER_STEP)

# Define sequence for 28BYJ-48 stepper motor
# Try from https://components101.com/motors/28byj-48-stepper-motor
#   [O, Y, P, B]
se8 = [
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 1]
]
#   [O, Y, P, B]
se4 = [
    [0, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 1]
]

# Function to rotate the stepper motor one step
def step(delay, step_sequence):
    pin1.value(step_sequence[0])
    pin2.value(step_sequence[1])
    pin3.value(step_sequence[2])
    pin4.value(step_sequence[3])
    time.sleep(delay)
    pin1.value(0)
    pin2.value(0)
    pin3.value(0)
    pin4.value(0)

# Functions to move the stepper motor one step forward
def step_forward(delay, steps):
    led.on()
    for _ in range(steps):
        step(delay, se4[0])
        step(delay, se4[1])
        step(delay, se4[2])
        step(delay, se4[3])
    led.off()

def step_forward8(delay, steps):
    led.on()
    for _ in range(steps):
        step(delay, se8[0])
        step(delay, se8[1])
        step(delay, se8[2])
        step(delay, se8[3])
        step(delay, se8[4])
        step(delay, se8[5])
        step(delay, se8[6])
        step(delay, se8[7])
    led.off()

# Functions to move the stepper motor one step backward
def step_backward(delay, steps):
    led.on()
    for _ in range(steps):
        step(delay, se4[3])
        step(delay, se4[2])
        step(delay, se4[1])
        step(delay, se4[0])
    led.off()

def step_backward8(delay, steps):
    led.on()
    for _ in range(steps):
        step(delay, se8[7])
        step(delay, se8[6])
        step(delay, se8[5])
        step(delay, se8[4])
        step(delay, se8[3])
        step(delay, se8[2])
        step(delay, se8[1])
    led.off()

def reset():
     delay = 0.005
     for _ in range(12):
        step_backward8(delay, STEPS_PER_REVOLUTION)

def main():
    try:
        # time the step command sequence is applied.
        delay = 0.005
        # delay = 1

        print(se4)
        print(STEPS_PER_REVOLUTION)
        step_forward8(delay, 1)
        return

        while True:
            # Rotate one revolution forward (clockwise)
            step_forward8(delay, STEPS_PER_REVOLUTION)
            # step_backward(delay, STEPS_PER_REVOLUTION)

            # Pause for 2 seconds
            time.sleep(2)

            # Rotate one revolution backward (anticlockwise)
            step_backward8(delay, STEPS_PER_REVOLUTION)

            # Pause for 2 seconds
            # time.sleep(2)

    except KeyboardInterrupt:
        print("\nExiting the script.")
    except Exception as e:
        print(str(e))

# main for micropython tests
#main()
#while True:
#    led.toggle()
#    print("Done???")
#    # Pause for 2 seconds
#    time.sleep(2)
