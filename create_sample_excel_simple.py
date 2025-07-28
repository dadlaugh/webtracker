#!/usr/bin/env python3
"""
Simple helper script to create a sample Excel file with URLs for testing.
Uses openpyxl directly without pandas dependency.
"""

from openpyxl import Workbook

# Sample URLs for testing
sample_data = [
    ("https://www.example.com", "Example Site", "Basic example site"),
    ("https://httpbin.org/html", "HTTP Bin", "Test HTTP responses"),
    ("https://jsonplaceholder.typicode.com/posts/1", "JSON Placeholder", "Fake API"),
    ("https://www.google.com", "Google", "Search engine"),
    ("https://www.github.com", "GitHub", "Code hosting")
]

# Create workbook and worksheet
wb = Workbook()
ws = wb.active
ws.title = "Webpages"

# Add headers
ws.append(["URL", "Name", "Description"])

# Add data
for url, name, description in sample_data:
    ws.append([url, name, description])

# Save to Excel
wb.save('webpages.xlsx')
print("Sample Excel file 'webpages.xlsx' created successfully!")
print(f"Added {len(sample_data)} sample URLs") 