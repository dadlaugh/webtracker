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

def build_directory_tree(directory):
    """Build a hierarchical tree structure for a directory."""
    tree = {}
    if os.path.exists(directory):
        for root, dirs, filenames in os.walk(directory):
            # Get relative path from base directory
            rel_path = os.path.relpath(root, directory)
            if rel_path == '.':
                rel_path = ''
            
            # Create path components
            path_parts = rel_path.split(os.sep) if rel_path else []
            
            # Navigate to the correct level in the tree
            current_level = tree
            for part in path_parts:
                if part not in current_level:
                    current_level[part] = {'files': [], 'subdirs': {}}
                current_level = current_level[part]['subdirs']
            
            # Add files to current level
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = Path(root) / filename
                    file_info = get_file_info(file_path)
                    current_level[filename] = file_info
    
    return tree

def render_tree_html(tree, base_path='', level=0):
    """Render the directory tree as HTML."""
    html = ''
    indent = '  ' * level
    
    for name, content in sorted(tree.items()):
        if isinstance(content, dict) and 'files' in content:
            # This is a directory
            html += f'{indent}<div class="tree-folder">\n'
            html += f'{indent}  <div class="tree-folder-header" onclick="toggleFolder(this)">\n'
            html += f'{indent}    <span class="tree-icon">📁</span>\n'
            html += f'{indent}    <span class="tree-name">{name}</span>\n'
            html += f'{indent}  </div>\n'
            html += f'{indent}  <div class="tree-folder-content">\n'
            html += render_tree_html(content['subdirs'], f"{base_path}/{name}" if base_path else name, level + 1)
            html += f'{indent}  </div>\n'
            html += f'{indent}</div>\n'
        else:
            # This is a file
            file_info = content
            html += f'{indent}<div class="tree-file">\n'
            html += f'{indent}  <div class="tree-file-header">\n'
            html += f'{indent}    <span class="tree-icon">📄</span>\n'
            html += f'{indent}    <a href="/file/{file_info["path"]}" target="_blank" class="tree-name">{name}</a>\n'
            html += f'{indent}    <span class="tree-info">📏 {file_info["size"]} | 🕒 {file_info["modified"]}</span>\n'
            html += f'{indent}  </div>\n'
            html += f'{indent}</div>\n'
    
    return html

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
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
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
            .folder-structure { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .folder-structure h3 { color: #495057; margin-bottom: 15px; }
            .folder-tree { font-family: monospace; line-height: 1.6; }
            .folder-tree .number { color: #007bff; font-weight: bold; }
            .folder-tree .language { color: #28a745; }
            .folder-tree .type { color: #6c757d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Webpage Tracker Dashboard</h1>
            
            <div class="nav">
                <a href="/">📊 Dashboard</a>
                <a href="/versions">📁 Versions</a>
                <a href="/diffs">🔄 Diffs</a>
                <a href="/logs">📋 Logs</a>
            </div>
            
            <div class="folder-structure">
                <h3>📂 Current File Organization</h3>
                <div class="folder-tree">
                    webpage_versions/<br>
                    ├── <span class="number">01</span>/<br>
                    │   ├── <span class="language">en_reference</span>/<br>
                    │   └── <span class="language">zh_preview</span>/<br>
                    ├── <span class="number">02</span>/<br>
                    │   ├── <span class="language">en_reference</span>/<br>
                    │   └── <span class="language">zh_preview</span>/<br>
                    └── ... (continues for all entries)<br>
                    <br>
                    <small>📝 Each number represents an Excel entry with English reference and Chinese preview URLs</small>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">''' + str(len(list_html_files(WEBPAGE_VERSIONS_DIR))) + '''</div>
                    <div class="stat-label">Total Webpage Versions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">''' + str(len(list_html_files(DIFFS_DIR))) + '''</div>
                    <div class="stat-label">Generated Diffs</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📁 Recent Webpage Versions</h2>
                <ul class="file-list">
    '''
    
    # Get recent files
    recent_files = list_html_files(WEBPAGE_VERSIONS_DIR)[:10]
    
    for file_info in recent_files:
        html += f'''
                    <li class="file-item">
                        <div class="file-name">
                            <a href="/file/{file_info['path']}" target="_blank">{file_info['name']}</a>
                        </div>
                        <div class="file-info">
                            📁 {file_info['path']} | 📏 {file_info['size']} | 🕒 {file_info['modified']}
                        </div>
                    </li>
        '''
    
    html += '''
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/versions')
def versions():
    """List all webpage versions in tree structure."""
    tree = build_directory_tree(WEBPAGE_VERSIONS_DIR)
    tree_html = render_tree_html(tree)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webpage Versions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .back-link { margin-bottom: 20px; }
            .back-link a { color: #007bff; text-decoration: none; }
            
            .tree-container { 
                background: #f8f9fa; 
                border: 1px solid #dee2e6; 
                border-radius: 8px; 
                padding: 20px; 
                font-family: 'Courier New', monospace; 
                font-size: 14px; 
                line-height: 1.6; 
            }
            
            .tree-folder { margin: 5px 0; }
            .tree-folder-header { 
                cursor: pointer; 
                padding: 8px 12px; 
                background: #e9ecef; 
                border-radius: 4px; 
                margin: 2px 0; 
                display: flex; 
                align-items: center; 
                transition: background 0.2s; 
            }
            .tree-folder-header:hover { background: #dee2e6; }
            .tree-folder-content { 
                margin-left: 20px; 
                border-left: 2px solid #dee2e6; 
                padding-left: 15px; 
            }
            
            .tree-file { margin: 5px 0; }
            .tree-file-header { 
                padding: 8px 12px; 
                background: #f8f9fa; 
                border-radius: 4px; 
                margin: 2px 0; 
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                transition: background 0.2s; 
            }
            .tree-file-header:hover { background: #e9ecef; }
            
            .tree-icon { margin-right: 8px; font-size: 16px; }
            .tree-name { 
                color: #007bff; 
                text-decoration: none; 
                font-weight: 500; 
                flex-grow: 1; 
            }
            .tree-name:hover { text-decoration: underline; }
            .tree-info { 
                color: #6c757d; 
                font-size: 12px; 
                margin-left: 10px; 
            }
            
            .folder-collapsed .tree-folder-content { display: none; }
            .folder-collapsed .tree-icon { content: "📂"; }
        </style>
        <script>
            function toggleFolder(element) {
                const folder = element.parentElement;
                folder.classList.toggle('folder-collapsed');
                
                // Change icon
                const icon = element.querySelector('.tree-icon');
                if (folder.classList.contains('folder-collapsed')) {
                    icon.textContent = '📂';
                } else {
                    icon.textContent = '📁';
                }
            }
            
            // Expand all folders by default
            window.onload = function() {
                const folders = document.querySelectorAll('.tree-folder');
                folders.forEach(folder => {
                    folder.classList.remove('folder-collapsed');
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Back to Dashboard</a>
            </div>
            <h1>📄 Webpage Versions</h1>
            <div class="tree-container">
                {{ tree_html | safe }}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, tree_html=tree_html)

@app.route('/diffs')
def diffs():
    """List all diff files in tree structure."""
    tree = build_directory_tree(DIFFS_DIR)
    tree_html = render_tree_html(tree)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diff Files</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .back-link { margin-bottom: 20px; }
            .back-link a { color: #007bff; text-decoration: none; }
            
            .tree-container { 
                background: #f8f9fa; 
                border: 1px solid #dee2e6; 
                border-radius: 8px; 
                padding: 20px; 
                font-family: 'Courier New', monospace; 
                font-size: 14px; 
                line-height: 1.6; 
            }
            
            .tree-folder { margin: 5px 0; }
            .tree-folder-header { 
                cursor: pointer; 
                padding: 8px 12px; 
                background: #e9ecef; 
                border-radius: 4px; 
                margin: 2px 0; 
                display: flex; 
                align-items: center; 
                transition: background 0.2s; 
            }
            .tree-folder-header:hover { background: #dee2e6; }
            .tree-folder-content { 
                margin-left: 20px; 
                border-left: 2px solid #dee2e6; 
                padding-left: 15px; 
            }
            
            .tree-file { margin: 5px 0; }
            .tree-file-header { 
                padding: 8px 12px; 
                background: #f8f9fa; 
                border-radius: 4px; 
                margin: 2px 0; 
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                transition: background 0.2s; 
            }
            .tree-file-header:hover { background: #e9ecef; }
            
            .tree-icon { margin-right: 8px; font-size: 16px; }
            .tree-name { 
                color: #007bff; 
                text-decoration: none; 
                font-weight: 500; 
                flex-grow: 1; 
            }
            .tree-name:hover { text-decoration: underline; }
            .tree-info { 
                color: #6c757d; 
                font-size: 12px; 
                margin-left: 10px; 
            }
            
            .folder-collapsed .tree-folder-content { display: none; }
            .folder-collapsed .tree-icon { content: "📂"; }
        </style>
        <script>
            function toggleFolder(element) {
                const folder = element.parentElement;
                folder.classList.toggle('folder-collapsed');
                
                // Change icon
                const icon = element.querySelector('.tree-icon');
                if (folder.classList.contains('folder-collapsed')) {
                    icon.textContent = '📂';
                } else {
                    icon.textContent = '📁';
                }
            }
            
            // Expand all folders by default
            window.onload = function() {
                const folders = document.querySelectorAll('.tree-folder');
                folders.forEach(folder => {
                    folder.classList.remove('folder-collapsed');
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Back to Dashboard</a>
            </div>
            <h1>🔍 Diff Files</h1>
            <div class="tree-container">
                {{ tree_html | safe }}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, tree_html=tree_html)

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