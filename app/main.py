import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.modules.fraud_intelligence.router import router as fraud_intelligence_router
from app.modules.ocr.router import router as ocr_router
from app.modules.trust_score.router import router as trust_score_router
from app.modules.scan_pipeline.router import router as scan_pipeline_router
from app.modules.scan_pipeline.mock_router import router as mock_router

app = FastAPI(
    title="TrustLayer AI API",
    description="The Trust Verification Layer for Digital Payments",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fraud_intelligence_router)
app.include_router(ocr_router)
app.include_router(trust_score_router)
app.include_router(scan_pipeline_router)
app.include_router(mock_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TrustLayer AI"}

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TrustLayer AI - Payment Proof Forensics</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #090D16;
                --card-bg: rgba(17, 24, 39, 0.7);
                --card-border: rgba(255, 255, 255, 0.08);
                --primary: #3B82F6;
                --primary-glow: rgba(59, 130, 246, 0.3);
                --accent: #6366F1;
                --accent-glow: rgba(99, 102, 241, 0.3);
                --success: #10B981;
                --success-glow: rgba(16, 185, 129, 0.2);
                --text: #F3F4F6;
                --text-muted: #9CA3AF;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            body {
                background-color: var(--bg);
                color: var(--text);
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }

            body::before, body::after {
                content: '';
                position: absolute;
                width: 400px;
                height: 400px;
                border-radius: 50%;
                filter: blur(120px);
                z-index: -1;
                opacity: 0.15;
            }
            body::before {
                background: var(--primary);
                top: -100px;
                right: -100px;
                animation: float 10s ease-in-out infinite alternate;
            }
            body::after {
                background: var(--accent);
                bottom: -100px;
                left: -100px;
                animation: float 10s ease-in-out infinite alternate-reverse;
            }

            @keyframes float {
                0% { transform: translate(0, 0) scale(1); }
                100% { transform: translate(50px, 50px) scale(1.2); }
            }

            header {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem 1rem;
                width: 100%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 700;
                font-size: 1.25rem;
                background: linear-gradient(135deg, #FFF 0%, #93C5FD 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .logo-shield {
                width: 24px;
                height: 24px;
                background: var(--primary);
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                box-shadow: 0 0 10px var(--primary-glow);
            }

            .status-badge {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                color: var(--success);
                padding: 0.35rem 0.85rem;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 500;
                box-shadow: 0 0 15px var(--success-glow);
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background-color: var(--success);
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }

            @keyframes pulse {
                0% { opacity: 0.4; }
                50% { opacity: 1; }
                100% { opacity: 0.4; }
            }

            main {
                max-width: 1200px;
                margin: 0 auto;
                padding: 1rem 1rem 3rem 1rem;
                width: 100%;
                display: grid;
                grid-template-columns: 1.2fr 1fr;
                gap: 2.5rem;
                align-items: start;
            }

            @media (max-width: 968px) {
                main {
                    grid-template-columns: 1fr;
                }
            }

            .hero-section h1 {
                font-size: 3rem;
                font-weight: 800;
                line-height: 1.15;
                margin-bottom: 1rem;
                letter-spacing: -0.03em;
                background: linear-gradient(135deg, #FFFFFF 30%, #93C5FD 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-section p {
                color: var(--text-muted);
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }

            .stack-info {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1rem;
                margin-bottom: 2rem;
            }

            .stack-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                backdrop-filter: blur(12px);
            }

            .stack-card h4 {
                font-size: 0.75rem;
                color: var(--text-muted);
                text-transform: uppercase;
                margin-bottom: 0.35rem;
                letter-spacing: 0.05em;
            }

            .stack-card p {
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--text);
                margin: 0;
            }

            .upload-card {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
            }

            .upload-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent);
            }

            .dropzone {
                border: 2px dashed rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 3rem 1.5rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255, 255, 255, 0.01);
            }

            .dropzone:hover, .dropzone.highlight {
                border-color: var(--primary);
                background: rgba(59, 130, 246, 0.05);
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
            }

            .dropzone svg {
                width: 48px;
                height: 48px;
                margin-bottom: 1rem;
                stroke: var(--text-muted);
                transition: stroke 0.3s ease;
            }

            .dropzone:hover svg, .dropzone.highlight svg {
                stroke: var(--primary);
            }

            .dropzone p {
                font-size: 0.95rem;
                color: var(--text-muted);
            }

            .dropzone span {
                color: var(--text);
                font-weight: 600;
            }

            .file-input {
                display: none;
            }

            .btn {
                width: 100%;
                background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
                border: none;
                border-radius: 12px;
                color: white;
                padding: 1rem;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 1.5rem;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            }

            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
                box-shadow: none !important;
            }

            .preview-container {
                margin-top: 1.5rem;
                display: none;
            }

            .preview-img {
                width: 100%;
                max-height: 200px;
                object-fit: contain;
                border-radius: 8px;
                border: 1px solid var(--card-border);
            }

            .results-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 1.5rem;
                backdrop-filter: blur(12px);
                max-height: 580px;
                display: flex;
                flex-direction: column;
            }

            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid var(--card-border);
            }

            .results-title {
                font-size: 1rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .json-viewer {
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--card-border);
                border-radius: 8px;
                padding: 1rem;
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.85rem;
                color: #34D399;
                overflow-y: auto;
                flex-grow: 1;
                white-space: pre-wrap;
                line-height: 1.4;
            }

            .placeholder-text {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: var(--text-muted);
                text-align: center;
                padding: 3rem 1rem;
            }

            .placeholder-text svg {
                width: 64px;
                height: 64px;
                stroke: rgba(255, 255, 255, 0.1);
                margin-bottom: 1rem;
            }

            .loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                gap: 1rem;
            }

            .spinner {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(59, 130, 246, 0.1);
                border-radius: 50%;
                border-top-color: var(--primary);
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                100% { transform: rotate(360deg); }
            }

            footer {
                text-align: center;
                padding: 2rem;
                font-size: 0.85rem;
                color: var(--text-muted);
                border-top: 1px solid var(--card-border);
                margin-top: auto;
            }

            footer a {
                color: var(--primary);
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">
                <div class="logo-shield"></div>
                TrustLayer AI
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                API Active
            </div>
        </header>

        <main>
            <div class="hero-section">
                <h1>Payment Proof Forensics</h1>
                <p>An advanced deterministic Trust Score and multi-model AI reasoning engine verifying digital transactions against visual forging, tampering, and double-spend fraud.</p>
                
                <div class="stack-info">
                    <div class="stack-card">
                        <h4>OCR Engine</h4>
                        <p>Nemotron-VL</p>
                    </div>
                    <div class="stack-card">
                        <h4>Reasoning LLM</h4>
                        <p>Qwen-3.5-122B</p>
                    </div>
                    <div class="stack-card">
                        <h4>Persistence</h4>
                        <p>Supabase</p>
                    </div>
                </div>

                <div class="upload-card">
                    <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                        </svg>
                        <p><span>Click to upload</span> or drag and drop</p>
                        <p style="font-size: 0.75rem; margin-top: 0.25rem;">Supports PNG, JPG, JPEG</p>
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept="image/*" onchange="handleFileSelect(event)" />
                    
                    <div class="preview-container" id="previewContainer">
                        <img src="" class="preview-img" id="previewImg" alt="Preview" />
                    </div>

                    <button class="btn" id="scanBtn" onclick="runForensicScan()" disabled>Execute Forensic Scan</button>
                </div>
            </div>

            <div class="results-card">
                <div class="results-header">
                    <div class="results-title">
                        <svg style="width: 20px; height: 20px; fill: var(--primary);" viewBox="0 0 24 24">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2zm0-4H7V7h10v2zm0 8H7v-2h10v2z"/>
                        </svg>
                        Analysis Report
                    </div>
                    <span id="timingBadge" style="font-size: 0.8rem; color: var(--text-muted); font-weight: 500;"></span>
                </div>
                
                <div class="json-viewer" id="outputConsole">
                    <div class="placeholder-text" id="placeholderText">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <p>Upload a screenshot and execute scan to populate forensic payload.</p>
                    </div>
                </div>
            </div>
        </main>

        <footer>
            <p>Built for the Hackathon. Powered by <a href="https://build.nvidia.com" target="_blank">NVIDIA NIMs</a> & <a href="https://supabase.com" target="_blank">Supabase</a>.</p>
        </footer>

        <script>
            let selectedFile = null;

            const dropzone = document.getElementById('dropzone');
            const fileInput = document.getElementById('fileInput');

            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            // Toggle highlight styles when item is dragged over the zone
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.add('highlight'), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.remove('highlight'), false);
            });

            // Handle dropped files
            dropzone.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length) {
                    fileInput.files = files;
                    handleFile(files[0]);
                }
            }

            function handleFileSelect(event) {
                const file = event.target.files[0];
                if (file) {
                    handleFile(file);
                }
            }

            function handleFile(file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('previewContainer').style.display = 'block';
                    document.getElementById('scanBtn').disabled = false;
                };
                reader.readAsDataURL(file);
            }

            async function runForensicScan() {
                if (!selectedFile) return;

                const btn = document.getElementById('scanBtn');
                const consoleEl = document.getElementById('outputConsole');
                const timingBadge = document.getElementById('timingBadge');
                
                btn.disabled = true;
                btn.innerText = "Analyzing...";
                consoleEl.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">Running Multimodal OCR & Fraud Verification...</p>
                    </div>
                `;
                timingBadge.innerText = "";

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const start = performance.now();
                    const response = await fetch('/api/v1/scan/execute', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Server Error ${response.status}: ${await response.text()}`);
                    }

                    const data = await response.json();
                    const elapsed = Math.round(performance.now() - start);
                    
                    timingBadge.innerText = `Scan Completed in ${elapsed}ms`;
                    consoleEl.innerHTML = JSON.stringify(data, null, 2);
                    consoleEl.style.color = "#34D399"; // Success green
                } catch (error) {
                    consoleEl.innerHTML = \`Error: \${error.message}\`;
                    consoleEl.style.color = "#EF4444"; // Error red
                    timingBadge.innerText = "Scan Failed";
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Execute Forensic Scan";
                }
            }
        </script>
    </body>
    </html>
    """

