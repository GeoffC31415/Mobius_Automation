from __future__ import print_function
import RPi.GPIO as GPIO
import time
import os
import thread
import InfluxHandler
#from picamera import PiCamera
from datetime import datetime as dt
from datetime import timedelta as td

#
# Key parameters for climate control
#

TARGET_LOG_TEMP    = 31 # Degrees celsius
MORNING_LIGHT_ON   = 8  # Hour of the day
EVENING_LIGHT_OFF  = 22 # Hour of the day
PICTUREINTERVALHRS = 1  # Hours between photos

# Query to get recent average temp
TEMPQRY      = 'select mean(Water_Temp) from vivarium where time > now() - 5m'
TEMPNOW		 = 'select Water_Temp from vivarium order by time desc limit 1'

# Order here is relay 1 to 4
RELAY_PINS   = {
	'lamp': 26,
	'heatpad_backwall': 19,
	'heatpad_underlog': 13,
	'relay4': 6
}
relay_status = {
	'lamp': 0,
	'heatpad_backwall': 0,
	'heatpad_underlog': 0,
	'relay4': 0
} # 1 on 0 off

def archivePhoto(curfile,arcfile):
	try:
		os.rename(curfile, arcfile)
	except:
		print(str(time.ctime()) + '    File rename failed')

def getLightStatus(curtime):
	""" Light timer function. Determines the target state of the light 
		given a time. Works for both morning/evening and also overnight
		timings.
	
	Arguments:
		curtime (datetime) - The time to evaluate the light status at
		
	Returns:
		bool - True if the light should be on given the global on, off hours
			   False otherwise
	"""
	
	if MORNING_LIGHT_ON < EVENING_LIGHT_OFF:
		result = ((curtime.hour >= MORNING_LIGHT_ON) and (curtime.hour < EVENING_LIGHT_OFF))
	else:
		result = ((curtime.hour >= MORNING_LIGHT_ON) or (curtime.hour < EVENING_LIGHT_OFF))
	return result
	
def getHeaterStatus():
	""" Thermostat function. Queries temperature using Influx client, and compares to target.
	Seeing as the target temp lags heatpad, we want to enable immediately depending on target.
	
	Arugments: 
		target (float) - Target temp in celsius
		
	Returns:
		bool - True if actual temperature is below target. False otherwise.
			   If the temperature can't be determined, return True.
	"""
	
	try:
		result1 = InfluxHandler.read(TEMPNOW)
		temp_now = list(result1.get_points())
		
		if temp_now[0]['Water_Temp'] <= TARGET_LOG_TEMP:
			retval = True
		else:
			retval = False
	except:
		print(str(time.ctime()) + "    Unable to retrieve temperature for thermostat.")
		retval = True # If we can't get the current temp, turn on heater
	return retval
			
def set_relay(device, status):
	""" Set a given relay
	
	Arguments:
		device - Key in the relay dictionary in RELAY_PINS
		status - True for relay closed, false for relay open
		
	Returns:
		bool - True if there was an error accessing the DB, False otherwise
	"""
	global relay_status
	write_error = False
	
	if status != relay_status[device]:
		if status:
			GPIO.output(RELAY_PINS[device], GPIO.LOW)
			print(str(time.ctime()) + '        {} ON           '.format(device))
		else:
			GPIO.output(RELAY_PINS[device], GPIO.HIGH)
			print(str(time.ctime()) + '        {} OFF          '.format(device))
		relay_status[device] = status
		time.sleep(1)
	write_error = influxlog('{}_status'.format(device),status)
	return write_error

def influxlog(measurementstr, state):
	"""Add it into InfluxDB"""
	json_body = [{
		"measurement": "vivarium",
		"fields": {
			measurementstr : bool(state)
		}
	}]

	write_error = False
	InfluxHandler.write(json_body)
	return  write_error

def init_relays():
	# Set up General Purpose IO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	
	# Initialise relays
	print(str(time.ctime()) + '    Initialising all outputs to off...')
	for key in RELAY_PINS:
		GPIO.setup(RELAY_PINS[key], GPIO.OUT)
		GPIO.output(RELAY_PINS[key], GPIO.HIGH)
		influxlog('{}_status'.format(key),False)
		
	# Initialise camera
	#try:
	#	camera = PiCamera()
	#	camera.rotation = 180
	#	nextphototime = dt.now()
	#except:
	#	print(str(time.ctime()) + "    Could not initialise camera")

def main(args): 
	
	init_relays()
	
	# Primary loop
	while 1:
		curdt = dt.now()
		
		# Set all main relays
		write_error = False
		write_error = set_relay('lamp', getLightStatus(curdt))
		write_error |= set_relay('heatpad_backwall', getHeaterStatus())
		write_error |= set_relay('heatpad_underlog', getHeaterStatus())
			
		# Take photo if the interval has passed
		#if curdt > nextphototime:
		#	if True:
		#		curfile = '/var/www/html/Mobius_Website/images/image_recent.jpg'
		#		arcfile = '/var/www/html/Mobius_Website/images/archive/image_' + time.strftime("%Y%m%d%H%M%S") + '.jpg'
		#		archivePhoto(curfile,arcfile)
		#		try:
		#			camera.capture(curfile)
		#			print(str(time.ctime()) + '        IMAGE CAPTURED            ')
		#		except:
		#			print(str(time.ctime()) + '        Could not take picture            ')
		#		nextphototime = curdt + td(hours=PICTUREINTERVALHRS)
				
		time.sleep(30)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
