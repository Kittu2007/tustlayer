import sys
import os
import traceback

error_traceback = None
app = None

try:
    # Safely get current file path with NameError fallback
    try:
        current_file = __file__
    except NameError:
        current_file = os.path.join(os.getcwd(), "api", "index.py")
        
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(current_file)))
    if project_root not in sys.path:
        sys.path.append(project_root)
        
    from backend.main import app as real_app
    app = real_app
except Exception as e:
    error_traceback = traceback.format_exc()
    print(f"Error on startup: {error_traceback}")

if app is None:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(title="TrustLayer AI - Startup Error Diagnoser")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def diagnose_error(path: str):
        return HTMLResponse(content=f"""
        <html>
        <head>
            <title>TrustLayer AI - Startup Diagnosis</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 2rem; }}
                h1 {{ color: #f43f5e; }}
                pre {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; overflow-x: auto; color: #fda4af; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.5; }}
            </style>
        </head>
        <body>
            <h1>TrustLayer AI - Startup Diagnosis Report</h1>
            <p>An exception occurred during module import / startup initialization on Vercel:</p>
            <pre>{error_traceback}</pre>
        </body>
        </html>
        """)
