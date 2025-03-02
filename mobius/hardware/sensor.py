"""
Sensor Manager Module
Manages all sensors for the reptile vivarium
"""

import random
import logging
import subprocess
import glob
import os
import time
from typing import Dict, List, Tuple

try:
    import Adafruit_DHT
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False

from mobius.config import settings


class SensorManager:
    """Manager for all sensor interactions"""
    
    def __init__(self):
        """Initialize the sensor manager"""
        self.logger = logging.getLogger('mobius.hardware.sensor')
        
        # Initialize one-wire temperature sensor if available
        self._init_onewire()
        
        # Initialize DHT sensors
        self._init_dht()
        
    def _init_onewire(self):
        """Initialize one-wire temperature sensor interface"""
        try:
            if os.path.exists('/sys/bus/w1/devices/'):
                self.logger.info("One-wire interface already initialized")
            else:
                self.logger.info("Initializing one-wire interface")
                os.system('modprobe w1-gpio')
                os.system('modprobe w1-therm')
                
            # Find device folder
            device_folders = glob.glob(settings.ONEWIRE_BASE_DIR + settings.ONEWIRE_DEVICE_PREFIX)
            if device_folders:
                self.device_file = device_folders[0] + '/w1_slave'
                self.logger.info("Found one-wire device: {}".format(device_folders[0]))
                self.onewire_available = True
            else:
                self.logger.warning("No one-wire temperature sensors found")
                self.onewire_available = False
        except Exception as e:
            self.logger.error("Error initializing one-wire: {}".format(e))
            self.onewire_available = False
            
    def _init_dht(self):
        """Initialize DHT temperature/humidity sensors"""
        self.dht_available = DHT_AVAILABLE
        if not self.dht_available:
            self.logger.warning("Adafruit_DHT library not available - DHT sensors disabled")
            
    def get_temperature(self) -> float:
        """Get the current water temperature
        
        Returns:
            float: Temperature in Celsius
        """
        if self.onewire_available:
            try:
                return self._read_onewire_temp()
            except Exception as e:
                self.logger.error("Error reading water temperature: {}".format(e))
                
        # Return a reasonable default if sensor read fails
        self.logger.warning("Using simulated temperature value")
        return 25.0  # Default fallback
    
    def get_dht_reading(self, sensor_id: int) -> Tuple[float, float]:
        """Get humidity and temperature from a DHT sensor
        
        Args:
            sensor_id: The sensor ID (1-based index into DHT_PINS)
            
        Returns:
            tuple: (humidity, temperature) readings in % and Celsius
        """
        if not self.dht_available or sensor_id > len(settings.DHT_PINS):
            # Return simulated data if sensor not available
            self.logger.debug("Using simulated data for DHT sensor {sensor_id}".format(sensor_id=sensor_id))
            return (
                60.0 + random.normalvariate(0, 5),  # Simulated humidity around 60%
                25.0 + random.normalvariate(0, 2)   # Simulated temp around 25°C
            )
            
        # Get the GPIO pin for this sensor
        pin = settings.DHT_PINS[sensor_id - 1]
        
        try:
            # Read from sensor
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin)
            
            # Add jitter to readings to help visualize changes
            if humidity is not None:
                humidity += random.normalvariate(0, settings.DHT_JITTER)
            else:
                humidity = -1
                
            if temperature is not None:
                temperature += random.normalvariate(0, settings.DHT_JITTER)
            else:
                temperature = -1
                
            return (humidity, temperature)
            
        except Exception as e:
            self.logger.error("Error reading DHT sensor {sensor_id}: {e}".format(sensor_id=sensor_id, e=e))
            return (-1, -1)  # Error indicator
            
    def get_all_readings(self) -> Dict[str, float]:
        """Get readings from all sensors
        
        Returns:
            dict: Dictionary of sensor readings
        """
        readings = {}
        
        # Get water temperature
        water_temp = self.get_temperature()
        readings['Water_Temp'] = float(water_temp)
        
        # Get DHT readings (3 sensors with IDs 1, 2, 4)
        dht_sensors = [1, 2, 4]
        for sensor_id in dht_sensors:
            humidity, temperature = self.get_dht_reading(sensor_id)
            
            # Set sensor name based on ID
            humidity_key = "DHT{sensor_id}_Hum".format(sensor_id=sensor_id)
            temperature_key = "DHT{sensor_id}_Temp".format(sensor_id=sensor_id)
            
            # Filter out invalid readings
            if humidity >= 35 and humidity < 100:
                readings[humidity_key] = float(humidity)
                
            if temperature > 12:
                readings[temperature_key] = float(temperature)
                
        return readings
        
    def _read_onewire_temp(self) -> float:
        """Read temperature from one-wire temperature sensor
        
        Returns:
            float: Temperature in Celsius
        """
        if not self.onewire_available:
            return -1
            
        try:
            # Read raw data from sensor
            lines = self._read_temp_raw()
            
            # Wait for valid reading
            retries = 5
            while lines[0].strip()[-3:] != 'YES' and retries > 0:
                time.sleep(0.2)
                lines = self._read_temp_raw()
                retries -= 1
                
            # Parse temperature value
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
            else:
                return -1
        except Exception as e:
            self.logger.error("Error reading one-wire sensor: {}".format(e))
            return -1
            
    def _read_temp_raw(self) -> List[str]:
        """Read raw data from one-wire temperature sensor
        
        Returns:
            list: Lines of output from sensor
        """
        try:
            # Use subprocess to read the sensor file
            cat_process = subprocess.Popen(
                ['cat', self.device_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = cat_process.communicate()
            
            # Decode and split output
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            return lines
        except Exception as e:
            self.logger.error("Error reading raw temperature: {}".format(e))
            return ["", ""]
            
    def cleanup(self):
        """Clean up sensor resources"""
        # Nothing to clean up for current sensors
        pass 