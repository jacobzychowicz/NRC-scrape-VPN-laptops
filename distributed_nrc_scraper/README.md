# Distributed NRC Scraper

A distributed web scraper for the National Research Council Canada (NRC) website that can run on multiple laptops simultaneously without downloading duplicate files.

## Features

- **Distributed Operation**: Run on multiple laptops simultaneously
- **No Duplicate Downloads**: Coordination system prevents downloading the same files
- **VPN Support**: Automatic VPN switching with multiple providers (ProtonVPN, NordVPN, ExpressVPN)
- **Progress Tracking**: Saves progress and can resume from where it left off
- **PDF Detection**: Automatically finds and downloads PDF files
- **Error Handling**: Graceful handling of network errors and VPN issues
- **Configurable**: Easy setup for different laptops and environments

## System Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux
- VPN client (optional, for bypassing restrictions)
- Network access to share coordination file

## Installation

1. **Download the scraper files** to each laptop
2. **Install Python dependencies**:
   ```bash
   pip install requests beautifulsoup4
   ```
3. **Install VPN client** (if using automatic VPN switching):
   - ProtonVPN CLI: `pip install protonvpn-cli`
   - NordVPN: Download from nordvpn.com
   - ExpressVPN: Download from expressvpn.com

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script on each laptop:

```bash
python setup_distributed_scraper.py
```

The script will guide you through:
- Setting a unique laptop ID
- Configuring VPN settings
- Setting up coordination file sharing
- Creating batch files for easy running

### Option 2: Manual Setup

1. **Copy files to each laptop**:
   - `distributed_nrc_scraper.py`
   - `vpn_config.py`
   - `run_distributed_scraper_config.py`
   - `distributed_config.py`

2. **Configure each laptop**:
   - Edit `distributed_config.py` on each laptop
   - Set unique `LAPTOP_ID` for each laptop
   - Configure `COORDINATION_FILE` path
   - Set VPN settings

## Configuration

### Laptop Configuration

Each laptop needs a unique configuration in `distributed_config.py`:

```python
# LAPTOP CONFIGURATION
LAPTOP_ID = "laptop1"  # Change to "laptop2" for second laptop
OUTPUT_DIR = "nrc_downloads_laptop1"  # Unique output directory

# COORDINATION SETUP
COORDINATION_FILE = "distributed_coordination.json"  # Shared file path
SYNC_INTERVAL = 30  # How often to sync (seconds)
```

### Coordination File Setup

The coordination file must be accessible by all laptops. Choose one option:

#### Option 1: Network Drive (Recommended)
```python
COORDINATION_FILE = "\\\\server\\share\\nrc_scraper\\distributed_coordination.json"
```

#### Option 2: Cloud Sync (Dropbox/OneDrive)
```python
COORDINATION_FILE = "C:\\Users\\Username\\Dropbox\\nrc_scraper\\distributed_coordination.json"
```

#### Option 3: USB Drive
```python
COORDINATION_FILE = "E:\\nrc_scraper\\distributed_coordination.json"
```

#### Option 4: Local File (Manual Sync)
```python
COORDINATION_FILE = "distributed_coordination.json"
# Manually copy this file between laptops
```

### VPN Configuration

#### Manual VPN (Default)
```python
VPN_TYPE = "manual"
VPN_LOCATIONS = ['Canada', 'United States', 'United Kingdom']
```

#### ProtonVPN
```python
VPN_TYPE = "protonvpn"
VPN_EMAIL = "your_email@example.com"
VPN_PASSWORD = "your_password"
VPN_LOCATIONS = ['CA', 'US', 'GB']  # Country codes
```

#### NordVPN
```python
VPN_TYPE = "nordvpn"
VPN_LOCATIONS = ['Canada', 'United States', 'United Kingdom']
```

## Usage

### Starting the Scraper

#### Option 1: Using the batch file (Windows)
Double-click: `run_scraper_laptop1.bat`

#### Option 2: Using Python directly
```bash
python run_distributed_scraper_config.py
```

#### Option 3: Using command line arguments
```bash
python distributed_nrc_scraper.py --laptop-id laptop1 --coordination-file distributed_coordination.json
```

### Running on Multiple Laptops

1. **Start the first laptop**:
   ```bash
   python run_distributed_scraper_config.py
   ```

2. **Start the second laptop** (with different laptop ID):
   ```bash
   python run_distributed_scraper_config.py
   ```

