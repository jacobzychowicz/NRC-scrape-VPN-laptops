#!/usr/bin/env python3
"""
Test script for Distributed NRC Scraper setup
This script verifies that all components are working correctly.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests module imported successfully")
    except ImportError:
        print("✗ requests module not found. Install with: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 module imported successfully")
    except ImportError:
        print("✗ beautifulsoup4 module not found. Install with: pip install beautifulsoup4")
        return False
    
    try:
        from distributed_nrc_scraper import DistributedNRCScraper
        print("✓ DistributedNRCScraper imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DistributedNRCScraper: {e}")
        return False
    
    try:
        from vpn_config import ManualVPNManager
        print("✓ VPN config imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import VPN config: {e}")
        return False
    
    return True

def test_config_file():
    """Test configuration file"""
    print("\nTesting configuration file...")
    
    if not os.path.exists('distributed_config.py'):
        print("✗ distributed_config.py not found")
        print("  Run setup_distributed_scraper.py to create it")
        return False
    
    try:
        from distributed_config import get_config
        config = get_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  Laptop ID: {config['laptop_id']}")
        print(f"  Output Dir: {config['output_dir']}")
        print(f"  Coordination File: {config['coordination_file']}")
        print(f"  VPN Type: {config['vpn_type']}")
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_coordination_file():
    """Test coordination file access"""
    print("\nTesting coordination file...")
    
    try:
        from distributed_config import get_config
        config = get_config()
        coord_file = config['coordination_file']
        
        # Test if we can read/write to the coordination file
        test_data = {
            'test': True,
            'timestamp': time.time(),
            'laptop_id': config['laptop_id']
        }
        
        # Write test data
        with open(coord_file, 'w') as f:
            json.dump(test_data, f)
        print(f"✓ Successfully wrote to coordination file: {coord_file}")
        
        # Read test data
        with open(coord_file, 'r') as f:
            read_data = json.load(f)
        
        if read_data['test'] and read_data['laptop_id'] == config['laptop_id']:
            print("✓ Successfully read from coordination file")
            
            # Clean up test data
            if os.path.exists(coord_file):
                os.remove(coord_file)
            print("✓ Cleaned up test coordination file")
            return True
        else:
            print("✗ Coordination file data mismatch")
            return False
            
    except Exception as e:
        print(f"✗ Coordination file test failed: {e}")
        return False

def test_vpn_manager():
    """Test VPN manager"""
    print("\nTesting VPN manager...")
    
    try:
        from distributed_config import get_config
        config = get_config()
        
        from vpn_config import ManualVPNManager
        vpn_manager = ManualVPNManager(config['vpn_locations'])
        
        print(f"✓ VPN manager created successfully")
        print(f"  Type: {config['vpn_type']}")
        print(f"  Locations: {config['vpn_locations']}")
        
        # Test getting next location
        next_location = vpn_manager.get_next_location()
        if next_location:
            print(f"  Next location: {next_location}")
        
        return True
    except Exception as e:
        print(f"✗ VPN manager test failed: {e}")
        return False

def test_scraper_creation():
    """Test scraper creation"""
    print("\nTesting scraper creation...")
    
    try:
        from distributed_config import get_config
        config = get_config()
        
        # Create a test scraper with minimal settings
        scraper = DistributedNRCScraper(
            base_url="https://nrc.canada.ca",
            output_dir="test_output",
            coordination_file="test_coordination.json",
            laptop_id="test_laptop",
            vpn_locations=['Canada'],
            vpn_type="manual",
            sync_interval=5
        )
        
        print("✓ Scraper created successfully")
        
        # Clean up test files
        if os.path.exists("test_output"):
            import shutil
            shutil.rmtree("test_output")
        if os.path.exists("test_coordination.json"):
            os.remove("test_coordination.json")
        
        print("✓ Cleaned up test files")
        return True
        
    except Exception as e:
        print(f"✗ Scraper creation test failed: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity"""
    print("\nTesting network connectivity...")
    
    try:
        import requests
        
        # Test basic connectivity
        response = requests.get("https://www.google.com", timeout=10)
        if response.status_code == 200:
            print("✓ Basic internet connectivity working")
        else:
            print("✗ Basic internet connectivity failed")
            return False
        
        # Test NRC website access
        response = requests.get("https://nrc.canada.ca", timeout=10)
        if response.status_code == 200:
            print("✓ NRC website accessible")
        else:
            print(f"⚠ NRC website returned status {response.status_code}")
            print("  This might be expected if VPN is required")
        
        return True
        
    except Exception as e:
        print(f"✗ Network connectivity test failed: {e}")
        return False

def test_file_permissions():
    """Test file permissions"""
    print("\nTesting file permissions...")
    
    try:
        from distributed_config import get_config
        config = get_config()
        
        # Test output directory creation
        test_dir = "test_permissions"
        os.makedirs(test_dir, exist_ok=True)
        
        # Test file creation
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Test file reading
        with open(test_file, 'r') as f:
            content = f.read()
        
        if content == "test":
            print("✓ File read/write permissions working")
        else:
            print("✗ File read/write test failed")
            return False
        
        # Clean up
        os.remove(test_file)
        os.rmdir(test_dir)
        print("✓ Cleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"✗ File permissions test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("DISTRIBUTED NRC SCRAPER SETUP TEST")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config_file),
        ("Coordination File Test", test_coordination_file),
        ("VPN Manager Test", test_vpn_manager),
        ("Scraper Creation Test", test_scraper_creation),
        ("Network Connectivity Test", test_network_connectivity),
        ("File Permissions Test", test_file_permissions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"  Test failed")
        except Exception as e:
            print(f"  Test error: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Your distributed scraper is ready to use.")
        print("\nNext steps:")
        print("1. Configure the other laptop(s) with different laptop IDs")
        print("2. Set up the coordination file sharing method")
        print("3. Start scraping on all laptops")
    else:
        print("⚠ Some tests failed. Please fix the issues before running the scraper.")
        print("\nCommon fixes:")
        print("- Run setup_distributed_scraper.py to create configuration")
        print("- Install missing Python packages: pip install requests beautifulsoup4")
        print("- Check file permissions and network access")
        print("- Verify VPN configuration if using automatic VPN")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 