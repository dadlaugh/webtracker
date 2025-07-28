#!/usr/bin/env python3
"""
Helper script to create a sample Excel file with URLs for testing.
"""

import pandas as pd

# Sample URLs for testing
sample_urls = [
    "https://www.example.com",
    "https://httpbin.org/html",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://www.google.com",
    "https://www.github.com"
]

# Create DataFrame
df = pd.DataFrame({
    'URL': sample_urls,
    'Name': ['Example Site', 'HTTP Bin', 'JSON Placeholder', 'Google', 'GitHub'],
    'Description': ['Basic example site', 'Test HTTP responses', 'Fake API', 'Search engine', 'Code hosting']
})

# Save to Excel
df.to_excel('webpages.xlsx', index=False)
print("Sample Excel file 'webpages.xlsx' created successfully!")
print(f"Added {len(sample_urls)} sample URLs") 