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
SENSOR_READ_INTERVAL = 10       # How often to read and log sensor data
RELAY_CHECK_INTERVAL = 30       # How often to update relay states
FILE_MAINTENANCE_INTERVAL = 3600  # How often to perform file maintenance (1 hour)

# Time-based device settings
# Format: {condition_name: {'on': (start_hour, end_hour), 'devices': [device_names]}}
TIME_SETTINGS = {
    'daylight': {
        'on': (6, 21),          # 6 AM to 9 PM
        'devices': ['led_lights']
    },
    'sunny': {
        'on': (8, 20),          # 8 AM to 8 PM
        'devices': ['lamp']
    },
    'rains': {
        'on': (1, 23),          # 1 AM to 11 PM
        'devices': ['fountain']
    }
}

# Temperature-based device settings
# Format: {zone_name: {'target': target_temp, 'devices': [device_names]}}
THERMO_SETTINGS = {
    'main': {
        'target': 34,           # Target temperature in Celsius
        'devices': ['heatpad_backwall', 'heatpad_underlog']
    }
}

# GPIO pin mappings for devices
DEVICE_PINS = {
    'lamp': 26,
    'heatpad_backwall': 19,
    'heatpad_underlog': 13,
    'mains_relay4': 6,
    'led_lights': 12,
    'fountain': 16,
    'lowvolt_relay3': 20,
    'lowvolt_relay4': 21,
}

# DHT sensor configuration
DHT_PINS = [4, 17, 27, 22]      # GPIO pins for DHT sensors
DHT_JITTER = 0.08               # Amount of jitter to add to DHT readings

# One-wire temperature sensor configuration
ONEWIRE_BASE_DIR = '/sys/bus/w1/devices/'
ONEWIRE_DEVICE_PREFIX = '28*'

# Video file management
VIDEO_MAX_AGE_DAYS = 14         # Maximum age for video files
VIDEO_CLEAN_MIN_HOUR = 6        # Start hour for daytime videos to clean
VIDEO_CLEAN_MAX_HOUR = 20       # End hour for daytime videos to clean
VIDEO_CLEAN_MAX_SIZE = 3e6      # Maximum size for videos to keep (bytes)

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 