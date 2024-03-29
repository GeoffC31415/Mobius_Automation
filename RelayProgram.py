import RPi.GPIO as GPIO
import time
import os

import InfluxHandler
import PullReading

from datetime import datetime as dt
from datetime import timedelta as td

verbose = False

# Query to get recent average temp
TEMPQRY = 'select mean(Water_Temp) from vivarium where time > now() - 5m'
TEMPNOW = 'select Water_Temp from vivarium order by time desc limit 1'

# Stepper sequencing
HALFSTEP = [
    [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], 
    [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]
]

# Order here is relay 1 to 4
device_pins = {
    'lamp': 26,
    'heatpad_backwall': 19,
    'heatpad_underlog': 13,
    'mains_relay4': 6,
    'led_lights': 12,
    'fountain': 16,
    'lowvolt_relay3': 20,
    'lowvolt_relay4': 21,
    #'stepper': [18, 23, 24, 25]
}
device_status = {
    'lamp': 0,
    'heatpad_backwall': 0,
    'heatpad_underlog': 0,
    'mains_relay4': 0,
    'led_lights': 0,
    'fountain': 0,
    'lowvolt_relay3': 0,
    'lowvolt_relay4': 0
}  # 1 on 0 off


def set_timer_devices(settings):
    for period in settings:
        s = settings[period]
        status = inPeriod(dt.now(), s['on'])
        for d in s['devices']:
            set_relay(d, status)


def set_thermo_devices(settings):
    for devblock in settings:
        s = settings[devblock]
        status = getHeaterStatus(s['target'])
        for d in s['devices']:
            set_relay(d, status)


def inPeriod(t, time_tuple):
    """ Determine whether t is inside or outside of a time period tuple.
    e.g. (8,22) would return false for 07:59, true for 08:00, true for
    21:59 and false for 22:00.

    Works for overnight (across midnight time reset) if the second entry 
    is smaller than the first

    Arguments:
        t (datetime) - The time to evaluate the time tuple at
        time_tuple (2-tuple, ints) - Block of time left-inclusive

    Returns:
        bool - True if we are inside the time period
               False otherwise
    """

    t1, t2 = time_tuple

    if t1 < t2:
        result = ((t.hour >= t1) and (t.hour < t2))
    else:
        result = ((t.hour >= t1) or (t.hour < t2))
    return result


def getHeaterStatus(target):
    """ Thermostat function. Queries temperature using Influx client, and compares to target.
    Seeing as the target temp lags heatpad, we want to enable immediately depending on target.

    Arugments: 
        target (float) - Target temp in celsius

    Returns:
        bool - True if actual temperature is below target. False otherwise.
               If the temperature can't be determined, return True.
    """

    # Use five minute average as best temp
    try:
        result1 = InfluxHandler.read(TEMPNOW)
        temp_now = list(result1.get_points())[0]['Water_Temp']
    except Exception as err:
        # Get the current temperature instead of 5 minute average
        temp_now = PullReading.GetReading(6)
        print(str(time.ctime()) + "    Unable to retrieve temperature for thermostat.")
        print(str(time.ctime()) + "    " + str(err))
        print(str(time.ctime()) + "    Using sensor reading of " + str(temp_now) + " degC")

    retval = temp_now <= target
    return retval


def set_relay(device, status):
    """ Set a given relay

    Arguments:
        device - Key in the relay dictionary in device_pins
        status - True for relay closed, false for relay open

    Returns:
        bool - False if there was an error accessing the DB, true otherwise
    """
    global device_status
    write_error = False

    if status != device_status[device]:
        if status:
            GPIO.output(device_pins[device], GPIO.LOW)
            print(str(time.ctime()) + '        {} ON           '.format(device))
        else:
            GPIO.output(device_pins[device], GPIO.HIGH)
            print(str(time.ctime()) + '        {} OFF          '.format(device))
        device_status[device] = status
        time.sleep(1)
    write_error = influxlog('{}_status'.format(device), status)
    return not write_error


def influxlog(measurementstr, state):
    """Add it into InfluxDB"""
    json_body = [{"measurement": "vivarium", "fields": {measurementstr: bool(state)}}]
    try:
        InfluxHandler.write(json_body)
        return True
    except:
        return False


def init_relays():
    # Set up General Purpose IO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialise relays
    print(str(time.ctime()) + '    Initialising all outputs to off...')
    for key in device_pins:
        if isinstance(device_pins[key], list):
            for pin in device_pins[key]:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, 0)
            influxlog('{}_status'.format(key), False)
        else:
            GPIO.setup(device_pins[key], GPIO.OUT)
            GPIO.output(device_pins[key], GPIO.HIGH)
            influxlog('{}_status'.format(key), False)


def main(args):
    init_relays()

    try:
        # Primary loop
        while 1:
            curdt = dt.now()

            # Set all main relays
            set_relay('lamp', getLightStatus(curdt))
            set_relay('heatpad_backwall', getHeaterStatus())
            set_relay('heatpad_underlog', getHeaterStatus())

            time.sleep(30)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
