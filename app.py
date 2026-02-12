from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
from datetime import datetime
import io

# Add utils to path (Kept for internal dependencies support)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

# ✅ UPDATED IMPORTS
from utils.file_scanner import scan_project_folder, get_project_stats
from utils.markdown_generator import generate_markdown
from utils.project_analyzer import is_android_project, get_project_name

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None  # Unlimited upload

# Create exports folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_FOLDER = os.path.join(BASE_DIR, 'exports')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

os.makedirs(EXPORTS_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_project():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files[]')

        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_temp_folder = os.path.join(
            app.config['UPLOAD_FOLDER'], f'project_{timestamp}'
        )
        os.makedirs(project_temp_folder, exist_ok=True)

        file_count = 0

        for file in files:
            if file.filename:
                filepath = file.filename.replace('\\', '/')
                path_parts = filepath.split('/')
                secured_parts = [
                    secure_filename(part) if part else part
                    for part in path_parts
                ]
                safe_filepath = '/'.join(secured_parts)

                full_path = os.path.join(project_temp_folder, safe_filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                try:
                    file.save(full_path)
                    file_count += 1
                except Exception as e:
                    print(f"⚠ Could not save {filepath}: {e}")
                    continue

        project_name = get_project_name(project_temp_folder)
        all_files = scan_project_folder(project_temp_folder)
        stats = get_project_stats(all_files)

        return jsonify({
            'success': True,
            'project_name': project_name,
            'project_path': project_temp_folder,
            'stats': stats,
            'file_count': file_count
        }), 200

    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/generate', methods=['POST'])
def generate_export():
    try:
        data = request.json
        project_path = data.get('project_path')
        project_name = data.get('project_name')
        include_structure = data.get('include_structure', True)
        include_summary = data.get('include_summary', True)

        if not project_path or not os.path.exists(project_path):
            return jsonify({'error': 'Invalid project path'}), 400

        all_files = scan_project_folder(project_path)
        stats = get_project_stats(all_files)

        markdown_content = generate_markdown(
            project_path=project_path,
            project_name=project_name,
            all_files=all_files,
            stats=stats,
            include_structure=include_structure,
            include_summary=include_summary
        )

        filename = f"{project_name}-CodeToGPT.md"
        filepath = os.path.join(EXPORTS_FOLDER, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return jsonify({
            'success': True,
            'filename': filename,
            'size': len(markdown_content.encode('utf-8'))
        }), 200

    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(EXPORTS_FOLDER, secure_filename(filename))

        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/export-path', methods=['POST'])
def export_from_path():
    try:
        data = request.json
        project_path = data.get('project_path', '').strip()

        if not project_path:
            return jsonify({'error': 'No path provided'}), 400

        project_path = project_path.strip('"').strip("'")

        if not os.path.exists(project_path):
            return jsonify({'error': f'Path not found: {project_path}'}), 404

        if not os.path.isdir(project_path):
            return jsonify({'error': 'Path must be a directory'}), 400

        project_name = get_project_name(project_path)
        all_files = scan_project_folder(project_path)

        if not all_files:
            return jsonify({'error': 'No files found'}), 400

        stats = get_project_stats(all_files)

        markdown_content = generate_markdown(
            project_path=project_path,
            project_name=project_name,
            all_files=all_files,
            stats=stats,
            include_structure=True,
            include_summary=True
        )

        filename = f"{project_name}-CodeToGPT.md"
        filepath = os.path.join(EXPORTS_FOLDER, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return jsonify({
            'success': True,
            'filename': filename,
            'size': len(markdown_content.encode('utf-8')),
            'stats': stats
        }), 200

    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


# ✅ PRODUCTION SAFE RUN (Render Compatible)
if __name__ == '__main__':
    print("🚀 CodeToGPT is starting...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
