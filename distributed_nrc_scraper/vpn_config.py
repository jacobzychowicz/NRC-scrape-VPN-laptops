"""
VPN Configuration for NRC Scraper

This file contains configuration examples for different VPN clients.
Uncomment and modify the appropriate section for your VPN client.
"""

import subprocess
import time
import logging
import os

logger = logging.getLogger(__name__)

class VPNManager:
    """Base class for VPN management"""
    
    def __init__(self, locations: list):
        self.locations = locations
        self.current_location = None
    
    def connect(self, location: str) -> bool:
        """Connect to a specific location"""
        raise NotImplementedError("Subclass must implement connect method")
    
    def disconnect(self) -> bool:
        """Disconnect from VPN"""
        raise NotImplementedError("Subclass must implement disconnect method")
    
    def get_status(self) -> str:
        """Get current VPN status"""
        raise NotImplementedError("Subclass must implement get_status method")

class ProtonVPNManager(VPNManager):
    """ProtonVPN client manager"""
    
    def __init__(self, locations: list, email: str = None, password: str = None):
        super().__init__(locations)
        self.email = email
        self.password = password
        self.is_logged_in = False
    
    def _login(self) -> bool:
        """Login to ProtonVPN"""
        if self.is_logged_in:
            return True
            
        try:
            if not self.email or not self.password:
                logger.error("ProtonVPN credentials not provided")
                return False
            
            logger.info("Logging into ProtonVPN...")
            
            # Login to ProtonVPN
            login_cmd = f'protonvpn-cli login --username {self.email}'
            result = subprocess.run(login_cmd.split(), 
                                  input=f"{self.password}\n", 
                                  text=True, 
                                  capture_output=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                self.is_logged_in = True
                logger.info("Successfully logged into ProtonVPN")
                return True
            else:
                logger.error(f"Failed to login to ProtonVPN: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout logging into ProtonVPN")
            return False
        except Exception as e:
            logger.error(f"Error logging into ProtonVPN: {e}")
            return False
    
    def connect(self, location: str) -> bool:
        try:
            # Login first if not already logged in
            if not self._login():
                return False
            
            logger.info(f"Connecting to ProtonVPN location: {location}")
            
            # Connect to specific location
            connect_cmd = f'protonvpn-cli connect --cc {location}'
            result = subprocess.run(connect_cmd.split(), 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.current_location = location
                logger.info(f"Successfully connected to {location}")
                time.sleep(5)  # Wait for connection to stabilize
                return True
            else:
                logger.error(f"Failed to connect to {location}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout connecting to {location}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to {location}: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            logger.info("Disconnecting from ProtonVPN")
            result = subprocess.run(['protonvpn-cli', 'disconnect'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.current_location = None
                logger.info("Successfully disconnected from ProtonVPN")
                return True
            else:
                logger.error(f"Failed to disconnect: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False
    
    def get_status(self) -> str:
        try:
            result = subprocess.run(['protonvpn-cli', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "Unknown"

class NordVPNManager(VPNManager):
    """NordVPN client manager"""
    
    def connect(self, location: str) -> bool:
        try:
            logger.info(f"Connecting to NordVPN location: {location}")
            result = subprocess.run(['nordvpn', 'connect', location], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.current_location = location
                logger.info(f"Successfully connected to {location}")
                time.sleep(3)  # Wait for connection to stabilize
                return True
            else:
                logger.error(f"Failed to connect to {location}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout connecting to {location}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to {location}: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            logger.info("Disconnecting from NordVPN")
            result = subprocess.run(['nordvpn', 'disconnect'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.current_location = None
                logger.info("Successfully disconnected from NordVPN")
                return True
            else:
                logger.error(f"Failed to disconnect: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False
    
    def get_status(self) -> str:
        try:
            result = subprocess.run(['nordvpn', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "Unknown"

class ExpressVPNManager(VPNManager):
    """ExpressVPN client manager"""
    
    def connect(self, location: str) -> bool:
        try:
            logger.info(f"Connecting to ExpressVPN location: {location}")
            result = subprocess.run(['expressvpn', 'connect', location], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.current_location = location
                logger.info(f"Successfully connected to {location}")
                time.sleep(3)  # Wait for connection to stabilize
                return True
            else:
                logger.error(f"Failed to connect to {location}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout connecting to {location}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to {location}: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            logger.info("Disconnecting from ExpressVPN")
            result = subprocess.run(['expressvpn', 'disconnect'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.current_location = None
                logger.info("Successfully disconnected from ExpressVPN")
                return True
            else:
                logger.error(f"Failed to disconnect: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return False
    
    def get_status(self) -> str:
        try:
            result = subprocess.run(['expressvpn', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "Unknown"

class ManualVPNManager(VPNManager):
    """Manual VPN manager (for VPNs without CLI)"""
    
    def connect(self, location: str) -> bool:
        logger.info(f"MANUAL VPN SWITCH REQUIRED: Please connect to {location}")
        logger.info("Waiting 10 seconds for manual connection...")
        time.sleep(10)
        self.current_location = location
        return True
    
    def disconnect(self) -> bool:
        logger.info("MANUAL VPN DISCONNECT REQUIRED")
        self.current_location = None
        return True
    
    def get_status(self) -> str:
        return f"Manual VPN - Current: {self.current_location}"

# Example usage:
# vpn_manager = NordVPNManager(['Canada', 'United States', 'United Kingdom'])
# vpn_manager = ExpressVPNManager(['Canada', 'United States', 'United Kingdom'])
# vpn_manager = ManualVPNManager(['Canada', 'United States', 'United Kingdom'])
# vpn_manager = ProtonVPNManager(['CA', 'US', 'GB'], 'your-email@proton.me', 'your-password') 