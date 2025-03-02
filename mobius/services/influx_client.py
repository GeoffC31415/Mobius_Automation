"""
InfluxDB Client Module
Handles all interactions with InfluxDB for data logging
"""

import json
import logging
import os
from typing import Dict, List, Any, Union

try:
    from influxdb import InfluxDBClient
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False


class InfluxClient:
    """Client for interacting with InfluxDB"""
    
    def __init__(self):
        """Initialize the InfluxDB client"""
        self.logger = logging.getLogger('mobius.services.influx')
        
        self.measurement = "vivarium"
        self.run_id = "v1"
        
        # Set up InfluxDB connection
        self.credentials = self._get_credentials()
        
        if not INFLUX_AVAILABLE:
            self.logger.warning("InfluxDB package not available - data will not be logged")
            
    def _get_credentials(self) -> Dict[str, Any]:
        """Get InfluxDB credentials from secrets file
        
        Returns:
            dict: InfluxDB connection parameters
        """
        try:
            # Try to load secret file
            secret_path = '/home/pi/Documents/Mobius/secret.txt'
            if os.path.exists(secret_path):
                with open(secret_path) as s:
                    secrets = json.load(s)
                return secrets.get('InfluxAccount', {})
            else:
                # Use environment variables if available
                return {
                    'host': os.environ.get('INFLUX_HOST', 'localhost'),
                    'port': int(os.environ.get('INFLUX_PORT', 8086)),
                    'username': os.environ.get('INFLUX_USER', ''),
                    'password': os.environ.get('INFLUX_PASS', ''),
                    'database': os.environ.get('INFLUX_DB', 'vivarium')
                }
        except Exception as e:
            self.logger.error(f"Error loading InfluxDB credentials: {e}", exc_info=True)
            return {
                'host': 'localhost',
                'port': 8086,
                'database': 'vivarium'
            }
            
    def write_sensor_data(self, data: Dict[str, float]) -> bool:
        """Write sensor readings to InfluxDB
        
        Args:
            data: Dictionary of sensor readings
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not data:
            self.logger.warning("No data to write to InfluxDB")
            return False
            
        # Format as InfluxDB json structure
        json_body = [{
            "measurement": self.measurement,
            "tags": {
                "run": self.run_id
            },
            "fields": data
        }]
        
        return self.write_points(json_body)
        
    def log_device_state(self, device: str, state: bool) -> bool:
        """Log device state to InfluxDB
        
        Args:
            device: Device name
            state: Boolean state
            
        Returns:
            bool: True if successful, False otherwise
        """
        json_body = [{
            "measurement": self.measurement,
            "tags": {
                "run": self.run_id
            },
            "fields": {
                f"{device}_status": bool(state)
            }
        }]
        
        return self.write_points(json_body)
        
    def log_file_size(self, size: float) -> bool:
        """Log file size to InfluxDB
        
        Args:
            size: File size in bytes
            
        Returns:
            bool: True if successful, False otherwise
        """
        json_body = [{
            "measurement": self.measurement,
            "tags": {
                "run": self.run_id
            },
            "fields": {
                "videosize": float(size)
            }
        }]
        
        return self.write_points(json_body)
        
    def write_points(self, json_body: List[Dict[str, Any]]) -> bool:
        """Write data points to InfluxDB
        
        Args:
            json_body: InfluxDB formatted json data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not INFLUX_AVAILABLE:
            self.logger.debug("InfluxDB not available, skipping write")
            return False
            
        try:
            client = InfluxDBClient(**self.credentials)
            client.write_points(json_body)
            client.close()
            self.logger.debug("Data written to InfluxDB successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error writing to InfluxDB: {e}")
            return False
            
    def read_query(self, query: str) -> Any:
        """Execute a query against InfluxDB
        
        Args:
            query: InfluxQL query string
            
        Returns:
            ResultSet: Query results
        """
        if not INFLUX_AVAILABLE:
            self.logger.error("InfluxDB not available, cannot execute query")
            return None
            
        try:
            client = InfluxDBClient(**self.credentials)
            results = client.query(query)
            client.close()
            return results
        except Exception as e:
            self.logger.error(f"Error querying InfluxDB: {e}")
            return None 