let currentProjectPath = null;
let currentProjectName = null;

// Drag & Drop functionality
const dropZone = document.getElementById('dropZone');
const folderInput = document.getElementById('folderInput');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    uploadProject(files);
});

folderInput.addEventListener('change', (e) => {
    const files = e.target.files;
    uploadProject(files);
});

function uploadProject(files) {
    if (files.length === 0) return;

    showLoading(true);
    hideMessages();

    const formData = new FormData();
    for (let file of files) {
        formData.append('files[]', file, file.webkitRelativePath || file.name);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || data.warning) {
            currentProjectPath = data.project_path;
            currentProjectName = data.project_name;
            
            displayProjectInfo(data.project_name, data.stats);
            showLoading(false);
            
            if (data.warning) {
                showError(data.warning);
            }
        } else {
            showError(data.error || 'Upload failed');
            showLoading(false);
        }
    })
    .catch(error => {
        showError('Upload error: ' + error.message);
        showLoading(false);
    });
}

function displayProjectInfo(projectName, stats) {
    document.getElementById('projectName').textContent = projectName;
    document.getElementById('totalFiles').textContent = stats.total_files;
    document.getElementById('totalFolders').textContent = stats.total_folders;
    document.getElementById('projectSize').textContent = formatBytes(stats.total_size);

    // Display file types
    const fileTypesDiv = document.getElementById('fileTypes');
    fileTypesDiv.innerHTML = '';
    
    for (const [ext, count] of Object.entries(stats.file_types)) {
        const badge = document.createElement('div');
        badge.className = 'file-type-badge';
        badge.textContent = `${ext}: ${count}`;
        fileTypesDiv.appendChild(badge);
    }

    document.getElementById('infoCard').style.display = 'block';
    document.getElementById('dropZone').style.display = 'none';
}


function generateAndDownload() {
    if (!currentProjectPath) {
        showError('No project selected');
        return;
    }

    const includeStructure = document.getElementById('includeStructure').checked;
    const includeSummary = document.getElementById('includeSummary').checked;

    document.getElementById('downloadBtn').disabled = true;
    showLoading(true);

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            project_path: currentProjectPath,
            project_name: currentProjectName,
            include_structure: includeStructure,
            include_summary: includeSummary
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            // Download the file
            window.location.href = `/download/${data.filename}`;
            
            showSuccess(`✅ Downloaded: ${data.filename}\n📤 Now upload to Perplexity AI!`);
            
            // Reset after 3 seconds
            setTimeout(() => {
                resetUI();
            }, 3000);
        } else {
            showError(data.error || 'Generation failed');
            document.getElementById('downloadBtn').disabled = false;
        }
    })
    .catch(error => {
        showError('Error: ' + error.message);
        showLoading(false);
        document.getElementById('downloadBtn').disabled = false;
    });
}


function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}


function showError(message) {
    const errorDiv = document.getElementById('errorMsg');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}


function showSuccess(message) {
    const successDiv = document.getElementById('successMsg');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
}


function hideMessages() {
    document.getElementById('errorMsg').style.display = 'none';
    document.getElementById('successMsg').style.display = 'none';
}


function resetUI() {
    currentProjectPath = null;
    currentProjectName = null;
    document.getElementById('infoCard').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('downloadBtn').disabled = false;
    hideMessages();
    folderInput.value = '';
}


function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Export from direct path
function exportFromPath() {
    const pathInput = document.getElementById('pathInput');
    const projectPath = pathInput.value.trim();
    
    if (!projectPath) {
        showError('Please enter a project folder path');
        return;
    }
    
    // Validate path format (basic check)
    if (!projectPath.includes(':') && !projectPath.startsWith('/')) {
        showError('Invalid path format. Example: D:\\FlutterProjects\\emi_pro');
        return;
    }
    
    showLoading(true);
    document.getElementById('loadingText').textContent = 'Exporting project...';
    hideMessages();
    
    // Send path to backend
    fetch('/export-path', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            project_path: projectPath 
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Export failed');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showLoading(false);
            showSuccess(`✅ Exported successfully: ${data.filename}`);
            
            // Trigger download
            setTimeout(() => {
                window.location.href = `/download/${data.filename}`;
                pathInput.value = ''; // Clear input
            }, 500);
        }
    })
    .catch(error => {
        showError(error.message);
        showLoading(false);
    });
}

// Allow Enter key in path input
document.addEventListener('DOMContentLoaded', function() {
    const pathInput = document.getElementById('pathInput');
    if (pathInput) {
        pathInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                exportFromPath();
            }
        });
    }
});
