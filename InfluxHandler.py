from __future__ import print_function
from influxdb import InfluxDBClient
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

# InFlux DB variables for storing data points
host = "localhost"
port = 8086
dbname = "Mobius"

# Create the InfluxDB object as root
client = InfluxDBClient(host=host, port=port, database=dbname)

def write(data):
	try:
		client.write_points(data)
	except:
		print(str(time.ctime()) + "    Error writing data to influx")
		pp.pprint(data[0]['fields'])

def read(qry):
	return client.query(qry)
