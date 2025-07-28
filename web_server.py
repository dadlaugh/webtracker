#!/usr/bin/env python3
"""
Simple Web Server for Webpage Tracker Files
Provides easy access to webpage versions and diffs for the team.
"""

from flask import Flask, render_template_string, send_from_directory, request
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
WEBPAGE_VERSIONS_DIR = 'webpage_versions'
DIFFS_DIR = 'diffs'
LOGS_DIR = 'logs'

def get_file_info(file_path):
    """Get file information for display."""
    stat = file_path.stat()
    try:
        relative_path = str(file_path.relative_to(Path.cwd()))
    except ValueError:
        # Handle case where file is not in current directory
        relative_path = str(file_path)
    return {
        'name': file_path.name,
        'size': f"{stat.st_size:,} bytes",
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'path': relative_path
    }

def list_html_files(directory):
    """List all HTML files in a directory recursively."""
    files = []
    if os.path.exists(directory):
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = Path(root) / filename
                    files.append(get_file_info(file_path))
    return sorted(files, key=lambda x: x['modified'], reverse=True)

@app.route('/')
def index():
    """Main dashboard page."""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webpage Tracker Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .nav { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
            .nav a { padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
            .nav a:hover { background: #0056b3; }
            .section { margin-bottom: 40px; }
            .section h2 { color: #555; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .file-list { list-style: none; padding: 0; }
            .file-item { padding: 15px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; background: #f9f9f9; }
            .file-item:hover { background: #f0f0f0; }
            .file-name { font-weight: bold; color: #007bff; }
            .file-info { color: #666; font-size: 0.9em; margin-top: 5px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #1976d2; }
            .stat-label { color: #555; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Webpage Tracker Dashboard</h1>
            
            <div class="nav">
                <a href="/versions">📄 Webpage Versions</a>
                <a href="/diffs">🔍 Diffs</a>
                <a href="/logs">📋 Logs</a>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ versions_count }}</div>
                    <div class="stat-label">Webpage Versions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ diffs_count }}</div>
                    <div class="stat-label">Diff Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ domains_count }}</div>
                    <div class="stat-label">Tracked Domains</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📄 Recent Webpage Versions</h2>
                <ul class="file-list">
                    {% for file in recent_versions[:5] %}
                    <li class="file-item">
                        <div class="file-name">
                            <a href="/file/{{ file.path }}" target="_blank">{{ file.name }}</a>
                        </div>
                        <div class="file-info">
                            📁 {{ file.path }} | 📏 {{ file.size }} | 🕒 {{ file.modified }}
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                <p><a href="/versions">View all versions →</a></p>
            </div>
            
            <div class="section">
                <h2>🔍 Recent Diffs</h2>
                <ul class="file-list">
                    {% for file in recent_diffs[:5] %}
                    <li class="file-item">
                        <div class="file-name">
                            <a href="/file/{{ file.path }}" target="_blank">{{ file.name }}</a>
                        </div>
                        <div class="file-info">
                            📁 {{ file.path }} | 📏 {{ file.size }} | 🕒 {{ file.modified }}
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                <p><a href="/diffs">View all diffs →</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    # Get file counts
    versions = list_html_files(WEBPAGE_VERSIONS_DIR)
    diffs = list_html_files(DIFFS_DIR)
    
    # Count unique domains
    domains = set()
    for file in versions:
        path_parts = file['path'].split('/')
        if len(path_parts) > 1:
            domains.add(path_parts[0])
    
    return render_template_string(html, 
                                versions_count=len(versions),
                                diffs_count=len(diffs),
                                domains_count=len(domains),
                                recent_versions=versions,
                                recent_diffs=diffs)

@app.route('/versions')
def versions():
    """List all webpage versions."""
    files = list_html_files(WEBPAGE_VERSIONS_DIR)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webpage Versions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .back-link { margin-bottom: 20px; }
            .back-link a { color: #007bff; text-decoration: none; }
            .file-list { list-style: none; padding: 0; }
            .file-item { padding: 15px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; background: #f9f9f9; }
            .file-item:hover { background: #f0f0f0; }
            .file-name { font-weight: bold; color: #007bff; }
            .file-info { color: #666; font-size: 0.9em; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Back to Dashboard</a>
            </div>
            <h1>📄 Webpage Versions ({{ files|length }} files)</h1>
            <ul class="file-list">
                {% for file in files %}
                <li class="file-item">
                    <div class="file-name">
                        <a href="/file/{{ file.path }}" target="_blank">{{ file.name }}</a>
                    </div>
                    <div class="file-info">
                        📁 {{ file.path }} | 📏 {{ file.size }} | 🕒 {{ file.modified }}
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, files=files)

@app.route('/diffs')
def diffs():
    """List all diff files."""
    files = list_html_files(DIFFS_DIR)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diff Files</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .back-link { margin-bottom: 20px; }
            .back-link a { color: #007bff; text-decoration: none; }
            .file-list { list-style: none; padding: 0; }
            .file-item { padding: 15px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; background: #f9f9f9; }
            .file-item:hover { background: #f0f0f0; }
            .file-name { font-weight: bold; color: #007bff; }
            .file-info { color: #666; font-size: 0.9em; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Back to Dashboard</a>
            </div>
            <h1>🔍 Diff Files ({{ files|length }} files)</h1>
            <ul class="file-list">
                {% for file in files %}
                <li class="file-item">
                    <div class="file-name">
                        <a href="/file/{{ file.path }}" target="_blank">{{ file.name }}</a>
                    </div>
                    <div class="file-info">
                        📁 {{ file.path }} | 📏 {{ file.size }} | 🕒 {{ file.modified }}
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, files=files)

@app.route('/logs')
def logs():
    """Show recent logs."""
    log_files = []
    if os.path.exists(LOGS_DIR):
        for filename in os.listdir(LOGS_DIR):
            if filename.endswith('.log'):
                file_path = Path(LOGS_DIR) / filename
                log_files.append(get_file_info(file_path))
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Log Files</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .back-link { margin-bottom: 20px; }
            .back-link a { color: #007bff; text-decoration: none; }
            .file-list { list-style: none; padding: 0; }
            .file-item { padding: 15px; border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; background: #f9f9f9; }
            .file-item:hover { background: #f0f0f0; }
            .file-name { font-weight: bold; color: #007bff; }
            .file-info { color: #666; font-size: 0.9em; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Back to Dashboard</a>
            </div>
            <h1>📋 Log Files ({{ files|length }} files)</h1>
            <ul class="file-list">
                {% for file in files %}
                <li class="file-item">
                    <div class="file-name">
                        <a href="/file/{{ file.path }}" target="_blank">{{ file.name }}</a>
                    </div>
                    <div class="file-info">
                        📁 {{ file.path }} | 📏 {{ file.size }} | 🕒 {{ file.modified }}
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, files=log_files)

@app.route('/file/<path:filepath>')
def serve_file(filepath):
    """Serve individual files."""
    return send_from_directory('.', filepath)

if __name__ == '__main__':
    print("🌐 Starting Webpage Tracker Web Server...")
    print("📱 Access your files at: http://localhost:8080")
    print("🌍 For remote access: http://your-server-ip:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=8080, debug=False) 