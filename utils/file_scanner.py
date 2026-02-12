import os
from pathlib import Path
from collections import defaultdict


IGNORE_FOLDERS = {
    'build', '.gradle', '.idea', 'node_modules', '.git',
    '.dart_tool', '__pycache__', '.vscode', '.vs', 'dist',
    'bin', 'obj', '.metadata', '.cxx', '.kotlin',
    'intermediates', 'generated', 'outputs'
}


IGNORE_FILES = {
    '*.apk', '*.jar', '*.class', '*.pyc', '*.o', '*.so',
    '.DS_Store', 'Thumbs.db', '*.iml', '*.lock'
}


INCLUDE_EXTENSIONS = {
    '.kt', '.java', '.dart', '.xml', '.gradle', '.json',
    '.properties', '.md', '.txt', '.yml', '.yaml', '.sh',
    '.bat', '.gradle.kts', '.toml', '.lock', '.pubspec'
}



def should_ignore_folder(folder_name):
    """Check if folder should be ignored"""
    # Fix: Changed AND to OR
    if folder_name.startswith('.') or folder_name in IGNORE_FOLDERS:
        return True
    
    # Ignore build-related folders
    if 'build' in folder_name.lower() or 'cache' in folder_name.lower():
        return True
    
    return False



def should_include_file(filename):
    """Check if file should be included"""
    if any(filename.endswith(pattern.replace('*', '')) for pattern in IGNORE_FILES):
        return False
    
    ext = Path(filename).suffix.lower()
    return ext in INCLUDE_EXTENSIONS or ext == ''



def scan_project_folder(root_path):
    """Recursively scan project folder and return all files"""
    all_files = []
    
    try:
        for root, dirs, files in os.walk(root_path):
            # Remove ignored folders (in-place modification)
            dirs[:] = [d for d in dirs if not should_ignore_folder(d)]
            
            for file in files:
                if should_include_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_path)
                    
                    try:
                        size = os.path.getsize(file_path)
                        
                        # Skip very large files (>10MB)
                        if size > 10 * 1024 * 1024:
                            continue
                        
                        all_files.append({
                            'path': rel_path,
                            'full_path': file_path,
                            'size': size,
                            'name': file
                        })
                    except Exception as e:
                        print(f"⚠️  Error reading {file}: {e}")
                        pass
    
    except Exception as e:
        print(f"❌ Error scanning folder: {e}")
    
    return all_files



def get_project_stats(all_files):
    """Calculate statistics from file list"""
    stats = {
        'total_files': len(all_files),
        'total_size': sum(f['size'] for f in all_files),
        'total_folders': len(set(os.path.dirname(f['path']) for f in all_files)),
        'file_types': defaultdict(int)
    }
    
    for file in all_files:
        ext = Path(file['name']).suffix.lower() or 'no-extension'
        stats['file_types'][ext] += 1
    
    return dict(stats)
