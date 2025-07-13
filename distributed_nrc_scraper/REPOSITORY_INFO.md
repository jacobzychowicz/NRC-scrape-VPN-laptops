# Distributed NRC Scraper Repository

This repository contains a distributed web scraper for the National Research Council Canada (NRC) website that can run on multiple laptops simultaneously without downloading duplicate files.

## Repository Structure

```
distributed_nrc_scraper/
├── README.md                           # Main documentation
├── QUICK_START.md                      # Quick start guide for Windows 11
├── REPOSITORY_INFO.md                  # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── Core Files:
├── distributed_nrc_scraper.py          # Main scraper with coordination
├── vpn_config.py                       # VPN management for multiple providers
├── run_distributed_scraper_config.py   # Runner script using config
├── setup_distributed_scraper.py        # Interactive setup wizard
├── test_distributed_setup.py           # Setup verification tests
│
├── Windows Batch Files:
├── setup_laptop.bat                    # Easy setup for Windows
├── test_setup.bat                      # Easy testing for Windows
├── start_scraping.bat                  # Easy scraper start for Windows
│
└── Generated Files (after setup):
    ├── distributed_config.py           # Laptop-specific configuration
    ├── distributed_coordination.json   # Shared coordination file
    ├── nrc_downloads_laptop1/          # Output directory for laptop1
    ├── nrc_downloads_laptop2/          # Output directory for laptop2
    ├── nrc_scraper_laptop1.log         # Log file for laptop1
    ├── nrc_scraper_laptop2.log         # Log file for laptop2
    └── run_scraper_laptop1.bat         # Generated batch file
```

## Key Features

- **Distributed Operation**: Run on multiple laptops simultaneously
- **No Duplicate Downloads**: Coordination system prevents downloading the same files
- **VPN Support**: Automatic VPN switching with multiple providers
- **Progress Tracking**: Saves progress and can resume from where it left off
- **PDF Detection**: Automatically finds and downloads PDF files
- **Error Handling**: Graceful handling of network errors and VPN issues
- **Easy Setup**: Interactive setup wizard for each laptop

## Supported VPN Providers

- **Manual VPN**: You switch locations manually
- **ProtonVPN**: Automatic CLI switching
- **NordVPN**: Automatic CLI switching
- **ExpressVPN**: Automatic CLI switching

## Quick Setup for Windows 11

1. **Clone the repository** on both laptops
2. **Run setup**: Double-click `setup_laptop.bat`
3. **Test setup**: Double-click `test_setup.bat`
4. **Start scraping**: Double-click `start_scraping.bat`

## Coordination Methods

The scraper supports multiple ways to share coordination data between laptops:

1. **Network Drive**: Shared folder accessible by both laptops
2. **Cloud Sync**: Dropbox, OneDrive, or Google Drive
3. **USB Drive**: Manual file transfer
4. **Local File**: Manual copy between laptops

## File Filtering

The scraper automatically filters out:
- CSS, JavaScript, and image files
- French content (`/fr/` URLs)
- Documentation pages (`/docs/` URLs)
- Duplicate content based on file hashes

## Monitoring

Monitor progress through:
- **Log files**: `nrc_scraper_laptop1.log`, `nrc_scraper_laptop2.log`
- **Progress files**: `scraper_progress_laptop1.json`
- **Coordination file**: `distributed_coordination.json`
- **Output directories**: `nrc_downloads_laptop1/`, `nrc_downloads_laptop2/`

## Security Notes

- VPN credentials are stored locally and not committed to version control
- The `.gitignore` file excludes sensitive configuration files
- Network access should be secured for coordination file sharing

## License

This scraper is for educational and research purposes. Please respect the website's terms of service and robots.txt file.

## Support

For issues or questions:
1. Check the log files for error messages
2. Run `test_distributed_setup.py` to verify setup
3. Check the main README.md for detailed documentation
4. Verify VPN configuration if using automatic VPN

## Contributing

When contributing to this repository:
1. Test your changes on both laptops
2. Update documentation as needed
3. Ensure VPN credentials are not committed
4. Follow the existing code style and structure 