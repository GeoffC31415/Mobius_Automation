import time
import PullReading
import pprint
from influxdb import InfluxDBClient
from datetime import datetime as dt

pp = pprint.PrettyPrinter(indent=4)

# InFlux DB variables for storing data points
host = "localhost"
port = 8086
dbname = "Mobius"
session = "vivarium"
runNo = dt.now().strftime("%Y%m%d%H%M")

delay = 10 # Extra delay on top of ~40seconds for sensor readings
 
# Create the InfluxDB object as root
client = InfluxDBClient(host=host, port=port, database=dbname)

while True:
	# Gather readings
	print str(time.ctime()) + "    Starting reading cycle..."
	
	DHTs = [PullReading.GetDHTReading(i) for i in [1,2,4]]
	waterTemp	= PullReading.GetReading(6) #One-wire, just outside log
	iso 		= time.ctime()

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
		if readings[1] > 13:
			if i==2:
				sensor_name="DHT4_Temp"
			else:
				sensor_name="DHT{}_Temp".format(i+1)
				
			json_body[0]['fields'][sensor_name] = readings[1]
		
	pp.pprint(json_body[0]['fields'])
	try:
		client.write_points(json_body)
		print str(iso) + "    Sensor Data Written to InfluxDB"
	except:
		#client.close()
		print(str(time.ctime()) + "    Couldn't write to InFlux this pass")
		client = InfluxDBClient(host=host, port=port, database=dbname)
	
	# Wait for next sample
	time.sleep(delay)
