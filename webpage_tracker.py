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
        """Generate site name based on number, language, and URL structure."""
        try:
            number = url_info['number']
            language = url_info['language']
            url_type = url_info['type']
            url = url_info['url']
            
            # Extract domain and path from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('.', '-')
            path = parsed.path.strip('/').replace('/', '-')
            
            # Create URL-based folder name
            url_folder = f"{domain}-{path}" if path else domain
            
            # Create folder structure: number/language_type/url_folder
            site_name = f"{number:02d}/{language}_{url_type}/{url_folder}"
            
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
    
    def extract_text_content(self, html_content):
        """Extract clean, readable text content from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Extract text from meaningful elements
            text_sections = []
            
            # Get title
            title = soup.find('title')
            if title and title.get_text().strip():
                text_sections.append(f"TITLE: {title.get_text().strip()}")
            
            # Get headings (h1-h6)
            for i in range(1, 7):
                headings = soup.find_all(f'h{i}')
                for heading in headings:
                    text = heading.get_text().strip()
                    if text:
                        text_sections.append(f"H{i}: {text}")
            
            # Get paragraphs
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:  # Only meaningful paragraphs
                    text_sections.append(f"PARAGRAPH: {text}")
            
            # Get list items
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if text:
                        text_sections.append(f"LIST ITEM: {text}")
            
            # Get navigation links (if they have meaningful text)
            nav_links = soup.find_all('a')
            for link in nav_links:
                text = link.get_text().strip()
                href = link.get('href', '')
                if text and len(text) > 2 and not text.startswith('http'):
                    text_sections.append(f"LINK: {text} ({href})")
            
            return text_sections
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return []

    def generate_diff(self, site_name, old_file, new_file, date_str):
        """Generate readable text diff between two webpage versions."""
        try:
            # Create diff directory for this site
            site_diff_dir = self.diffs_dir / site_name
            site_diff_dir.mkdir(parents=True, exist_ok=True)
            
            # Read old and new files
            with open(old_file, 'r', encoding='utf-8') as f:
                old_html = f.read()
            
            with open(new_file, 'r', encoding='utf-8') as f:
                new_html = f.read()
            
            # Extract text content
            old_text_sections = self.extract_text_content(old_html)
            new_text_sections = self.extract_text_content(new_html)
            
            # Generate text diff
            diff = HtmlDiff()
            diff_html = diff.make_file(old_text_sections, new_text_sections,
                                     fromdesc=f"Version {Path(old_file).stem} (Text Content)",
                                     todesc=f"Version {date_str} (Text Content)")
            
            # Create enhanced diff with better styling
            enhanced_diff_html = self.create_enhanced_diff_html(
                diff_html, site_name, old_file, new_file, date_str,
                len(old_text_sections), len(new_text_sections)
            )
            
            # Save diff file
            diff_file = site_diff_dir / f"diff_{Path(old_file).stem}_to_{date_str}.html"
            with open(diff_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_diff_html)
            
            logger.info(f"Generated text diff: {diff_file}")
            return diff_file
            
        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return None

    def create_enhanced_diff_html(self, diff_html, site_name, old_file, new_file, date_str, old_count, new_count):
        """Create enhanced diff HTML with better styling and context."""
        enhanced_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text Content Diff - {site_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .stat-card .number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .diff-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .diff {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        .diff .diff_header {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .diff .diff_next {{
            background-color: #e8f5e8;
            color: #2d5a2d;
        }}
        .diff .diff_sub {{
            background-color: #ffeaea;
            color: #8b0000;
        }}
        .diff .diff_chg {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .legend {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 Text Content Changes</h1>
        <p>Comparing webpage text content between versions</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Site</h3>
            <div class="number">{site_name}</div>
        </div>
        <div class="stat-card">
            <h3>Previous Version</h3>
            <div class="number">{Path(old_file).stem}</div>
        </div>
        <div class="stat-card">
            <h3>New Version</h3>
            <div class="number">{date_str}</div>
        </div>
        <div class="stat-card">
            <h3>Content Sections</h3>
            <div class="number">{old_count} → {new_count}</div>
        </div>
    </div>
    
    <div class="diff-container">
        {diff_html}
    </div>
    
    <div class="legend">
        <h3>📋 Legend</h3>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #e8f5e8;"></div>
            <span>Added content (green)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #ffeaea;"></div>
            <span>Removed content (red)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #fff3cd;"></div>
            <span>Changed content (yellow)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #f8f9fa;"></div>
            <span>Unchanged content (gray)</span>
        </div>
    </div>
</body>
</html>
        """
        return enhanced_html
    
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