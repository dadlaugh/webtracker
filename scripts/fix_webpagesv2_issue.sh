#!/bin/bash

# Fix webpagesv2.xlsx directory issue script
# This script diagnoses and fixes the issue where webpagesv2.xlsx is treated as a directory

set -e

echo "🔍 Diagnosing webpagesv2.xlsx issue..."

# Check if webpagesv2.xlsx exists and what type it is
if [ -e "webpagesv2.xlsx" ]; then
    if [ -d "webpagesv2.xlsx" ]; then
        echo "❌ Found: webpagesv2.xlsx is a DIRECTORY (this is the problem!)"
        echo "📁 Directory contents:"
        ls -la webpagesv2.xlsx/
        
        echo ""
        echo "🛠️  Fixing the issue..."
        
        # Remove the directory
        rm -rf webpagesv2.xlsx
        
        echo "✅ Removed webpagesv2.xlsx directory"
        
        # Pull the correct file from git
        echo "📥 Pulling correct webpagesv2.xlsx file from git..."
        git checkout HEAD -- webpagesv2.xlsx
        
        if [ -f "webpagesv2.xlsx" ]; then
            echo "✅ Successfully restored webpagesv2.xlsx as a file"
            echo "📏 File size: $(ls -lh webpagesv2.xlsx | awk '{print $5}')"
        else
            echo "❌ Failed to restore webpagesv2.xlsx file"
        fi
        
    elif [ -f "webpagesv2.xlsx" ]; then
        echo "✅ Found: webpagesv2.xlsx is a FILE (this is correct)"
        echo "📏 File size: $(ls -lh webpagesv2.xlsx | awk '{print $5}')"
    else
        echo "❓ Found: webpagesv2.xlsx exists but is neither file nor directory"
        ls -la webpagesv2.xlsx
    fi
else
    echo "❌ webpagesv2.xlsx does not exist"
    echo "📥 Pulling from git..."
    git checkout HEAD -- webpagesv2.xlsx
    
    if [ -f "webpagesv2.xlsx" ]; then
        echo "✅ Successfully pulled webpagesv2.xlsx file"
        echo "📏 File size: $(ls -lh webpagesv2.xlsx | awk '{print $5}')"
    else
        echo "❌ Failed to pull webpagesv2.xlsx file"
    fi
fi

echo ""
echo "🔍 Current directory contents:"
ls -la *.xlsx 2>/dev/null || echo "No .xlsx files found"

echo ""
echo "🧪 Testing Excel file reading..."
python3 -c "
import pandas as pd
try:
    df = pd.read_excel('webpagesv2.xlsx')
    print(f'✅ Successfully read Excel file with {len(df)} rows and {len(df.columns)} columns')
    print(f'📋 Columns: {list(df.columns)}')
except Exception as e:
    print(f'❌ Error reading Excel file: {e}')
"

echo ""
echo "🎯 Next steps:"
echo "1. If the file is now correct, run: python3 webpage_tracker.py"
echo "2. If issues persist, check git status and pull latest changes" 