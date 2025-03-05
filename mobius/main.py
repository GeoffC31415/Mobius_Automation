#!/usr/bin/env python3
"""
Reptile Vivarium Monitoring System - Main Entry Point
This script initializes and starts the vivarium monitoring and control system.
"""

import sys
import signal
import logging
import argparse
from pathlib import Path

# Add parent directory to path so we can import mobius package
sys.path.append(str(Path(__file__).parent.parent))

from mobius.core.controller import VivController


def setup_logging(log_level=logging.INFO):
    """Configure logging for the application"""
    # Basic configuration for console output
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add a rotating file handler with date-based filenames
    import os
    import datetime
    import glob
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.expanduser('~/mobius_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file with today's date in the filename
    today = datetime.datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, 'mobius_{}.log'.format(today))
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    
    # Set the formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    logging.getLogger().addHandler(file_handler)
    
    # Clean up old log files (keep only the latest 30 days)
    log_files = glob.glob(os.path.join(log_dir, 'mobius_*.log'))
    if len(log_files) > 30:
        # Sort files by modification time (oldest first)
        log_files.sort(key=os.path.getmtime)
        # Remove the oldest files, keeping only the latest 30
        for old_file in log_files[:-30]:
            try:
                os.remove(old_file)
                logging.debug("Removed old log file: {}".format(old_file))
            except Exception as e:
                logging.warning("Failed to remove old log file {}: {}".format(old_file, e))
    
    # Return the logger
    return logging.getLogger('mobius')


def signal_handler(sig, frame):
    """Handle system signals for graceful shutdown"""
    logger = logging.getLogger('mobius')
    logger.info("Signal received, shutting down...")
    sys.exit(0)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Reptile Vivarium Monitoring System')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', help='Path to custom config file')
    return parser.parse_args()


def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logging(log_level)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Reptile Vivarium Monitoring System")
    
    try:
        # Initialize and start the controller
        controller = VivController()
        controller.start()
    except Exception as e:
        logger.error("Error in main execution: {}".format(e))
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 