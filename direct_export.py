# direct_export.py - Direct folder export without browser

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
from file_scanner import scan_project_folder, get_project_stats
from markdown_generator import generate_markdown
from project_analyzer import get_project_name


def export_project(project_path):
    """Export project directly from folder path"""
    
    print(f"🚀 CodeToGPT - Direct Export\n")
    print(f"📁 Scanning: {project_path}\n")
    
    # Check if path exists
    if not os.path.exists(project_path):
        print(f"❌ Error: Folder not found: {project_path}")
        return
    
    # Get project info
    project_name = get_project_name(project_path)
    print(f"📦 Project: {project_name}")
    
    # Scan files
    print("🔍 Scanning files...")
    all_files = scan_project_folder(project_path)
    
    if not all_files:
        print("❌ No files found to export")
        return
    
    # Get stats
    stats = get_project_stats(all_files)
    print(f"✅ Found {stats['total_files']} files in {stats['total_folders']} folders")
    print(f"📊 Total size: {format_bytes(stats['total_size'])}")
    
    # Show file types
    print("\n📋 File types:")
    for ext, count in sorted(stats['file_types'].items()):
        print(f"   - {ext}: {count} files")
    
    # Generate markdown
    print("\n⚙️  Generating markdown...")
    markdown_content = generate_markdown(
        project_path=project_path,
        project_name=project_name,
        all_files=all_files,
        stats=stats,
        include_structure=True,
        include_summary=True
    )
    
    # Save to Downloads folder
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    filename = f"{project_name}-CodeToGPT.md"
    output_path = os.path.join(downloads_folder, filename)
    
    print(f"💾 Saving to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    file_size = os.path.getsize(output_path)
    print(f"\n✅ Success! Exported: {filename}")
    print(f"📦 File size: {format_bytes(file_size)}")
    print(f"📂 Location: {downloads_folder}")
    print(f"\n🎯 Next step: Upload this file to Perplexity AI!")
    
    # Open the file
    try:
        os.startfile(output_path)
        print(f"📄 Opening file...")
    except:
        pass


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


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  CodeToGPT - Direct Project Exporter")
    print("="*60 + "\n")
    
    # Check if path provided
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Ask for path
        print("Enter your project folder path:")
        print("Example: D:\\FlutterProjects\\emi_pro")
        print()
        project_path = input("Path: ").strip().strip('"')
    
    if project_path:
        export_project(project_path)
    else:
        print("❌ No path provided")
    
    print("\n" + "="*60)
    input("\nPress Enter to exit...")
