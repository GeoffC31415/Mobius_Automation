import random
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
import glob
import subprocess
import os

# DHT setup
sensor_DHT11 = Adafruit_DHT.DHT11
DHT_Pins = [
	4,  # Medium (water bath)
	17, # Long (centre of viv)
	27, # Not attached
	22  # Shortest wire (electricals box)
]
DHT_JITTER = 0.08

# One-wire setup
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
	
def read_watertemp_raw():
	catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines

def read_watertemp():
	lines = read_watertemp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_watertemp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
	return temp_c

def GetReading(sensorID):
	new_reading = -1
	
	if sensorID == 6:
		new_reading = read_watertemp()
		
	return new_reading

def GetDHTReading(sensorID):
	hum_reading = -1
	temp_reading = -1
		
	if sensorID <= len(DHT_Pins):
		# Get median of four
		humarray = []
		temparray = []
		readpin = DHT_Pins[sensorID-1]
		
		for x in range(0,3):
			humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, readpin)
			if humidity is not None:
				hum_reading = humidity
			if temperature is not None:
				temp_reading = temperature
			humarray.append(hum_reading)
			temparray.append(temp_reading)
		
		humarray.sort()
		temparray.sort()
		hum_reading = humarray[1] #middle of three
		temp_reading = temparray[1] #middle of three
		
		hum_reading += random.normalvariate(0,DHT_JITTER)
		temp_reading += random.normalvariate(0,DHT_JITTER)
		
	readings = [hum_reading, temp_reading]	
		
	return readings	
