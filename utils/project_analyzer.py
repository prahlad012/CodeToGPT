import os
from pathlib import Path


def is_android_project(folder_path):
    """Check if folder contains Android project markers"""
    markers = ['AndroidManifest.xml', 'build.gradle', 'settings.gradle']
    
    for root, dirs, files in os.walk(folder_path):
        if any(marker in files for marker in markers):
            return True
    
    return False


def get_project_name(folder_path):
    """Extract project name from folder"""
    basename = os.path.basename(folder_path)
    
    # Remove timestamp if present (project_YYYYMMDD_HHMMSS)
    if '_' in basename and basename.split('_')[0] == 'project':
        return 'android_project'
    
    return basename if basename else 'unknown_project'


def get_file_extension_category(ext):
    """Categorize file by extension"""
    categories = {
        'kotlin': ['.kt'],
        'java': ['.java'],
        'dart': ['.dart'],
        'xml': ['.xml'],
        'json': ['.json'],
        'gradle': ['.gradle', '.gradle.kts'],
        'documentation': ['.md', '.txt'],
        'config': ['.properties', '.yml', '.yaml', '.toml'],
        'other': []
    }
    
    ext_lower = ext.lower()
    for category, extensions in categories.items():
        if ext_lower in extensions:
            return category
    
    return 'other'
