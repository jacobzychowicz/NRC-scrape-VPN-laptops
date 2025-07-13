#!/usr/bin/env python3
"""
Runner script for Distributed NRC Scraper using configuration file
This script uses distributed_config.py for all settings.
"""

import os
import sys
import time
import logging
from distributed_nrc_scraper import DistributedNRCScraper
from distributed_config import get_config

def setup_logging(log_level):
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'nrc_scraper_{get_config()["laptop_id"]}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function"""
    try:
        # Load configuration
        config = get_config()
        
        # Setup logging
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)
        
        # Display configuration
        logger.info("=" * 60)
        logger.info("DISTRIBUTED NRC SCRAPER STARTING")
        logger.info("=" * 60)
        logger.info(f"Laptop ID: {config['laptop_id']}")
        logger.info(f"Output Directory: {config['output_dir']}")
        logger.info(f"Coordination File: {config['coordination_file']}")
        logger.info(f"VPN Type: {config['vpn_type']}")
        logger.info(f"Sync Interval: {config['sync_interval']} seconds")
        logger.info(f"Base URL: {config['base_url']}")
        logger.info(f"Max Depth: {config['max_depth']}")
        logger.info("-" * 60)
        
        # Check if coordination file directory exists
        coord_dir = os.path.dirname(config['coordination_file'])
        if coord_dir and not os.path.exists(coord_dir):
            logger.warning(f"Coordination file directory does not exist: {coord_dir}")
            logger.info("Creating directory...")
            os.makedirs(coord_dir, exist_ok=True)
        
        # Create scraper
        scraper = DistributedNRCScraper(
            base_url=config['base_url'],
            output_dir=config['output_dir'],
            coordination_file=config['coordination_file'],
            laptop_id=config['laptop_id'],
            vpn_locations=config['vpn_locations'],
            vpn_type=config['vpn_type'],
            vpn_email=config['vpn_email'],
            vpn_password=config['vpn_password'],
            sync_interval=config['sync_interval']
        )
        
        # Start scraping
        logger.info("Starting scraping process...")
        scraper.scrape_site()
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        if 'scraper' in locals():
            scraper.save_progress()
            scraper.save_coordination()
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        if 'scraper' in locals():
            scraper.save_progress()
            scraper.save_coordination()
        sys.exit(1)

if __name__ == "__main__":
    main() 