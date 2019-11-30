import RelayProgram
import InFluxLogger
import FileHandler
import time

from datetime import datetime as dt
from datetime import timedelta as td

TIME_SETTINGS = {
	'daylight': {
		'on': (6,21),
		'devices': ['led_lights']
	},
	'sunny': {
		'on': (10,18),
		'devices': ['lamp']
	},
	'rains': {
		'on': (1,23),
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
	
	print(str(time.ctime()) + '========================')
	print(str(time.ctime()) + '    Monitor Starting')
	print(str(time.ctime()) + '========================')
		
	logging_pause = 10
	relay_pause = 30
	filetrim_pause = 3600
	
	last_log = dt(2019,1,1)
	last_relay = dt(2019,1,1)
	last_filetrim = dt(2019,1,1)
	
	RelayProgram.init_relays()

	while True:
		if dt.now() > (last_relay + td(seconds=relay_pause)):
			last_relay = dt.now()
			RelayProgram.set_timer_devices(TIME_SETTINGS)
			RelayProgram.set_thermo_devices(THERMO_SETTINGS)
			
		if dt.now() > (last_log + td(seconds=logging_pause)):
			last_log = dt.now()
			InFluxLogger.write_points(InFluxLogger.form_reading_set())
			
		if dt.now() > (last_filetrim + td(seconds=filetrim_pause)):
			last_filetrim = dt.now()
			
			startdate = dt.now() - td(days=1)
			enddate = dt.now()
			totalsize = FileHandler.get_total_size(startdate, enddate)
			InFluxLogger.log_filesize_json(totalsize)
			
			FileHandler.cleanVideos(minhr=6, maxhr=20, maxsize=3e6)
			
		time.sleep(0.1)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
