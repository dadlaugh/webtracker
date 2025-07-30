#!/usr/bin/env python3
"""
Generate Translation Tables from Saved Webpage Versions

This script processes existing saved webpage versions and creates
translation reference tables for translation work.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path to import WebpageTracker
sys.path.append(str(Path(__file__).parent.parent))

from webpage_tracker import WebpageTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TranslationTableGenerator:
    def __init__(self):
        self.webpage_versions_dir = Path('webpage_versions')
        self.translation_dir = Path('translation_references')
        self.translation_dir.mkdir(exist_ok=True)
    
    def get_all_saved_versions(self):
        """Get all saved webpage versions."""
        versions = []
        
        if not self.webpage_versions_dir.exists():
            logger.warning("No webpage versions directory found")
            return versions
        
        for site_dir in self.webpage_versions_dir.iterdir():
            if site_dir.is_dir():
                site_name = site_dir.name
                for html_file in site_dir.glob("*.html"):
                    versions.append({
                        'site_name': site_name,
                        'file_path': html_file,
                        'date': html_file.stem
                    })
        
        return versions
    
    def process_saved_version(self, version_info):
        """Process a saved webpage version and create translation table."""
        try:
            site_name = version_info['site_name']
            file_path = version_info['file_path']
            date_str = version_info['date']
            
            logger.info(f"Processing {site_name} from {date_str}")
            
            # Read HTML content
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create tracker instance to use its extraction methods
            tracker = WebpageTracker()
            
            # Extract text content
            extracted_data = tracker.extract_text_content(html_content, f"file://{file_path}", date_str)
            if not extracted_data:
                logger.error(f"Failed to extract content from {file_path}")
                return None
            
            # Create translation table
            translation_file = tracker.create_translation_table(extracted_data, site_name)
            if translation_file:
                logger.info(f"Created translation table: {translation_file}")
                return translation_file
            
        except Exception as e:
            logger.error(f"Error processing {version_info['file_path']}: {e}")
            return None
    
    def generate_all_translation_tables(self):
        """Generate translation tables for all saved webpage versions."""
        logger.info("Starting translation table generation...")
        
        versions = self.get_all_saved_versions()
        if not versions:
            logger.warning("No saved webpage versions found")
            return
        
        logger.info(f"Found {len(versions)} saved webpage versions")
        
        success_count = 0
        for version in versions:
            if self.process_saved_version(version):
                success_count += 1
        
        logger.info(f"Translation table generation complete! {success_count}/{len(versions)} tables created successfully.")
    
    def generate_for_specific_site(self, site_name):
        """Generate translation table for a specific site."""
        logger.info(f"Generating translation table for site: {site_name}")
        
        site_dir = self.webpage_versions_dir / site_name
        if not site_dir.exists():
            logger.error(f"Site directory not found: {site_dir}")
            return
        
        # Get the most recent version
        html_files = list(site_dir.glob("*.html"))
        if not html_files:
            logger.error(f"No HTML files found for site: {site_name}")
            return
        
        # Sort by date and get the most recent
        html_files.sort(reverse=True)
        latest_file = html_files[0]
        date_str = latest_file.stem
        
        version_info = {
            'site_name': site_name,
            'file_path': latest_file,
            'date': date_str
        }
        
        self.process_saved_version(version_info)

def main():
    """Main function."""
    generator = TranslationTableGenerator()
    
    if len(sys.argv) > 1:
        # Generate for specific site
        site_name = sys.argv[1]
        generator.generate_for_specific_site(site_name)
    else:
        # Generate for all sites
        generator.generate_all_translation_tables()

if __name__ == "__main__":
    main() 