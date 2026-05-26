from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="TrustLayer AI - Startup Diagnostic Hello World")

@app.get("/{path:path}", response_class=HTMLResponse)
async def home(path: str):
    return HTMLResponse(content="""
    <html>
    <head>
        <title>TrustLayer AI - Live Diagnostic</title>
        <style>
            body { font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 3rem; text-align: center; }
            h1 { color: #3b82f6; }
        </style>
    </head>
    <body>
        <h1>TrustLayer AI - Diagnostic Hello World is LIVE!</h1>
        <p>Vercel's Python serverless runtime is running perfectly and successfully.</p>
    </body>
    </html>
    """)
