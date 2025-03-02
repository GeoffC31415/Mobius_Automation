"""
Secrets Management Module
Handles loading and managing sensitive configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('mobius.config.secrets')

# Default path to secrets file
DEFAULT_SECRETS_PATH = '/home/pi/Documents/Mobius/secret.txt'


def get_secrets(secrets_path: Optional[str] = None) -> Dict[str, Any]:
    """Load secrets from file or environment variables
    
    Args:
        secrets_path: Optional path to secrets file
        
    Returns:
        dict: Dictionary of secrets
    """
    secrets = {}
    
    # Try to load from file
    try:
        path = secrets_path or DEFAULT_SECRETS_PATH
        if os.path.exists(path):
            with open(path, 'r') as f:
                secrets = json.load(f)
            logger.info("Loaded secrets from {path}".format(path=path))
    except Exception as e:
        logger.warning("Could not load secrets from file: {}".format(e))
    
    # Use environment variables as fallback or override
    env_secrets = {
        'InfluxAccount': {
            'host': os.environ.get('INFLUX_HOST'),
            'port': os.environ.get('INFLUX_PORT'),
            'username': os.environ.get('INFLUX_USER'),
            'password': os.environ.get('INFLUX_PASS'),
            'database': os.environ.get('INFLUX_DB')
        }
    }
    
    # Clean up None values
    for category, values in env_secrets.items():
        cleaned = {k: v for k, v in values.items() if v is not None}
        if cleaned:
            if category in secrets:
                secrets[category].update(cleaned)
            else:
                secrets[category] = cleaned
    
    return secrets