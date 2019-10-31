from __future__ import print_function
import time
import PullReading
import InfluxHandler
import pprint
from influxdb import InfluxDBClient
from datetime import datetime as dt

pp = pprint.PrettyPrinter(indent=4)

session = "vivarium"
runNo = dt.now().strftime("%Y%m%d%H%M")

delay = 10 # Extra delay per loop

def form_reading_set():
	# Gather readings
	print(str(time.ctime()) + "    Starting reading cycle...")
	
	DHTs = [PullReading.GetDHTReading(i) for i in [1,2,4]]
	waterTemp	= PullReading.GetReading(6) #One-wire, just outside log

	# Form JSON
	json_body = [
		{
		  "measurement": session,
		  "tags": {"run": runNo},
		  "fields": {
			  "Water_Temp" : float(waterTemp)
		  }
		}
	]
	
	# Do humidities seperately as they can be over 100
	# We want blanks in those cases where it's out of range
	for i, readings in enumerate(DHTs):
		# Humidities (accept 30-100)
		if readings[0] < 100 and readings[0] > 35:
			if i==2:
				sensor_name="DHT4_Hum"
			else:
				sensor_name="DHT{}_Hum".format(i+1)
				
			json_body[0]['fields'][sensor_name] = readings[0]
		# Temperatures (under 12 is an error)
		if readings[1] > 12:
			if i==2:
				sensor_name="DHT4_Temp"
			else:
				sensor_name="DHT{}_Temp".format(i+1)
				
			json_body[0]['fields'][sensor_name] = readings[1]
		
	pp.pprint(json_body[0]['fields'])
	return json_body

def write_points(data):
	InfluxHandler.write(data)
	print(str(time.ctime()) + "    Sensor Data Written to InfluxDB")

def main(args):
	while True:
		readings = form_reading_set()
		InfluxHandler.write(readings)
		time.sleep(delay)
	
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
