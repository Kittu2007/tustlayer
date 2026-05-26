import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
