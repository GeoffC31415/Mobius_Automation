from __future__ import print_function
import time
import RelayProgram
import InFluxLogger
from datetime import datetime as dt
from datetime import timedelta as td


def main(args):
		
	logging_pause = 10
	relay_pause = 30
	last_log = dt(2019,1,1)
	last_relay = dt(2019,1,1)
	
	RelayProgram.init_relays()

	while True:
		if dt.now() > (last_relay + td(seconds=relay_pause)):
			# Set all main relays
			write_error = False
			write_error = RelayProgram.set_relay("lamp", RelayProgram.getLightStatus(dt.now()))
			write_error |= RelayProgram.set_relay("heatpad_backwall", RelayProgram.getHeaterStatus())
			write_error |= RelayProgram.set_relay("heatpad_underlog", RelayProgram.getHeaterStatus())
			last_relay = dt.now()
			
		if dt.now() > (last_log + td(seconds=logging_pause)):
			readings = InFluxLogger.form_reading_set()
			InFluxLogger.write_points(readings)
			last_log = dt.now()
			
		time.sleep(1)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
