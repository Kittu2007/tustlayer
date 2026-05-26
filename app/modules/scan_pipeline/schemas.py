from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time

from app.modules.ocr.schemas import OCRResult
from app.modules.fraud_intelligence.schemas import FraudMatchResult
from app.modules.trust_score.schemas import TrustScoreResult

class ScanMetadata(BaseModel):
    execution_time_ms: int
    modules_executed: list[str]

class FinalScanResponse(BaseModel):
    """
    Cinematic Monolithic Payload
    Designed for frontend progressive disclosure.
    """
    success: bool = True
    metadata: ScanMetadata
    
    # Core Results
    trust_score_data: TrustScoreResult
    
    # Supporting Evidence
    ocr_data: OCRResult
    fraud_intelligence_data: FraudMatchResult

    # Session & Rate Limit Context
    anonymous_session_id: Optional[str] = None
    remaining_scans: int = Field(-1, description="Scans remaining for guest, or -1 if authenticated")

