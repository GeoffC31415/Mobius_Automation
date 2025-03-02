"""
Core Controller Module
The central control system that coordinates all vivarium functions
"""

import time
import logging
import threading
from datetime import datetime, timedelta

from mobius.config import settings
from mobius.hardware.relay import RelayManager
from mobius.hardware.sensor import SensorManager
from mobius.services.influx_client import InfluxClient
from mobius.services.file_manager import FileManager


class VivController:
    """Main controller for the reptile vivarium system"""

    def __init__(self):
        """Initialize the controller and its components"""
        self.logger = logging.getLogger('mobius.controller')
        self.logger.info("Initializing VivController")
        
        # Initialize components
        self.influx_client = InfluxClient()
        self.sensor_manager = SensorManager()
        self.relay_manager = RelayManager()
        self.file_manager = FileManager()
        
        # Timekeeping
        self.last_sensor_read = datetime.min
        self.last_relay_check = datetime.min
        self.last_file_maintenance = datetime.min
        
        # Flags
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the main control loop in a separate thread"""
        if self.running:
            self.logger.warning("Controller already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        # Block the main thread
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Stop the controller and clean up resources"""
        self.logger.info("Stopping controller")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        # Cleanup hardware
        self.relay_manager.cleanup()
        self.sensor_manager.cleanup()
        
    def _run_loop(self):
        """Main control loop"""
        self.logger.info("Starting main control loop")
        
        while self.running:
            current_time = datetime.now()
            
            # 1. Read sensors and log data
            if current_time >= (self.last_sensor_read + timedelta(seconds=settings.SENSOR_READ_INTERVAL)):
                self.last_sensor_read = current_time
                try:
                    self._process_sensors()
                except Exception as e:
                    self.logger.error("Error processing sensors: {}".format(e))
            
            # 2. Check and update relay states based on time and temperature
            if current_time >= (self.last_relay_check + timedelta(seconds=settings.RELAY_CHECK_INTERVAL)):
                self.last_relay_check = current_time
                try:
                    self._process_relays()
                except Exception as e:
                    self.logger.error("Error processing relays: {}".format(e))
            
            # 3. Perform file maintenance
            if current_time >= (self.last_file_maintenance + timedelta(seconds=settings.FILE_MAINTENANCE_INTERVAL)):
                self.last_file_maintenance = current_time
                try:
                    self._process_files()
                except Exception as e:
                    self.logger.error("Error processing files: {}".format(e))
            
            # Sleep a short time to prevent CPU thrashing
            time.sleep(0.1)
    
    def _process_sensors(self):
        """Read all sensors and log the data"""
        self.logger.debug("Reading sensors")
        
        # Get readings from all sensors
        readings = self.sensor_manager.get_all_readings()
        
        # Log to InfluxDB
        self.influx_client.write_sensor_data(readings)
        
    def _process_relays(self):
        """Update relay states based on time and temperature"""
        self.logger.debug("Updating relay states")
        
        # Get current temperature
        temp = self.sensor_manager.get_temperature()
        
        # Update time-based devices
        self.relay_manager.update_time_devices(settings.TIME_SETTINGS)
        
        # Update temperature-based devices
        self.relay_manager.update_thermo_devices(settings.THERMO_SETTINGS, temp)
        
    def _process_files(self):
        """Perform file maintenance"""
        self.logger.debug("Performing file maintenance")
        
        # Get file stats for the past day
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now()
        
        # Get total file size
        total_size = self.file_manager.get_total_size(start_date, end_date)
        
        # Log file size to InfluxDB
        self.influx_client.log_file_size(total_size)
        
        # Clean up old videos
        self.file_manager.clean_videos(
            min_hour=settings.VIDEO_CLEAN_MIN_HOUR,
            max_hour=settings.VIDEO_CLEAN_MAX_HOUR,
            max_size=settings.VIDEO_CLEAN_MAX_SIZE
        ) 