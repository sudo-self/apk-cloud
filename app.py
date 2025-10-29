from flask import Flask, request, render_template_string, send_file, jsonify
import os
import uuid
import json

app = Flask(__name__)

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
        .download-section {
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
            margin: 5px;
        }
        .instructions {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 14px;
        }
        code {
            background: #1a1a1a;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 APK Builder</h1>
        <div class="subtitle">Generate Android APK project files</div>
        
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
                <label for="package_name">Package Name *</label>
                <input type="text" id="package_name" name="package_name" placeholder="com.example.myapp" value="com.webapp.android" required>
            </div>
            
            <button type="submit">GENERATE PROJECT FILES</button>
        </form>
        
        <div class="download-section" id="downloadSection" style="display: none;">
            <h3>🎉 Project Files Ready!</h3>
            <p>Download the files and build locally:</p>
            <a href="#" class="download-btn" id="downloadMain">Download main.py</a>
            <a href="#" class="download-btn" id="downloadRequirements">Download requirements.txt</a>
            <a href="#" class="download-btn" id="downloadScript">Download build script</a>
        </div>

        <div class="instructions">
            <h4>📋 Build Instructions:</h4>
            <ol>
                <li>Download all project files above</li>
                <li>Install Flet: <code>pip install flet</code></li>
                <li>Run build script: <code>bash build_apk.sh</code></li>
                <li>Find APK in <code>build/apk/</code> directory</li>
            </ol>
        </div>
    </div>

    <script>
        document.getElementById('buildForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Generate main.py content
            const mainPy = `import flet as ft

def main(page: ft.Page):
    page.title = "${data.app_name}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # WebView loading your website
    webview = ft.WebView(
        url="${data.url}",
        expand=True,
        on_page_started=lambda _: print("Loading ${data.url}..."),
        on_page_ended=lambda _: print("Page loaded successfully")
    )
    
    page.add(webview)

if __name__ == "__main__":
    ft.app(main)
`;

            const requirements = `flet>=0.10.0`;

            const buildScript = `#!/bin/bash

echo "=== Building ${data.app_name} APK ==="

# Install Flet if not present
pip install flet

# Build the APK
flet build apk \\
    --name "${data.app_name}" \\
    --build-version "1.0.0"

echo "=== Build complete! ==="
echo "APK location: build/apk/"
`;

            // Create download links
            const mainBlob = new Blob([mainPy], { type: 'text/python' });
            const requirementsBlob = new Blob([requirements], { type: 'text/plain' });
            const scriptBlob = new Blob([buildScript], { type: 'text/x-shellscript' });

            document.getElementById('downloadMain').href = URL.createObjectURL(mainBlob);
            document.getElementById('downloadMain').download = 'main.py';
            
            document.getElementById('downloadRequirements').href = URL.createObjectURL(requirementsBlob);
            document.getElementById('downloadRequirements').download = 'requirements.txt';
            
            document.getElementById('downloadScript').href = URL.createObjectURL(scriptBlob);
            document.getElementById('downloadScript').download = 'build_apk.sh';

            // Show download section
            document.getElementById('downloadSection').style.display = 'block';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
