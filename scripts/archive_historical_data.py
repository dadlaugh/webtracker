#!/usr/bin/env python3
"""
Archive Historical Data Script
This script archives old webpage versions and diffs before implementing the new structure.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def archive_historical_data():
    """Archive historical data to preserve it while implementing new structure."""
    
    # Create archive directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir = Path(f'historical_archive_{timestamp}')
    archive_dir.mkdir(exist_ok=True)
    
    print(f"📦 Creating historical archive: {archive_dir}")
    
    # Archive webpage versions
    webpage_versions_dir = Path('webpage_versions')
    if webpage_versions_dir.exists():
        archive_versions_dir = archive_dir / 'webpage_versions'
        archive_versions_dir.mkdir(exist_ok=True)
        
        # Copy all old structure files (non-numbered folders)
        old_folders = []
        for item in webpage_versions_dir.iterdir():
            if item.is_dir() and not item.name.isdigit():
                old_folders.append(item)
        
        if old_folders:
            print(f"📁 Archiving {len(old_folders)} old folders...")
            for folder in old_folders:
                dest = archive_versions_dir / folder.name
                shutil.copytree(folder, dest)
                print(f"  ✅ Archived: {folder.name}")
        else:
            print("📁 No old folders to archive")
    
    # Archive diffs
    diffs_dir = Path('diffs')
    if diffs_dir.exists():
        archive_diffs_dir = archive_dir / 'diffs'
        archive_diffs_dir.mkdir(exist_ok=True)
        
        # Copy all diff files
        diff_files = list(diffs_dir.rglob('*.html'))
        if diff_files:
            print(f"🔄 Archiving {len(diff_files)} diff files...")
            for diff_file in diff_files:
                # Create relative path structure
                rel_path = diff_file.relative_to(diffs_dir)
                dest = archive_diffs_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(diff_file, dest)
                print(f"  ✅ Archived: {rel_path}")
        else:
            print("🔄 No diff files to archive")
    
    # Create archive info file
    info_file = archive_dir / 'archive_info.txt'
    with open(info_file, 'w') as f:
        f.write(f"Historical Data Archive\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archive Directory: {archive_dir}\n\n")
        f.write(f"Contents:\n")
        f.write(f"- webpage_versions/: Old domain-based structure\n")
        f.write(f"- diffs/: Historical diff files\n\n")
        f.write(f"New Structure:\n")
        f.write(f"- Uses Excel-based numbering (01, 02, 03, etc.)\n")
        f.write(f"- Language-based folders (en_reference, zh_preview)\n")
        f.write(f"- Clean, organized structure\n")
    
    print(f"\n✅ Historical archive created successfully!")
    print(f"📁 Archive location: {archive_dir}")
    print(f"📄 Archive info: {info_file}")
    
    return archive_dir

if __name__ == "__main__":
    archive_historical_data() 