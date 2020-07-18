import RPi.GPIO as GPIO
import time

STEPPER_PINS = [18, 23, 24, 25]
HALFSTEP = [
	[1, 0, 0, 0],
	[1, 1, 0, 0],
	[0, 1, 0, 0],
	[0, 1, 1, 0],
	[0, 0, 1, 0],
	[0, 0, 1, 1],
	[0, 0, 0, 1],
	[1, 0, 0, 1]
]


def io_setup():
	GPIO.setmode(GPIO.BCM)
	for pin in STEPPER_PINS:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, 0)


def _set_stepper_pins(vals):
	for pin in range(4):
		GPIO.output(STEPPER_PINS[pin], vals[pin])


def _cycle(reverse=False):
	seq = HALFSTEP[::-1] if reverse else HALFSTEP
	for pinset in seq:
		_set_stepper_pins(pinset)
		time.sleep(0.005)


def _rotate(turns):
	reverse = False
	if turns < 0:
		turns = -turns
		reverse = True
		
	N = int(513 * turns)
	for i in range(N):
		_cycle(reverse)


def move_stepper(turns):
	io_setup()
	_rotate(turns)
	GPIO.cleanup()


def oscillate(turns):
	io_setup()
	try:
		while True:
			_rotate(turns)
			_rotate(-turns)
	except:
		pass
	finally:
		GPIO.cleanup()
