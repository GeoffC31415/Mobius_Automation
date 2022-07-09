import RPi.GPIO as GPIO
import time

LIGHTPIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHTPIN, GPIO.OUT)
GPIO.output(LIGHTPIN, 0)

pwm = GPIO.PWM(18, 1000)
pwm.start(0)

def set(val):
	pwm.ChangeDutyCycle(val)
