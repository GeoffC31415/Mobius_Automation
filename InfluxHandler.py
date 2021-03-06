from __future__ import print_function
from influxdb import InfluxDBClient
import time
import json

def get_secrets():
	with open('/home/pi/Documents/Mobius/secret.txt') as s:
		secrets = json.load(s)
	return secrets

# Create the InfluxDB object as root
influxaccount = get_secrets()['InfluxAccount']
client = InfluxDBClient(**influxaccount)

def write(data):
	try:
		client.write_points(data)
		return True
	except:
		# print(str(time.ctime()) + "    Error writing data to influx")
		return False

def read(qry):
	return client.query(qry)
