import json
import time

from influxdb import InfluxDBClient


def get_secrets():
    with open('/home/pi/Documents/Mobius/secret.txt') as s:
        secrets = json.load(s)
    return secrets


# Create the InfluxDB object as root
influxaccount = get_secrets()['InfluxAccount']


def write(data):
    try:
        client = InfluxDBClient(**influxaccount)
        client.write_points(data)
        client.close()
        return True
    except Exception as err:
        print(str(time.ctime()) + "    Error writing data to influx")
        # print(str(time.ctime()) + "    " + str(err))
        return False


def read(qry):
    client = InfluxDBClient(**influxaccount)
    results = client.query(qry)
    client.close()
    return results