3. **Monitor progress**:
   - Check log files: `nrc_scraper_laptop1.log`, `nrc_scraper_laptop2.log`
   - Check coordination file: `distributed_coordination.json`
   - Check output directories: `nrc_downloads_laptop1/`, `nrc_downloads_laptop2/`

## File Structure

```
nrc_scraper/
├── distributed_nrc_scraper.py          # Main scraper code
├── vpn_config.py                       # VPN management
├── distributed_config.py               # Configuration file
├── run_distributed_scraper_config.py   # Runner script
├── setup_distributed_scraper.py        # Setup script
├── distributed_coordination.json       # Shared coordination file
├── nrc_downloads_laptop1/              # Output directory for laptop1
│   ├── scraper_progress_laptop1.json   # Progress tracking
│   └── [downloaded files]
├── nrc_downloads_laptop2/              # Output directory for laptop2
│   ├── scraper_progress_laptop2.json   # Progress tracking
│   └── [downloaded files]
├── nrc_scraper_laptop1.log             # Log file for laptop1
├── nrc_scraper_laptop2.log             # Log file for laptop2
└── run_scraper_laptop1.bat             # Batch file for laptop1
```

## How It Works

### Coordination System

1. **Shared State**: All laptops read/write to a shared coordination file
2. **URL Tracking**: Each laptop tracks visited URLs and downloaded files
3. **Duplicate Prevention**: Before downloading, check if another laptop already downloaded the file
4. **Progress Sync**: Regular synchronization of progress between laptops

### VPN Management

1. **Automatic Switching**: When encountering 403 errors, automatically switch VPN locations
2. **Multiple Providers**: Support for ProtonVPN, NordVPN, ExpressVPN, and manual VPN
3. **Error Recovery**: Retry failed requests with different VPN locations
4. **Status Monitoring**: Track VPN connection status

### File Download

1. **Smart Filtering**: Skip CSS, JS, images, and French content
2. **PDF Detection**: Multiple methods to find PDF links
3. **Duplicate Detection**: Check file content to avoid duplicates
4. **Hierarchical Structure**: Organize files in folder structure matching URL paths

## Troubleshooting

### Common Issues

#### VPN Connection Problems
- Check VPN client installation
- Verify credentials for ProtonVPN
- Ensure VPN locations are available

#### Coordination File Issues
- Check file path accessibility
- Ensure all laptops can read/write to the file
- Verify network drive mapping

#### Permission Errors
- Run as administrator (Windows)
- Check file/folder permissions
- Ensure output directory is writable

#### Network Errors
- Check internet connection
- Verify VPN connection
- Try different VPN locations

### Log Files

Check the log files for detailed error messages:
- `nrc_scraper_laptop1.log`
- `nrc_scraper_laptop2.log`

### Progress Files

Monitor progress in:
- `nrc_downloads_laptop1/scraper_progress_laptop1.json`
- `nrc_downloads_laptop2/scraper_progress_laptop2.json`
- `distributed_coordination.json`

## Advanced Configuration

### Custom VPN Locations

Edit `VPN_LOCATIONS` in the config file:
```python
VPN_LOCATIONS = [
    'Canada', 'United States', 'United Kingdom', 
    'Germany', 'Netherlands', 'Switzerland'
]
```

### Adjusting Sync Interval

Change how often laptops sync:
```python
SYNC_INTERVAL = 60  # Sync every 60 seconds
```

### Modifying Scraping Behavior

Adjust scraping parameters:
```python
MAX_DEPTH = 5              # Follow links deeper
REQUEST_DELAY = 2          # Wait longer between requests
MAX_CONSECUTIVE_ERRORS = 5 # More errors before VPN switch
```

## Security Considerations

- **VPN Credentials**: Store securely, don't commit to version control
- **Network Access**: Use secure network connections for coordination file
- **File Permissions**: Restrict access to downloaded files as needed
- **Log Files**: May contain sensitive information, secure appropriately

## Performance Tips

1. **Use SSD storage** for faster file operations
2. **High-speed internet** for faster downloads
3. **Multiple VPN locations** for better availability
4. **Regular coordination sync** to avoid conflicts
5. **Monitor disk space** for large downloads

## Support

For issues or questions:
1. Check the log files for error messages
2. Verify configuration settings
3. Test VPN connectivity manually
4. Check network access to coordination file

## License

This scraper is for educational and research purposes. Please respect the website's terms of service and robots.txt file. 