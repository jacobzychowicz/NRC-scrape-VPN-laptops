#!/usr/bin/env python3
"""
Distributed NRC Scraper with Multi-Laptop Coordination
Runs on multiple laptops without downloading duplicate files.
Uses a shared coordination file to track downloads across machines.
"""

import os
import re
import time
import json
import logging
import requests
import urllib.parse
import hashlib
import threading
from typing import Set, List, Optional, Dict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta

# Import VPN manager
try:
    from vpn_config import ManualVPNManager, NordVPNManager, ExpressVPNManager, ProtonVPNManager
except ImportError:
    # Fallback if vpn_config.py doesn't exist
    class ManualVPNManager:
        def __init__(self, locations):
            self.locations = locations
            self.current_location = None
            self.current_index = 0
        def connect(self, location):
            print(f"MANUAL VPN SWITCH REQUIRED: Please connect to {location}")
            time.sleep(10)
            self.current_location = location
            return True
        def disconnect(self):
            print("MANUAL VPN DISCONNECT REQUIRED")
            self.current_location = None
            return True
        def get_status(self):
            return f"Manual VPN - Current: {self.current_location}"
        def get_next_location(self):
            if self.locations:
                location = self.locations[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.locations)
                return location
            return None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DistributedNRCScraper:
    def __init__(self, 
                 base_url: str = "https://nrc.canada.ca",
                 output_dir: str = "nrc_downloads_distributed",
                 coordination_file: str = "distributed_coordination.json",
                 laptop_id: str = "laptop1",
                 vpn_locations: Optional[List[str]] = None,
                 vpn_type: str = "manual",
                 vpn_email: Optional[str] = None,
                 vpn_password: Optional[str] = None,
                 sync_interval: int = 30):
        """
        Initialize distributed NRC scraper with multi-laptop coordination
        
        Args:
            base_url: Base URL of NRC website
            output_dir: Directory to save downloaded files
            coordination_file: Shared file for coordinating between laptops
            laptop_id: Unique identifier for this laptop
            vpn_locations: List of VPN locations to switch between on errors
            vpn_type: Type of VPN client ("manual", "nordvpn", "expressvpn", "protonvpn")
            vpn_email: Email for ProtonVPN login
            vpn_password: Password for ProtonVPN login
            sync_interval: How often to sync with coordination file (seconds)
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.coordination_file = coordination_file
        self.laptop_id = laptop_id
        self.sync_interval = sync_interval
        self.session = requests.Session()
        self.visited_urls: Set[str] = set()
        self.downloaded_files: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.vpn_switch_attempts = 0
        self.max_vpn_switches = 10
        self.last_sync_time = 0
        self.coordination_lock = threading.Lock()
        
        # Initialize VPN manager
        vpn_locations = vpn_locations or ['Canada', 'United States', 'United Kingdom', 'Germany', 'Netherlands']
        if vpn_type == "nordvpn":
            self.vpn_manager = NordVPNManager(vpn_locations)
        elif vpn_type == "expressvpn":
            self.vpn_manager = ExpressVPNManager(vpn_locations)
        elif vpn_type == "protonvpn":
            # Use country codes for ProtonVPN
            proton_locations = vpn_locations or ['CA', 'US', 'GB', 'DE', 'NL']
            if vpn_email and vpn_password:
                self.vpn_manager = ProtonVPNManager(proton_locations, vpn_email, vpn_password)
            else:
                logger.warning("ProtonVPN credentials not provided, falling back to manual VPN")
                self.vpn_manager = ManualVPNManager(vpn_locations)
        else:
            self.vpn_manager = ManualVPNManager(vpn_locations)
        
        # Browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load initial progress and coordination data
        self.load_progress()
        self.load_coordination()
        
        # Start coordination sync thread
        self.sync_thread = threading.Thread(target=self._sync_coordination_loop, daemon=True)
        self.sync_thread.start()
    
    def load_coordination(self):
        """Load coordination data from shared file"""
        try:
            if os.path.exists(self.coordination_file):
                with open(self.coordination_file, 'r') as f:
                    coordination = json.load(f)
                    
                # Merge downloaded files from all laptops
                all_downloaded = set()
                for laptop_data in coordination.get('laptops', {}).values():
                    all_downloaded.update(laptop_data.get('downloaded_files', []))
                
                # Update our local sets
                self.downloaded_files.update(all_downloaded)
                logger.info(f"Loaded coordination data: {len(all_downloaded)} total downloaded files across all laptops")
            else:
                logger.info("No coordination file found, starting fresh")
                
        except Exception as e:
            logger.error(f"Failed to load coordination data: {e}")
    
    def save_coordination(self):
        """Save coordination data to shared file"""
        try:
            with self.coordination_lock:
                # Load existing coordination data
                coordination = {}
                if os.path.exists(self.coordination_file):
                    with open(self.coordination_file, 'r') as f:
                        coordination = json.load(f)
                
                # Update our laptop's data
                if 'laptops' not in coordination:
                    coordination['laptops'] = {}
                
                coordination['laptops'][self.laptop_id] = {
                    'downloaded_files': list(self.downloaded_files),
                    'visited_urls': list(self.visited_urls),
                    'failed_urls': list(self.failed_urls),
                    'last_update': datetime.now().isoformat(),
                    'vpn_status': self.vpn_manager.get_status()
                }
                
                # Save back to file
                with open(self.coordination_file, 'w') as f:
                    json.dump(coordination, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to save coordination data: {e}")
    
    def _sync_coordination_loop(self):
        """Background thread to sync coordination data"""
        while True:
            try:
                time.sleep(self.sync_interval)
                self.save_coordination()
                
                # Also load updates from other laptops
                self.load_coordination()
                
            except Exception as e:
                logger.error(f"Error in coordination sync loop: {e}")
    
    def load_progress(self):
        """Load progress from previous runs"""
        progress_file = os.path.join(self.output_dir, f"scraper_progress_{self.laptop_id}.json")
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                    self.visited_urls = set(progress.get('visited_urls', []))
                    self.downloaded_files = set(progress.get('downloaded_files', []))
                    self.failed_urls = set(progress.get('failed_urls', []))
                logger.info(f"Loaded progress: {len(self.visited_urls)} visited, {len(self.downloaded_files)} downloaded")
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")
    
    def save_progress(self):
        """Save progress to file"""
        progress_file = os.path.join(self.output_dir, f"scraper_progress_{self.laptop_id}.json")
        try:
            progress = {
                'visited_urls': list(self.visited_urls),
                'downloaded_files': list(self.downloaded_files),
                'failed_urls': list(self.failed_urls),
                'laptop_id': self.laptop_id,
                'last_update': datetime.now().isoformat()
            }
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename for filesystem compatibility"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        # Remove file extensions from folder names
        filename = re.sub(r'\.[a-zA-Z0-9]+$', '', filename)
        return filename
    
    def should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        fragment = parsed.fragment
        
        # NEVER skip PDFs - they should always be downloaded
        if path.endswith('.pdf'):
            return False
        
        # Skip fragment-only URLs (page anchors like #wb-cont, #wb-info)
        if not path or path == '' and fragment:
            return True
        
        # Skip these patterns
        skip_patterns = [
            '/docs/',  # Skip docs directory
            '/sites/default/files/css/',
            '/sites/default/files/js/',
            '/libraries/',
            '/sites/default/files/index.ico',
            '/sites/default/files/css_css_',
            '/libraries_theme-gcweb_assets_',
            '/libraries_wet-boew_css_',
            '/sites_default_files_',
            '/fr/',  # Skip French content
        ]
        
        # Check for exact path matches first
        for pattern in skip_patterns:
            if pattern in path:
                return True
        
        # Check for file extensions to skip (but not PDFs)
        skip_extensions = [
            'css',
            'js',
            'ico',
            'svg',
            'png',
            'jpg',
            'jpeg',
            'gif',
            'woff',
            'woff2',
            'ttf',
            'eot'
        ]
        
        for ext in skip_extensions:
            if path.endswith(f'.{ext}'):
                return True
        
        return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments to avoid duplicate downloads"""
        parsed = urlparse(url)
        # Remove fragment but keep query parameters
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized
    
    def is_duplicate_content(self, url: str, content: bytes) -> bool:
        """Check if content is duplicate by comparing with existing files"""
        try:
            # Create hash of content
            content_hash = hashlib.md5(content).hexdigest()
            
            # Check if we already have this content
            for existing_file in self.downloaded_files:
                if os.path.exists(existing_file):
                    try:
                        with open(existing_file, 'rb') as f:
                            existing_content = f.read()
                            existing_hash = hashlib.md5(existing_content).hexdigest()
                            if existing_hash == content_hash:
                                logger.info(f"Duplicate content detected for {url}")
                                return True
                    except Exception:
                        continue
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate content: {e}")
            return False
    
    def create_hierarchical_folder_structure(self, url: str) -> str:
        """Create hierarchical folder structure based on URL path"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # Create folder path
        folder_path = self.output_dir
        for part in path_parts[:-1]:  # Exclude the last part (filename)
            if part:
                clean_part = self.clean_filename(part)
                folder_path = os.path.join(folder_path, clean_part)
                os.makedirs(folder_path, exist_ok=True)
        
        return folder_path
    
    def get_page_filename(self, url: str) -> str:
        """Generate filename for a page URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        query = parsed.query
        
        if not path:
            filename = "index"
        else:
            # Get the last part of the path
            path_parts = path.split('/')
            filename = path_parts[-1]
            
            # If it's empty or has no extension, use 'index'
            if not filename or '.' not in filename:
                filename = "index"
            else:
                # Remove extension for HTML files
                if filename.endswith('.html') or filename.endswith('.htm'):
                    filename = filename[:-5] if filename.endswith('.html') else filename[:-4]
        
        # Add query parameters to filename if present
        if query:
            # Clean query string for filename
            clean_query = re.sub(r'[<>:"/\\|?*]', '_', query)
            clean_query = clean_query.replace('&', '_and_')
            clean_query = clean_query.replace('=', '_')
            filename += f"_{clean_query}"
        
        # Add .html extension
        filename += ".html"
        
        return self.clean_filename(filename)
    
    def switch_vpn_location(self) -> bool:
        """Switch to next VPN location"""
        try:
            self.vpn_switch_attempts += 1
            
            if self.vpn_switch_attempts > self.max_vpn_switches:
                logger.error(f"Maximum VPN switches ({self.max_vpn_switches}) reached. Giving up.")
                return False
            
            # Disconnect current VPN
            self.vpn_manager.disconnect()
            time.sleep(2)
            
            # Get next location
            if hasattr(self.vpn_manager, 'get_next_location'):
                next_location = self.vpn_manager.get_next_location()
            else:
                # Fallback for manual VPN manager
                locations = getattr(self.vpn_manager, 'locations', ['Canada', 'United States'])
                current_index = getattr(self.vpn_manager, 'current_index', 0)
                next_location = locations[current_index % len(locations)]
                self.vpn_manager.current_index = (current_index + 1) % len(locations)
            
            if not next_location:
                logger.error("No more VPN locations available")
                return False
            
            # Connect to new location
            logger.info(f"Switching VPN to: {next_location}")
            if self.vpn_manager.connect(next_location):
                self.consecutive_errors = 0
                logger.info(f"Successfully switched to VPN location: {next_location}")
                return True
            else:
                logger.error(f"Failed to switch to VPN location: {next_location}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching VPN location: {e}")
            return False
    
    def handle_error_and_switch_vpn(self, error_msg: str) -> bool:
        """Handle error and switch VPN if needed"""
        self.consecutive_errors += 1
        logger.warning(f"Error: {error_msg} (consecutive errors: {self.consecutive_errors})")
        
        if self.consecutive_errors >= self.max_consecutive_errors:
            logger.info("Too many consecutive errors, switching VPN location...")
            if self.switch_vpn_location():
                return True
            else:
                logger.error("Failed to switch VPN, will retry with current connection")
                return False
        
        return True
    
    def download_file(self, url: str, folder_path: str) -> bool:
        """Download a file from URL"""
        try:
            # Check if already downloaded by any laptop
            if url in self.downloaded_files:
                logger.info(f"File already downloaded by another laptop: {url}")
                return True
            
            # Generate filename
            parsed = urlparse(url)
            if parsed.path.endswith('.pdf'):
                filename = os.path.basename(parsed.path)
            else:
                filename = self.get_page_filename(url)
            
            file_path = os.path.join(folder_path, filename)
            
            # Check if file already exists locally
            if os.path.exists(file_path):
                logger.info(f"File already exists locally: {file_path}")
                self.downloaded_files.add(url)
                return True
            
            # Download file
            logger.info(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check for duplicate content
            if self.is_duplicate_content(url, response.content):
                logger.info(f"Duplicate content detected, skipping: {url}")
                return True
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_files.add(url)
            logger.info(f"Successfully downloaded: {file_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to download {url}: {e}"
            return self.handle_error_and_switch_vpn(error_msg)
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return False
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from a page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Only include URLs from the same domain
            if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                normalized_url = self.normalize_url(absolute_url)
                if not self.should_skip_url(normalized_url):
                    links.append(normalized_url)
        
        return links
    
    def is_downloadable_file(self, url: str) -> bool:
        """Check if URL points to a downloadable file"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check for PDF files
        if path.endswith('.pdf'):
            return True
        
        # Check for other document types
        document_extensions = [
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.csv', '.xml', '.json'
        ]
        
        for ext in document_extensions:
            if path.endswith(ext):
                return True
        
        return False
    
    def extract_and_download_pdfs(self, soup: BeautifulSoup, base_url: str) -> None:
        """Extract and download PDF links from page"""
        try:
            # Find all links that might be PDFs
            pdf_links = []
            
            # Method 1: Direct PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    absolute_url = urljoin(base_url, href)
                    if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                        pdf_links.append(absolute_url)
            
            # Method 2: Look for PDF links in text content
            for link in soup.find_all('a'):
                link_text = link.get_text().lower()
                if 'pdf' in link_text or 'download' in link_text:
                    href = link.get('href', '')
                    if href:
                        absolute_url = urljoin(base_url, href)
                        if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                            pdf_links.append(absolute_url)
            
            # Method 3: Look for data attributes that might contain PDF URLs
            for element in soup.find_all(attrs={'data-pdf-url': True}):
                pdf_url = element['data-pdf-url']
                absolute_url = urljoin(base_url, pdf_url)
                if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                    pdf_links.append(absolute_url)
            
            # Method 4: Look for JavaScript variables containing PDF URLs
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for PDF URLs in JavaScript
                    pdf_matches = re.findall(r'["\']([^"\']*\.pdf[^"\']*)["\']', script.string)
                    for match in pdf_matches:
                        absolute_url = urljoin(base_url, match)
                        if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                            pdf_links.append(absolute_url)
            
            # Download unique PDFs
            unique_pdfs = list(set(pdf_links))
            for pdf_url in unique_pdfs:
                if pdf_url not in self.downloaded_files:
                    folder_path = self.create_hierarchical_folder_structure(pdf_url)
                    self.download_file(pdf_url, folder_path)
                    
        except Exception as e:
            logger.error(f"Error extracting PDFs: {e}")
    
    def scrape_page(self, url: str, depth: int = 0) -> None:
        """Scrape a single page"""
        try:
            # Check if already visited
            if url in self.visited_urls:
                return
            
            self.visited_urls.add(url)
            
            # Check if it's a downloadable file
            if self.is_downloadable_file(url):
                folder_path = self.create_hierarchical_folder_structure(url)
                self.download_file(url, folder_path)
                return
            
            # Download the page
            logger.info(f"Scraping page (depth {depth}): {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check for duplicate content
            if self.is_duplicate_content(url, response.content):
                logger.info(f"Duplicate content detected, skipping: {url}")
                return
            
            # Save the page
            folder_path = self.create_hierarchical_folder_structure(url)
            filename = self.get_page_filename(url)
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.downloaded_files.add(url)
            logger.info(f"Saved page: {file_path}")
            
            # Extract and download PDFs from this page
            soup = BeautifulSoup(response.content, 'html.parser')
            self.extract_and_download_pdfs(soup, url)
            
            # Extract links for further scraping (limit depth)
            if depth < 3:  # Limit depth to avoid infinite recursion
                links = self.extract_links(soup, url)
                for link in links:
                    if link not in self.visited_urls and link not in self.failed_urls:
                        self.scrape_page(link, depth + 1)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to scrape {url}: {e}"
            if not self.handle_error_and_switch_vpn(error_msg):
                self.failed_urls.add(url)
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            self.failed_urls.add(url)
    
    def scrape_site(self, start_url: Optional[str] = None) -> None:
        """Start scraping the site"""
        try:
            start_url = start_url or self.base_url
            
            logger.info(f"Starting distributed scraping with laptop ID: {self.laptop_id}")
            logger.info(f"Coordination file: {self.coordination_file}")
            logger.info(f"VPN status: {self.vpn_manager.get_status()}")
            
            # Initial VPN connection
            if hasattr(self.vpn_manager, 'get_next_location'):
                initial_location = self.vpn_manager.get_next_location()
                if initial_location:
                    self.vpn_manager.connect(initial_location)
            
            # Start scraping
            self.scrape_page(start_url)
            
            # Save final progress
            self.save_progress()
            self.save_coordination()
            
            logger.info("Scraping completed!")
            logger.info(f"Total URLs visited: {len(self.visited_urls)}")
            logger.info(f"Total files downloaded: {len(self.downloaded_files)}")
            logger.info(f"Failed URLs: {len(self.failed_urls)}")
            
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
            self.save_progress()
            self.save_coordination()
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
            self.save_progress()
            self.save_coordination()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Distributed NRC Scraper')
    parser.add_argument('--laptop-id', required=True, help='Unique identifier for this laptop (e.g., laptop1, laptop2)')
    parser.add_argument('--coordination-file', default='distributed_coordination.json', help='Shared coordination file path')
    parser.add_argument('--output-dir', default='nrc_downloads_distributed', help='Output directory')
    parser.add_argument('--vpn-type', default='manual', choices=['manual', 'nordvpn', 'expressvpn', 'protonvpn'], help='VPN client type')
    parser.add_argument('--vpn-email', help='ProtonVPN email')
    parser.add_argument('--vpn-password', help='ProtonVPN password')
    parser.add_argument('--vpn-locations', nargs='+', default=['Canada', 'United States', 'United Kingdom'], help='VPN locations')
    parser.add_argument('--sync-interval', type=int, default=30, help='Coordination sync interval (seconds)')
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = DistributedNRCScraper(
        output_dir=args.output_dir,
        coordination_file=args.coordination_file,
        laptop_id=args.laptop_id,
        vpn_locations=args.vpn_locations,
        vpn_type=args.vpn_type,
        vpn_email=args.vpn_email,
        vpn_password=args.vpn_password,
        sync_interval=args.sync_interval
    )
    
    # Start scraping
    scraper.scrape_site()

if __name__ == "__main__":
    main() 