#!/usr/bin/env python3
"""
Script to compare specific files in the CMC Markets folder.
"""

import os
from pathlib import Path
from webpage_tracker import WebpageTracker

def compare_cmc_files():
    """Compare the two CMC Markets files."""
    
    # Define the file paths
    folder_path = Path('webpage_versions/01/en_reference/www-cmcmarkets-com-preview-en-au-cfd')
    old_file = folder_path / '2025-07-29.html'
    new_file = folder_path / '2025-07-30.html'
    
    print(f"📁 Comparing files in: {folder_path}")
    print(f"📄 Old file: {old_file}")
    print(f"📄 New file: {new_file}")
    
    # Check if files exist
    if not old_file.exists():
        print(f"❌ Old file not found: {old_file}")
        return
    
    if not new_file.exists():
        print(f"❌ New file not found: {new_file}")
        return
    
    # Create tracker instance
    tracker = WebpageTracker()
    
    # Create site name for the diff
    site_name = "01/en_reference/www-cmcmarkets-com-preview-en-au-cfd"
    
    print("\n🔄 Generating diff...")
    
    # Generate the diff
    diff_file = tracker.generate_diff(
        site_name=site_name,
        old_file=str(old_file),
        new_file=str(new_file),
        date_str="2025-07-30"
    )
    
    if diff_file:
        print(f"✅ Diff generated successfully!")
        print(f"📄 Diff file: {diff_file}")
        print(f"🌐 Web server URL: http://localhost:8080/file/{diff_file}")
        print(f"📂 Direct file path: {os.path.abspath(diff_file)}")
        
        # Show file sizes for context
        old_size = old_file.stat().st_size / (1024 * 1024)  # MB
        new_size = new_file.stat().st_size / (1024 * 1024)  # MB
        
        print(f"\n📊 File Information:")
        print(f"   Old file (2025-07-29): {old_size:.1f} MB")
        print(f"   New file (2025-07-30): {new_size:.1f} MB")
        print(f"   Size difference: {abs(new_size - old_size):.1f} MB")
        
        return diff_file
    else:
        print("❌ Failed to generate diff")
        return None

if __name__ == "__main__":
    print("🔍 Comparing CMC Markets Files")
    print("=" * 40)
    
    diff_file = compare_cmc_files()
    
    if diff_file:
        print("\n🎉 Comparison completed!")
        print("You can now view the diff in your browser at the URL above.")
        print("The new diff will show:")
        print("✅ Text content changes (not raw HTML)")
        print("✅ Color-coded additions/removals")
        print("✅ Statistics and modern UI")
        print("✅ Easy-to-read format")
    else:
        print("\n❌ Comparison failed") 