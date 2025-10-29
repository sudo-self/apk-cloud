from flask import Flask, request, render_template_string, send_file, jsonify
import os
import subprocess
import tempfile
import shutil
import uuid
import requests
import threading

app = Flask(__name__)
BUILDS_DIR = "/app/builds"
os.makedirs(BUILDS_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>APK Builder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: #0f0f0f; 
            color: white; 
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        h1 { 
            text-align: center; 
            margin-bottom: 10px;
            color: #4CAF50;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #ccc;
        }
        input {
            width: 100%;
            padding: 12px;
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 5px;
            color: white;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #4CAF50;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .progress {
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: #4CAF50;
            width: 0%;
            transition: width 0.3s;
        }
        .status {
            text-align: center;
            margin: 10px 0;
            min-height: 24px;
        }
        .download-section {
            display: none;
            text-align: center;
            padding: 20px;
            background: #2a2a2a;
            border-radius: 5px;
            margin-top: 20px;
        }
        .download-btn {
            background: #2196F3;
            display: inline-block;
            padding: 12px 24px;
            text-decoration: none;
            color: white;
            border-radius: 5px;
            margin-top: 10px;
        }
        .download-btn:hover {
            background: #1976D2;
        }
        .error {
            color: #f44336;
            text-align: center;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 APK Builder</h1>
        <div class="subtitle">Convert websites to Android APK</div>
        
        <form id="buildForm">
            <div class="form-group">
                <label for="url">Website URL *</label>
                <input type="url" id="url" name="url" placeholder="https://example.com" required>
            </div>
            
            <div class="form-group">
                <label for="app_name">App Name *</label>
                <input type="text" id="app_name" name="app_name" placeholder="My App" value="WebApp" required>
            </div>
            
            <div class="form-group">
                <label for="icon_url">Icon URL (Optional)</label>
                <input type="url" id="icon_url" name="icon_url" placeholder="https://example.com/icon.png">
            </div>
            
            <button type="submit" id="buildBtn">BUILD APK</button>
        </form>
        
        <div class="progress" id="progressBar" style="display: none;">
            <div class="progress-bar" id="progressFill"></div>
        </div>
        
        <div class="status" id="status">Ready to build</div>
        <div class="error" id="error"></div>
        
        <div class="download-section" id="downloadSection">
            <h3>🎉 APK Ready!</h3>
            <p>Your Android app has been built successfully</p>
            <a href="#" class="download-btn" id="downloadLink">📲 DOWNLOAD APK</a>
        </div>
    </div>

    <script>
        document.getElementById('buildForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const buildBtn = document.getElementById('buildBtn');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const status = document.getElementById('status');
            const error = document.getElementById('error');
            const downloadSection = document.getElementById('downloadSection');
            
            buildBtn.disabled = true;
            buildBtn.textContent = 'Building...';
            progressBar.style.display = 'block';
            downloadSection.style.display = 'none';
            error.textContent = '';
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/build', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    status.textContent = 'Build completed!';
                    progressFill.style.width = '100%';
                    
                    // Show download section
                    const downloadLink = document.getElementById('downloadLink');
                    downloadLink.href = `/download/${result.filename}`;
                    downloadSection.style.display = 'block';
                } else {
                    throw new Error(result.error || 'Build failed');
                }
                
            } catch (err) {
                error.textContent = err.message;
                status.textContent = 'Build failed';
            } finally {
                buildBtn.disabled = false;
                buildBtn.textContent = 'BUILD APK';
            }
        });
        
        // Simulate progress updates
        function updateProgress() {
            const progressFill = document.getElementById('progressFill');
            const status = document.getElementById('status');
            const steps = [
                'Creating project...',
                'Downloading assets...', 
                'Building APK...',
                'Finalizing...'
            ];
            
            let progress = 0;
            steps.forEach((step, index) => {
                setTimeout(() => {
                    progress = ((index + 1) / steps.length) * 100;
                    progressFill.style.width = progress + '%';
                    status.textContent = step;
                }, index * 2000);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/build', methods=['POST'])
def build_apk():
    try:
        data = request.json
        url = data.get('url', '').strip()
        app_name = data.get('app_name', 'WebApp').strip()
        icon_url = data.get('icon_url', '').strip()
        
        if not url:
            return jsonify({'error': 'Website URL is required'}), 400
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Generate unique filename
        build_id = str(uuid.uuid4())[:8]
        apk_filename = f"{app_name.replace(' ', '_')}_{build_id}.apk"
        apk_path = os.path.join(BUILDS_DIR, apk_filename)
        
        # Build in background thread
        thread = threading.Thread(
            target=build_apk_thread,
            args=(url, app_name, icon_url, apk_path),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'Build started',
            'filename': apk_filename,
            'build_id': build_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def build_apk_thread(url: str, app_name: str, icon_url: str, apk_path: str):
    """Build APK in background thread"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate main.py
            main_py_content = f'''import flet as ft

def main(page: ft.Page):
    page.title = "{app_name}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    webview = ft.WebView(
        url="{url}",
        expand=True
    )
    page.add(webview)

ft.app(main)
'''
            
            with open(os.path.join(temp_dir, "main.py"), 'w') as f:
                f.write(main_py_content)
            
            # Create requirements.txt
            with open(os.path.join(temp_dir, "requirements.txt"), 'w') as f:
                f.write("flet\n")
            
            # Download icon if provided
            if icon_url:
                try:
                    response = requests.get(icon_url, timeout=30)
                    if response.status_code == 200:
                        assets_dir = os.path.join(temp_dir, "assets")
                        os.makedirs(assets_dir, exist_ok=True)
                        with open(os.path.join(assets_dir, "icon.png"), 'wb') as f:
                            f.write(response.content)
                except Exception as e:
                    print(f"Icon download failed: {e}")
            
            # Build APK
            os.chdir(temp_dir)
            result = subprocess.run(
                ['flet', 'build', 'apk', '--name', app_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Find and copy APK
                apk_source = find_apk_file(temp_dir)
                if apk_source:
                    shutil.copy2(apk_source, apk_path)
                    print(f"APK built successfully: {apk_path}")
                else:
                    print("APK file not found after build")
            else:
                print(f"Build failed: {result.stderr}")
                
    except Exception as e:
        print(f"Build error: {e}")

def find_apk_file(directory: str):
    """Find the built APK file"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.apk'):
                return os.path.join(root, file)
    return None

@app.route('/download/<filename>')
def download_file(filename):
    """Serve APK file for download"""
    file_path = os.path.join(BUILDS_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
