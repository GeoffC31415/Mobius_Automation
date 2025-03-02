"""
Relay Manager Module
Handles all relay hardware interactions for controlling devices
"""

import time
import logging
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

from mobius.config import settings
from mobius.services.influx_client import InfluxClient


class RelayManager:
    """Manages all relay interactions for the vivarium"""
    
    def __init__(self):
        """Initialize the relay manager"""
        self.logger = logging.getLogger('mobius.hardware.relay')
        self.influx_client = InfluxClient()
        
        # Initialize device status dictionary
        self.device_status = {device: False for device in settings.DEVICE_PINS}
        
        # Initialize GPIO if available
        if GPIO_AVAILABLE:
            self._setup_gpio()
        else:
            self.logger.warning("GPIO module not available - running in simulation mode")
            
    def _setup_gpio(self):
        """Set up GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialize all relay pins to OFF state
            self.logger.info("Initializing all relays to OFF state")
            for device, pin in settings.DEVICE_PINS.items():
                if isinstance(pin, list):
                    # Handle multi-pin devices (like steppers)
                    for p in pin:
                        GPIO.setup(p, GPIO.OUT)
                        GPIO.output(p, GPIO.LOW)
                else:
                    # Normal relay (HIGH = OFF for most relay modules)
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.HIGH)
                
                # Log initial state
                self._log_device_state(device, False)
        except Exception as e:
            self.logger.error(f"Error setting up GPIO: {e}", exc_info=True)
            raise
            
    def update_time_devices(self, time_settings):
        """Update all time-based devices
        
        Args:
            time_settings: Dictionary of time settings from settings.py
        """
        current_time = datetime.now()
        
        for period, config in time_settings.items():
            # Determine if current time is within the ON period
            should_be_on = self._in_time_period(current_time, config['on'])
            
            # Set each device for this time period
            for device in config['devices']:
                self.set_device(device, should_be_on)
                
    def update_thermo_devices(self, thermo_settings, current_temp):
        """Update all temperature-based devices
        
        Args:
            thermo_settings: Dictionary of temperature settings from settings.py
            current_temp: Current temperature reading
        """
        for zone, config in thermo_settings.items():
            # Determine if temperature is below target (needs heating)
            should_be_on = current_temp <= config['target']
            
            # Set each device for this temperature zone
            for device in config['devices']:
                self.set_device(device, should_be_on)
                
    def set_device(self, device, state):
        """Set a device to a specific state
        
        Args:
            device: Device name (must be in DEVICE_PINS)
            state: Boolean, True for ON, False for OFF
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if device exists
        if device not in settings.DEVICE_PINS:
            self.logger.error(f"Device {device} not found in settings")
            return False
            
        # Skip if no change needed
        if self.device_status.get(device) == state:
            return True
            
        # Update physical relay if GPIO available
        if GPIO_AVAILABLE:
            try:
                pin = settings.DEVICE_PINS[device]
                
                # Set pin state (typically, relays are active LOW)
                GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)
                
                # Log to console
                action = "ON" if state else "OFF"
                self.logger.info(f"Setting {device} {action}")
                
                # Small delay to prevent rapid relay switching
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error setting relay for {device}: {e}")
                return False
        else:
            # Simulation mode
            action = "ON" if state else "OFF"
            self.logger.info(f"[SIMULATION] Setting {device} {action}")
        
        # Update status and log to InfluxDB
        self.device_status[device] = state
        self._log_device_state(device, state)
        
        return True
        
    def _log_device_state(self, device, state):
        """Log device state to InfluxDB
        
        Args:
            device: Device name
            state: Boolean state
        """
        self.influx_client.log_device_state(device, state)
        
    def _in_time_period(self, current_time, time_period):
        """Check if current time is within the specified time period
        
        Args:
            current_time: datetime object
            time_period: Tuple of (start_hour, end_hour)
            
        Returns:
            bool: True if within time period, False otherwise
        """
        start_hour, end_hour = time_period
        
        if start_hour < end_hour:
            # Normal time period (e.g., 8 AM to 8 PM)
            return start_hour <= current_time.hour < end_hour
        else:
            # Overnight time period (e.g., 8 PM to 8 AM)
            return current_time.hour >= start_hour or current_time.hour < end_hour
            
    def cleanup(self):
        """Clean up GPIO resources"""
        if GPIO_AVAILABLE:
            try:
                # Turn off all relays before cleanup
                for device in settings.DEVICE_PINS:
                    self.set_device(device, False)
                    
                # Clean up GPIO
                GPIO.cleanup()
                self.logger.info("GPIO cleanup complete")
            except Exception as e:
                self.logger.error(f"Error during GPIO cleanup: {e}")
        else:
            self.logger.info("Simulation mode - no GPIO cleanup needed") 