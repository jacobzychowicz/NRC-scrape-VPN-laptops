# Quick Start Guide - Windows 11

This guide will help you set up the distributed NRC scraper on your Windows 11 laptops.

## Prerequisites

- Python 3.7 or higher installed on both laptops
- Git installed on both laptops
- Network access between laptops (for coordination file sharing)

## Step 1: Clone the Repository

On both laptops, open Command Prompt or PowerShell and run:

```bash
git clone <your-github-repo-url>
cd distributed_nrc_scraper
```

## Step 2: Install Dependencies

On both laptops, install the required Python packages:

```bash
pip install -r requirements.txt
```

## Step 3: Setup Each Laptop

### Laptop 1 Setup

```bash
python setup_distributed_scraper.py
```

When prompted:
- **Laptop ID**: Enter `laptop1`
- **VPN Type**: Choose `manual` (or your preferred VPN)
- **Coordination File**: Choose option 4 (local file) for now

### Laptop 2 Setup

```bash
python setup_distributed_scraper.py
```

When prompted:
- **Laptop ID**: Enter `laptop2`
- **VPN Type**: Choose `manual` (or your preferred VPN)
- **Coordination File**: Choose option 4 (local file) for now

## Step 4: Test the Setup

On both laptops, run the test script:

```bash
python test_distributed_setup.py
```

Make sure all tests pass before proceeding.

## Step 5: Setup Coordination File Sharing

### Option A: Network Drive (Recommended)

1. Create a shared folder on one laptop or a network drive
2. Edit `distributed_config.py` on both laptops
3. Change `COORDINATION_FILE` to the network path:
   ```python
   COORDINATION_FILE = "\\\\laptop1\\shared\\nrc_scraper\\distributed_coordination.json"
   ```

### Option B: Cloud Sync (Dropbox/OneDrive)

1. Install Dropbox or OneDrive on both laptops
2. Create a folder for the scraper
3. Edit `distributed_config.py` on both laptops:
   ```python
   COORDINATION_FILE = "C:\\Users\\YourUsername\\Dropbox\\nrc_scraper\\distributed_coordination.json"
   ```

### Option C: USB Drive

1. Use a USB drive to transfer the coordination file
2. Edit `distributed_config.py` on both laptops:
   ```python
   COORDINATION_FILE = "E:\\nrc_scraper\\distributed_coordination.json"
   ```

## Step 6: Start Scraping

### Start Laptop 1

```bash
python run_distributed_scraper_config.py
```

### Start Laptop 2

```bash
python run_distributed_scraper_config.py
```

## Monitoring Progress

- **Log files**: `nrc_scraper_laptop1.log`, `nrc_scraper_laptop2.log`
- **Progress files**: `nrc_downloads_laptop1/scraper_progress_laptop1.json`
- **Coordination file**: `distributed_coordination.json`
- **Output directories**: `nrc_downloads_laptop1/`, `nrc_downloads_laptop2/`

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Run `pip install -r requirements.txt`
2. **Permission errors**: Run Command Prompt as Administrator
3. **Network access issues**: Check Windows Firewall settings
4. **VPN connection problems**: Test VPN manually first

### Getting Help

1. Check the log files for error messages
2. Run `python test_distributed_setup.py` to verify setup
3. Check the main README.md for detailed documentation

## Next Steps

- Configure automatic VPN switching if needed
- Set up monitoring and alerts
- Optimize performance settings
- Set up automatic backups of downloaded files 