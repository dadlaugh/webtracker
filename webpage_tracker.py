#!/usr/bin/env python3
"""
Webpage Change Tracker

This script reads URLs from an Excel file, fetches webpage content daily,
saves prettified HTML versions, and generates diffs between consecutive versions.
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
    def __init__(self, excel_file='webpages.xlsx'):
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
        """Read URLs from Excel file."""
        try:
            if not os.path.exists(self.excel_file):
                logger.error(f"Excel file '{self.excel_file}' not found!")
                return []
            
            df = pd.read_excel(self.excel_file)
            
            if 'URL' not in df.columns:
                logger.error("Excel file must contain a 'URL' column!")
                return []
            
            # Filter out empty URLs and get unique URLs
            urls = df['URL'].dropna().unique().tolist()
            logger.info(f"Found {len(urls)} URLs in Excel file")
            return urls
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return []
    
    def get_site_name(self, url):
        """Extract site name from URL for folder naming."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '').replace('.', '_')
            
            # Get the path and make it filesystem-safe
            path = parsed.path.strip('/')
            if path:
                # Replace problematic characters in path
                safe_path = path.replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_').replace('#', '_')
                # Remove trailing underscores
                safe_path = safe_path.rstrip('_')
                # Limit path length
                if len(safe_path) > 100:
                    safe_path = safe_path[:100]
                # Return domain/path structure
                return f"{domain}/{safe_path}"
            else:
                # No path, just return domain
                return domain
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
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
        try:
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href')
                if href:
                    css_url = self._resolve_url(href, base_url)
                    try:
                        css_response = self.session.get(css_url, timeout=10)
                        if css_response.status_code == 200:
                            css_content = css_response.text
                            # Create inline style tag
                            style_tag = soup.new_tag('style')
                            style_tag.string = css_content
                            link.replace_with(style_tag)
                            logger.debug(f"Embedded CSS: {css_url}")
                    except Exception as e:
                        logger.debug(f"Failed to embed CSS {css_url}: {e}")
        except Exception as e:
            logger.debug(f"Error processing CSS: {e}")
    
    def _download_and_embed_js(self, soup, base_url):
        """Download and embed JavaScript files inline."""
        try:
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if src:
                    js_url = self._resolve_url(src, base_url)
                    try:
                        js_response = self.session.get(js_url, timeout=10)
                        if js_response.status_code == 200:
                            js_content = js_response.text
                            # Create inline script tag
                            new_script = soup.new_tag('script')
                            new_script.string = js_content
                            script.replace_with(new_script)
                            logger.debug(f"Embedded JS: {js_url}")
                    except Exception as e:
                        logger.debug(f"Failed to embed JS {js_url}: {e}")
        except Exception as e:
            logger.debug(f"Error processing JS: {e}")
    
    def _download_and_embed_images(self, soup, base_url):
        """Download and embed images as base64."""
        try:
            import base64
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    img_url = self._resolve_url(src, base_url)
                    try:
                        img_response = self.session.get(img_url, timeout=10)
                        if img_response.status_code == 200:
                            # Convert to base64
                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            content_type = img_response.headers.get('content-type', 'image/png')
                            img['src'] = f"data:{content_type};base64,{img_base64}"
                            logger.debug(f"Embedded image: {img_url}")
                    except Exception as e:
                        logger.debug(f"Failed to embed image {img_url}: {e}")
        except Exception as e:
            logger.debug(f"Error processing images: {e}")
    
    def _resolve_url(self, relative_url, base_url):
        """Resolve relative URLs to absolute URLs."""
        try:
            from urllib.parse import urljoin
            return urljoin(base_url, relative_url)
        except Exception as e:
            logger.debug(f"Error resolving URL {relative_url}: {e}")
            return relative_url
    
    def save_webpage_version(self, site_name, html_content, date_str):
        """Save webpage version to file."""
        try:
            # Handle hierarchical folder structure (domain/path)
            site_dir = self.webpage_versions_dir / site_name
            site_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = site_dir / f"{date_str}.html"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Saved webpage version: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving webpage version for {site_name}: {e}")
            return None
    
    def get_previous_version(self, site_name):
        """Get the most recent previous version of a webpage."""
        try:
            site_dir = self.webpage_versions_dir / site_name
            if not site_dir.exists():
                return None
            
            # Get all HTML files and sort by date
            html_files = list(site_dir.glob("*.html"))
            if len(html_files) < 2:  # Need at least 2 files to compare
                return None
            
            # Sort by filename (date) and get the second most recent
            html_files.sort(reverse=True)
            return html_files[1]  # Second most recent
            
        except Exception as e:
            logger.error(f"Error getting previous version for {site_name}: {e}")
            return None
    
    def generate_diff(self, site_name, old_file, new_file, date_str):
        """Generate HTML diff between two webpage versions."""
        try:
            # Read the files
            with open(old_file, 'r', encoding='utf-8') as f:
                old_content = f.readlines()
            
            with open(new_file, 'r', encoding='utf-8') as f:
                new_content = f.readlines()
            
            # Generate diff
            html_diff = HtmlDiff()
            diff_content = html_diff.make_file(old_content, new_content, 
                                             fromdesc=f"Previous version ({old_file.stem})",
                                             todesc=f"Current version ({new_file.stem})")
            
            # Save diff with hierarchical structure
            diff_dir = self.diffs_dir / site_name
            diff_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the date of the previous version for the filename
            prev_date = old_file.stem
            diff_filename = f"diff_{prev_date}_to_{date_str}.html"
            diff_path = diff_dir / diff_filename
            
            with open(diff_path, 'w', encoding='utf-8') as f:
                f.write(diff_content)
            
            logger.info(f"Generated diff: {diff_path}")
            return diff_path
            
        except Exception as e:
            logger.error(f"Error generating diff for {site_name}: {e}")
            return None
    
    def process_url(self, url):
        """Process a single URL: fetch, save, and generate diff if needed."""
        site_name = self.get_site_name(url)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch current webpage
        html_content = self.fetch_webpage(url)
        if html_content is None:
            return False
        
        # Save current version
        current_file = self.save_webpage_version(site_name, html_content, date_str)
        if current_file is None:
            return False
        
        # Check if we have a previous version to compare
        previous_file = self.get_previous_version(site_name)
        if previous_file:
            # Generate diff
            diff_path = self.generate_diff(site_name, previous_file, current_file, date_str)
            if diff_path:
                logger.info(f"Change detected for {site_name}. Diff saved at: {diff_path}")
                print(f"Change detected for {site_name}. Diff saved at: {diff_path}")
            else:
                logger.warning(f"Failed to generate diff for {site_name}")
        else:
            logger.info(f"First version saved for {site_name}. No diff generated.")
        
        return True
    
    def run(self):
        """Main execution method."""
        logger.info("Starting webpage tracker...")
        start_time = time.time()
        
        # Read URLs from Excel
        urls = self.read_urls_from_excel()
        if not urls:
            logger.error("No URLs found. Exiting.")
            return
        
        # Process each URL
        successful = 0
        failed = 0
        
        for url in urls:
            if self.process_url(url):
                successful += 1
            else:
                failed += 1
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Webpage tracker completed in {duration:.2f} seconds")
        logger.info(f"Successfully processed: {successful} URLs")
        logger.info(f"Failed to process: {failed} URLs")
        
        print(f"\nSummary:")
        print(f"Successfully processed: {successful} URLs")
        print(f"Failed to process: {failed} URLs")
        print(f"Total time: {duration:.2f} seconds")

def main():
    """Main entry point."""
    tracker = WebpageTracker()
    tracker.run()

if __name__ == "__main__":
    main() 