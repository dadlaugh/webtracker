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

    def analyze_changes(self, old_text_sections, new_text_sections):
        """Analyze and count different types of changes between text sections."""
        try:
            from difflib import SequenceMatcher
            
            # Create a detailed diff
            matcher = SequenceMatcher(None, old_text_sections, new_text_sections)
            
            # Count different types of changes
            changes = {
                'added': 0,
                'removed': 0,
                'modified': 0,
                'unchanged': 0,
                'total_changes': 0
            }
            
            # Analyze each operation
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'replace':
                    changes['modified'] += max(i2 - i1, j2 - j1)
                    changes['total_changes'] += max(i2 - i1, j2 - j1)
                elif tag == 'delete':
                    changes['removed'] += i2 - i1
                    changes['total_changes'] += i2 - i1
                elif tag == 'insert':
                    changes['added'] += j2 - j1
                    changes['total_changes'] += j2 - j1
                elif tag == 'equal':
                    changes['unchanged'] += i2 - i1
            
            # Calculate change percentage
            total_sections = len(old_text_sections) + len(new_text_sections)
            if total_sections > 0:
                changes['change_percentage'] = (changes['total_changes'] / total_sections) * 100
            else:
                changes['change_percentage'] = 0
            
            # Add summary statistics
            changes['old_total'] = len(old_text_sections)
            changes['new_total'] = len(new_text_sections)
            changes['net_change'] = len(new_text_sections) - len(old_text_sections)
            
            return changes
            
        except Exception as e:
            logger.error(f"Error analyzing changes: {e}")
            return {
                'added': 0,
                'removed': 0,
                'modified': 0,
                'unchanged': 0,
                'total_changes': 0,
                'change_percentage': 0,
                'old_total': len(old_text_sections),
                'new_total': len(new_text_sections),
                'net_change': len(new_text_sections) - len(old_text_sections)
            }

    def get_change_summary(self, old_file, new_file):
        """Get a summary of changes between two files without generating a full diff."""
        try:
            # Read files
            with open(old_file, 'r', encoding='utf-8') as f:
                old_html = f.read()
            
            with open(new_file, 'r', encoding='utf-8') as f:
                new_html = f.read()
            
            # Extract text content
            old_text_sections = self.extract_text_content(old_html)
            new_text_sections = self.extract_text_content(new_html)
            
            # Analyze changes
            changes = self.analyze_changes(old_text_sections, new_text_sections)
            
            # Create summary
            summary = {
                'old_file': str(old_file),
                'new_file': str(new_file),
                'changes': changes,
                'summary_text': f"📊 Change Summary: {changes['total_changes']} total changes ({changes['change_percentage']:.1f}%) - Added: {changes['added']}, Removed: {changes['removed']}, Modified: {changes['modified']}"
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting change summary: {e}")
            return None

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
            
            # Analyze changes
            changes = self.analyze_changes(old_text_sections, new_text_sections)
            
            # Generate text diff
            diff = HtmlDiff()
            diff_html = diff.make_file(old_text_sections, new_text_sections,
                                     fromdesc=f"Version {Path(old_file).stem} (Text Content)",
                                     todesc=f"Version {date_str} (Text Content)")
            
            # Create enhanced diff with better styling and change statistics
            enhanced_diff_html = self.create_enhanced_diff_html(
                diff_html, site_name, old_file, new_file, date_str,
                len(old_text_sections), len(new_text_sections), changes
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

    def create_enhanced_diff_html(self, diff_html, site_name, old_file, new_file, date_str, old_count, new_count, changes):
        """Create enhanced diff HTML with better styling, navigation, search functionality, and change statistics."""
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
        
        /* Navigation Controls */
        .nav-controls {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .nav-controls button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        .nav-controls button:hover {{
            background: #5a6fd8;
        }}
        .nav-controls button:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .search-box {{
            flex: 1;
            min-width: 200px;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        .change-counter {{
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .diff-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
            max-height: 70vh;
            overflow-y: auto;
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
        
        /* Highlighted changes */
        .diff-row {{
            transition: background-color 0.3s;
        }}
        .diff-row.highlighted {{
            background-color: #fff3cd !important;
            border-left: 4px solid #ffc107;
        }}
        .diff-row.changed {{
            background-color: #fff3cd !important;
        }}
        .diff-row.added {{
            background-color: #e8f5e8 !important;
        }}
        .diff-row.removed {{
            background-color: #ffeaea !important;
        }}
        
        /* Jump to change buttons */
        .jump-to-change {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1000;
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
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
            }}
            .nav-controls {{
                flex-direction: column;
                align-items: stretch;
            }}
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
    
    <!-- Change Statistics -->
    <div class="stats">
        <div class="stat-card" style="background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);">
            <h3>➕ Added</h3>
            <div class="number" style="color: #28a745;">{changes['added']}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #ffeaea 0%, #f8d7da 100%);">
            <h3>➖ Removed</h3>
            <div class="number" style="color: #dc3545;">{changes['removed']}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);">
            <h3>🔄 Modified</h3>
            <div class="number" style="color: #ffc107;">{changes['modified']}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <h3>📊 Total Changes</h3>
            <div class="number" style="color: #6c757d;">{changes['total_changes']}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);">
            <h3>📈 Change %</h3>
            <div class="number" style="color: #17a2b8;">{changes['change_percentage']:.1f}%</div>
        </div>
    </div>
    
    <div class="nav-controls">
        <button onclick="jumpToNextChange()">⏭️ Next Change</button>
        <button onclick="jumpToPrevChange()">⏮️ Previous Change</button>
        <button onclick="toggleChangedOnly()">👁️ Show Changes Only</button>
        <button onclick="expandAll()">📖 Expand All</button>
        <button onclick="collapseAll()">📕 Collapse All</button>
        <input type="text" class="search-box" placeholder="🔍 Search in content..." onkeyup="searchContent(this.value)">
        <div class="change-counter" id="changeCounter">
            📊 {changes['total_changes']} changes ({changes['change_percentage']:.1f}%)
        </div>
    </div>
    
    <div class="diff-container" id="diffContainer">
        {diff_html}
    </div>
    
    <div class="legend">
        <h3>📋 Legend & Navigation</h3>
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
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
            <strong>Navigation Tips:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Use "Next/Previous Change" buttons to jump between changes</li>
                <li>"Show Changes Only" hides unchanged content</li>
                <li>Search box finds specific text in the diff</li>
                <li>Click on any row to highlight it</li>
            </ul>
        </div>
    </div>

    <script>
        let currentChangeIndex = 0;
        let changeRows = [];
        let showChangesOnly = false;
        let originalRows = [];
        let changesData = {{
            'total_changes': {changes['total_changes']},
            'change_percentage': {changes['change_percentage']}
        }};
        
        // Initialize the diff interface
        document.addEventListener('DOMContentLoaded', function() {{
            setupDiffInterface();
        }});
        
        function setupDiffInterface() {{
            // Find all diff rows
            const rows = document.querySelectorAll('.diff tr');
            originalRows = Array.from(rows);
            
            // Identify change rows
            changeRows = rows.filter(row => {{
                return row.querySelector('.diff_add, .diff_sub, .diff_chg') !== null;
            }});
            
            updateChangeCounter();
            
            // Add click handlers to rows
            rows.forEach(row => {{
                row.addEventListener('click', function() {{
                    highlightRow(this);
                }});
                
                // Add change indicators
                if (row.querySelector('.diff_add')) {{
                    row.classList.add('added');
                }} else if (row.querySelector('.diff_sub')) {{
                    row.classList.add('removed');
                }} else if (row.querySelector('.diff_chg')) {{
                    row.classList.add('changed');
                }}
            }});
        }}
        
        function highlightRow(row) {{
            // Remove previous highlights
            document.querySelectorAll('.diff-row.highlighted').forEach(r => {{
                r.classList.remove('highlighted');
            }});
            
            // Add highlight to clicked row
            row.classList.add('highlighted');
            row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
        
        function jumpToNextChange() {{
            if (changeRows.length === 0) return;
            
            currentChangeIndex = (currentChangeIndex + 1) % changeRows.length;
            highlightRow(changeRows[currentChangeIndex]);
        }}
        
        function jumpToPrevChange() {{
            if (changeRows.length === 0) return;
            
            currentChangeIndex = (currentChangeIndex - 1 + changeRows.length) % changeRows.length;
            highlightRow(changeRows[currentChangeIndex]);
        }}
        
        function toggleChangedOnly() {{
            showChangesOnly = !showChangesOnly;
            const container = document.getElementById('diffContainer');
            const rows = container.querySelectorAll('.diff tr');
            
            rows.forEach(row => {{
                const hasChanges = row.querySelector('.diff_add, .diff_sub, .diff_chg') !== null;
                if (showChangesOnly) {{
                    row.style.display = hasChanges ? 'table-row' : 'none';
                }} else {{
                    row.style.display = 'table-row';
                }}
            }});
            
            // Update button text
            const button = event.target;
            button.textContent = showChangesOnly ? '👁️ Show All' : '👁️ Show Changes Only';
        }}
        
        function expandAll() {{
            showChangesOnly = false;
            const rows = document.querySelectorAll('.diff tr');
            rows.forEach(row => {{
                row.style.display = 'table-row';
            }});
            document.querySelector('button[onclick="toggleChangedOnly()"]').textContent = '👁️ Show Changes Only';
        }}
        
        function collapseAll() {{
            showChangesOnly = true;
            const rows = document.querySelectorAll('.diff tr');
            rows.forEach(row => {{
                const hasChanges = row.querySelector('.diff_add, .diff_sub, .diff_chg') !== null;
                row.style.display = hasChanges ? 'table-row' : 'none';
            }});
            document.querySelector('button[onclick="toggleChangedOnly()"]').textContent = '👁️ Show All';
        }}
        
        function searchContent(query) {{
            if (!query) {{
                // Reset all rows
                originalRows.forEach(row => {{
                    row.style.display = 'table-row';
                    row.style.backgroundColor = '';
                }});
                return;
            }}
            
            const rows = document.querySelectorAll('.diff tr');
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const matches = text.includes(query.toLowerCase());
                
                if (matches) {{
                    row.style.display = 'table-row';
                    row.style.backgroundColor = '#fff3cd';
                    row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
        
        function updateChangeCounter() {{
            const counter = document.getElementById('changeCounter');
            counter.textContent = `📊 ${{changeRows.length}} changes (${{changesData.change_percentage.toFixed(1)}}%)`;
        }}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowRight' || e.key === 'n') {{
                jumpToNextChange();
            }} else if (e.key === 'ArrowLeft' || e.key === 'p') {{
                jumpToPrevChange();
            }} else if (e.key === 'c') {{
                toggleChangedOnly();
            }}
        }});
    </script>
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