#!/usr/bin/env python3
"""
Reptile Vivarium Monitoring System - Main Entry Point
This script initializes and starts the vivarium monitoring and control system.
"""

import os
import sys
import signal
import logging
import argparse
from pathlib import Path

# Add parent directory to path so we can import mobius package
sys.path.append(str(Path(__file__).parent.parent))

from mobius.core.controller import VivController
from mobius.config import settings


def setup_logging(log_level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
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
        logger.error(f"Error in main execution: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 