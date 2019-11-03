from __future__ import print_function
import time
import RelayProgram
import InFluxLogger
from datetime import datetime as dt
from datetime import timedelta as td

TIME_SETTINGS = {
	'daylight': {
		'on': (8,22),
		'devices': ['lamp', 'led_lights']
	},
	'rains': {
		'on': (18,24),
		'devices': ['fountain']
	}
}
THERMO_SETTINGS = {
	'main': {
		'target': 31,
		'devices': ['heatpad_backwall','heatpad_underlog']
	}
}

def main(args):
		
	logging_pause = 10
	relay_pause = 30
	last_log = dt(2019,1,1)
	last_relay = dt(2019,1,1)
	
	RelayProgram.init_relays()

	while True:
		if dt.now() > (last_relay + td(seconds=relay_pause)):
			RelayProgram.set_timer_devices(TIME_SETTINGS)
			RelayProgram.set_thermo_devices(THERMO_SETTINGS)
			last_relay = dt.now()
			
		if dt.now() > (last_log + td(seconds=logging_pause)):
			InFluxLogger.write_points(InFluxLogger.form_reading_set())
			last_log = dt.now()
			
		time.sleep(1)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
