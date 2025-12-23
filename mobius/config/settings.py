"""
Settings Configuration
Centralized configuration for the vivarium monitoring system
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = os.environ.get('MOBIUS_DATA_DIR', '/var/www/html/Mobius_Website/images/')

# System timing intervals (seconds)
SENSOR_READ_INTERVAL = 10       	# How often to read and log sensor data
RELAY_CHECK_INTERVAL = 30       	# How often to update relay states
FILE_MAINTENANCE_INTERVAL = 3600  	# How often to perform file maintenance (1 hour)

# Time-based device settings
# Format: {condition_name: {'on': (start_hour, end_hour), 'devices': [device_names]}}
TIME_SETTINGS = {
    'daylight': {
        'on': (6, 19),          	# 6 AM to 7 PM
        'devices': ['lamp']
    }
}

# Temperature-based device settings
# Format: {zone_name: {'target': target_temp, 'devices': [device_names]}}
THERMO_SETTINGS = {
    'main': {
        'target': 32,           # Target temperature in Celsius
        'devices': ['ceramic_heat_lamp']
    },
    'backup': {
		'target': 34,
		'on': (10, 19),
		'devices': ['basking_lamp']
    }
}

# GPIO pin mappings for devices
DEVICE_PINS = {
    'relay1_in1': 26,  			# First relay, IN1
    'ceramic_heat_lamp': 19,  	# Black zero-light, linked to relay IN2
    'lamp': 13,  				# Original ligh-only lamp - linked to relay IN3
    'basking_lamp': 6,  		# Bright 100W basking lamp, IN4
    'relay2_in1': 12,  			# Second relay, IN1
    'relay2_in2': 16,  			# Second relay, IN2
    'relay2_in3': 20,  			# Second relay, IN3
    'relay2_in4': 21,  			# Second relay, IN4
}

# DHT sensor configuration
DHT_PINS = []      				# GPIO pins for DHT sensors
DHT_JITTER = 0.08               # Amount of jitter to add to DHT readings

# One-wire temperature sensor configuration
ONEWIRE_BASE_DIR = '/sys/bus/w1/devices/'
ONEWIRE_DEVICE_PREFIX = '28*'
ONEWIRE_FALLBACK = 20.0  		# If one wire fails, use this for temp and randomise relay settings

# Video file management
VIDEO_MAX_AGE_DAYS = 14         # Maximum age for video files
VIDEO_CLEAN_MIN_HOUR = 6        # Start hour for daytime videos to clean
VIDEO_CLEAN_MAX_HOUR = 20       # End hour for daytime videos to clean
VIDEO_CLEAN_MAX_SIZE = 3e6      # Maximum size for videos to keep (bytes)

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 
