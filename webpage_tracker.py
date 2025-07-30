#!/usr/bin/env python3
"""
Webpage Change Tracker

This script reads URLs from an Excel file, fetches webpage content daily,
saves prettified HTML versions, and generates diffs between consecutive versions.
Also extracts text content for translation references.
"""

import os
import sys
import logging
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from difflib import HtmlDiff
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webpage_tracker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebpageTracker:
    def __init__(self, excel_file='webpagesv2.xlsx'):
        self.excel_file = excel_file
        self.webpage_versions_dir = Path('webpage_versions')
        self.diffs_dir = Path('diffs')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories if they don't exist
        self.webpage_versions_dir.mkdir(exist_ok=True)
        self.diffs_dir.mkdir(exist_ok=True)
    
    def read_urls_from_excel(self):
        """Read URLs from Excel file with new structure."""
        try:
            if not os.path.exists(self.excel_file):
                logger.error(f"Excel file '{self.excel_file}' not found!")
                return []
            
            df = pd.read_excel(self.excel_file)
            
            # Check for required columns
            required_columns = ['NO.', 'AU - EN reference', 'AU - ZH Preview URL']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Excel file missing required columns: {missing_columns}")
                return []
            
            # Create a list of URL entries with metadata
            url_entries = []
            for _, row in df.iterrows():
                number = row['NO.']
                au_en_url = row['AU - EN reference']
                au_zh_url = row['AU - ZH Preview URL']
                
                # Add AU English URL
                if pd.notna(au_en_url) and au_en_url.strip():
                    url_entries.append({
                        'url': au_en_url.strip(),
                        'number': number,
                        'language': 'en',
                        'type': 'reference'
                    })
                
                # Add AU Chinese URL
                if pd.notna(au_zh_url) and au_zh_url.strip():
                    url_entries.append({
                        'url': au_zh_url.strip(),
                        'number': number,
                        'language': 'zh',
                        'type': 'preview'
                    })
            
            logger.info(f"Found {len(url_entries)} URLs in Excel file across {len(df)} entries")
            return url_entries
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return []
    
    def get_site_name(self, url_info):
        """Generate site name based on number and language structure."""
        try:
            number = url_info['number']
            language = url_info['language']
            url_type = url_info['type']
            
            # Create folder structure: number/language_type
            site_name = f"{number:02d}/{language}_{url_type}"
            
            return site_name
            
        except Exception as e:
            logger.error(f"Error generating site name for {url_info}: {e}")
            return "unknown_site"
    
    def fetch_webpage(self, url):
        """Fetch webpage content with comprehensive asset handling."""
        try:
            logger.info(f"Fetching webpage: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Download and embed CSS files
            self._download_and_embed_css(soup, url)
            
            # Download and embed JavaScript files
            self._download_and_embed_js(soup, url)
            
            # Download and embed images (convert to base64)
            self._download_and_embed_images(soup, url)
            
            # Prettify the enhanced HTML
            prettified_html = soup.prettify()
            
            logger.info(f"Successfully fetched {len(prettified_html)} characters from {url}")
            return prettified_html
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None
    
    def _download_and_embed_css(self, soup, base_url):
        """Download and embed CSS files inline."""
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                try:
                    css_url = self._resolve_url(href, base_url)
                    response = self.session.get(css_url, timeout=10)
                    if response.status_code == 200:
                        css_content = response.text
                        # Create style tag and replace link
                        style_tag = soup.new_tag('style')
                        style_tag.string = css_content
                        link.replace_with(style_tag)
                except Exception as e:
                    logger.warning(f"Failed to embed CSS {href}: {e}")
    
    def _download_and_embed_js(self, soup, base_url):
        """Download and embed JavaScript files inline."""
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                try:
                    js_url = self._resolve_url(src, base_url)
                    response = self.session.get(js_url, timeout=10)
                    if response.status_code == 200:
                        js_content = response.text
                        # Update script tag content
                        script.string = js_content
                        script['src'] = None
                except Exception as e:
                    logger.warning(f"Failed to embed JS {src}: {e}")
    
    def _download_and_embed_images(self, soup, base_url):
        """Download and embed images as base64."""
        import base64
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith('data:'):
                try:
                    img_url = self._resolve_url(src, base_url)
                    response = self.session.get(img_url, timeout=10)
                    if response.status_code == 200:
                        # Convert to base64
                        img_base64 = base64.b64encode(response.content).decode('utf-8')
                        content_type = response.headers.get('content-type', 'image/png')
                        img['src'] = f"data:{content_type};base64,{img_base64}"
                except Exception as e:
                    logger.warning(f"Failed to embed image {src}: {e}")
    
    def _resolve_url(self, relative_url, base_url):
        """Resolve relative URLs to absolute URLs."""
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)
    
    def save_webpage_version(self, site_name, html_content, date_str):
        """Save webpage version to file."""
        try:
            site_dir = self.webpage_versions_dir / site_name
            site_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = site_dir / f"{date_str}.html"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Saved webpage version: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving webpage version: {e}")
            return None
    
    def get_previous_version(self, site_name):
        """Get the most recent previous version of a webpage."""
        try:
            site_dir = self.webpage_versions_dir / site_name
            if not site_dir.exists():
                return None
            
            # Get all HTML files and sort by date
            html_files = list(site_dir.glob("*.html"))
            if len(html_files) < 2:  # Need at least 2 files for diff
                return None
            
            # Sort by filename (date) and get the second most recent
            html_files.sort(reverse=True)
            return str(html_files[1])  # Return the previous version
            
        except Exception as e:
            logger.error(f"Error getting previous version: {e}")
            return None
    
    def generate_diff(self, site_name, old_file, new_file, date_str):
        """Generate HTML diff between two webpage versions."""
        try:
            # Create diff directory for this site
            site_diff_dir = self.diffs_dir / site_name
            site_diff_dir.mkdir(parents=True, exist_ok=True)
            
            # Read old and new files
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.readlines()
            
            with open(new_file, 'r', encoding='utf-8') as f:
                new_content = f.readlines()
            
            # Generate diff
            diff = HtmlDiff()
            diff_html = diff.make_file(old_content, new_content, 
                                     fromdesc=f"Version {Path(old_file).stem}",
                                     todesc=f"Version {date_str}")
            
            # Save diff file
            diff_file = site_diff_dir / f"diff_{Path(old_file).stem}_to_{date_str}.html"
            with open(diff_file, 'w', encoding='utf-8') as f:
                f.write(diff_html)
            
            logger.info(f"Generated diff: {diff_file}")
            return diff_file
            
        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return None
    
    def process_url(self, url_info):
        """Process a single URL: fetch, save, and create diff."""
        try:
            site_name = self.get_site_name(url_info)
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Fetch webpage
            html_content = self.fetch_webpage(url_info['url'])
            if not html_content:
                return False
            
            # Save webpage version
            self.save_webpage_version(site_name, html_content, date_str)
            
            # Generate diff if previous version exists
            previous_version = self.get_previous_version(site_name)
            if previous_version:
                self.generate_diff(site_name, previous_version, f"{self.webpage_versions_dir}/{site_name}/{date_str}.html", date_str)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing URL {url_info['url']}: {e}")
            return False
    
    def run(self):
        """Main execution method."""
        logger.info("Starting Webpage Tracker...")
        
        urls = self.read_urls_from_excel()
        if not urls:
            logger.error("No URLs found in Excel file!")
            return
        
        success_count = 0
        total_count = len(urls)
        
        for url_info in urls:
            logger.info(f"Processing URL: {url_info['url']}")
            if self.process_url(url_info):
                success_count += 1
            else:
                logger.error(f"Failed to process URL: {url_info['url']}")
            
            # Add delay between requests
            time.sleep(2)
        
        logger.info(f"Processing complete! {success_count}/{total_count} URLs processed successfully.")

def main():
    """Main function."""
    tracker = WebpageTracker()
    tracker.run()

if __name__ == "__main__":
    main() 