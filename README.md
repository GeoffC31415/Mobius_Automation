# Mobius_Automation

## Summary

This repo contains all the main monitoring and logging code. It's structured according to the following hierarchy:

1. Monitor.py

This file is the main loop which governs the readings, relays and logging of data. It imports InFluxLogger as the main sensor capture code, and RelayProgram as the codebase which controls the relays and automated control settings. Designed to be run from a terminal window.

You can set main loop timings here, but little else.

2. InFluxLogger.py

This file contains the high level functions for capturing a set of sensor readings. It imports PullReading.py for the specific handling and scaling of inputs of the various sensors, and combines them all together into a single json object for writing to InfluxDB. It also imports InfluxHandler for the connection and read/write requests to Influx itself. Designed to be imported, but can also run independently from a terminal for logging only.

You can set error filters here for the sensors (humidity must be <100% for example).

3. RelayProgram.py

This file contains the functions for determining timings for lighting, thermostat settings, and the lower level functions for setting individual devices. It also imports InfluxHandler for reading capture from the database, and also writing the states of the devices on change. Note - this no longer controls the Pi Camera which instead is handled by a seperate service not in the repo, for snapshots and motion capture. Designed to be imported, but can also run independently from a terminal for device control only. Note - this will quickly result in heaters being fixed as on, if the database isn't updated too.

You can set target tempss for heaters, timing for lights, and also pin mappings here.

4. InfluxHandler.py

This file contains simple wrapper functions for DB handling. Note - this database is not publically available and can only be accessed behind the NAT.

You can set the DB connection details here, except password handling.

5. TakePicture.py

This is a simple test script for manual photo taking. Simply dumps a photo to Pi desktop when run from terminal.
