import os
from pathlib import Path
from datetime import datetime


def generate_markdown(project_path, project_name, all_files, stats, include_structure=True, include_summary=True):
    """Generate complete markdown content"""
    
    lines = []
    
    # Header
    lines.append("# CodeToGPT Export\n")
    lines.append(f"## Project: {project_name}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Project Statistics
    lines.append("## 📊 Project Statistics\n")
    lines.append(f"- **Total Files:** {stats['total_files']}\n")
    lines.append(f"- **Total Folders:** {stats['total_folders']}\n")
    lines.append(f"- **Project Size:** {format_bytes(stats['total_size'])}\n\n")
    
    # File Type Statistics
    lines.append("## 📋 File Types\n")
    for ext, count in sorted(stats['file_types'].items()):
        lines.append(f"- {ext}: {count} files\n")
    lines.append("\n")
    
    # Directory Structure
    if include_structure:
        lines.append("---\n\n")
        lines.append("## 📁 Directory Structure\n\n")
        lines.append("```\n")
        lines.append(generate_tree(project_path))
        lines.append("```\n\n")
    
    # File Summary
    if include_summary:
        lines.append("---\n\n")
        lines.append("## 📑 File Summary\n\n")
        
        for file_info in sorted(all_files, key=lambda x: x['path']):
            lines.append(f"- **{file_info['path']}** ({format_bytes(file_info['size'])})\n")
        lines.append("\n")
    
    # File Contents
    lines.append("---\n\n")
    lines.append("## 📄 File Contents\n\n")
    
    for idx, file_info in enumerate(all_files, 1):
        lines.append(f"### File {idx}: {file_info['name']}\n")
        lines.append(f"**Path:** `{file_info['path']}`\n")
        lines.append(f"**Size:** {format_bytes(file_info['size'])}\n\n")
        
        # Try to read file content
        try:
            with open(file_info['full_path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Limit content for very large files
                if len(content) > 50000:
                    content = content[:50000] + f"\n\n... [File truncated - showing first 50KB of {format_bytes(file_info['size'])}] ...\n"
                
                # Determine language for syntax highlighting
                ext = Path(file_info['name']).suffix.lower()
                lang_map = {
                    '.kt': 'kotlin',
                    '.java': 'java',
                    '.dart': 'dart',
                    '.xml': 'xml',
                    '.gradle': 'gradle',
                    '.json': 'json',
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.sh': 'bash',
                    '.md': 'markdown'
                }
                lang = lang_map.get(ext, 'text')
                
                lines.append(f"```{lang}\n")
                lines.append(content)
                lines.append("\n```\n\n")
        
        except Exception as e:
            lines.append(f"```\n[Error reading file: {str(e)}]\n```\n\n")
    
    return ''.join(lines)


def generate_tree(root_path, prefix="", is_last=True, max_depth=10, current_depth=0):
    """Generate tree view of directory structure"""
    if current_depth >= max_depth:
        return ""
    
    lines = []
    items = []
    
    try:
        entries = sorted(os.listdir(root_path))
        
        # Filter ignored folders
        ignore_folders = {'build', '.gradle', '.idea', 'node_modules', '.git', '.dart_tool', '__pycache__'}
        entries = [e for e in entries if not (e.startswith('.') and e in ignore_folders)]
        
        for entry in entries:
            path = os.path.join(root_path, entry)
            if os.path.isdir(path):
                items.append((entry, True))
            else:
                if should_include_in_tree(entry):
                    items.append((entry, False))
    
    except PermissionError:
        return ""
    
    for idx, (item, is_dir) in enumerate(items):
        is_last_item = idx == len(items) - 1
        connector = "└── " if is_last_item else "├── "
        
        if is_dir:
            lines.append(f"{prefix}{connector}📁 {item}/\n")
            
            extension = "    " if is_last_item else "│   "
            sub_path = os.path.join(root_path, item)
            lines.append(generate_tree(sub_path, prefix + extension, is_last_item, max_depth, current_depth + 1))
        else:
            lines.append(f"{prefix}{connector}📄 {item}\n")
    
    return ''.join(lines)


def should_include_in_tree(filename):
    """Check if file should be included in tree view"""
    include_extensions = {'.kt', '.java', '.dart', '.xml', '.gradle', '.json', '.md', '.txt'}
    ext = Path(filename).suffix.lower()
    return ext in include_extensions


def format_bytes(bytes_val):
    """Convert bytes to human readable format"""
    if bytes_val == 0:
        return "0 Bytes"
    
    sizes = ['Bytes', 'KB', 'MB', 'GB']
    i = 0
    
    while bytes_val >= 1024 and i < len(sizes) - 1:
        bytes_val /= 1024.0
        i += 1
    
    return f"{bytes_val:.2f} {sizes[i]}"
