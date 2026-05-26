from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# Input DTO combining results from previous phases
class TrustScoreInput(BaseModel):
    # Phase 3: OCR Inputs
    upi_transaction_id_valid: bool = Field(..., description="True if UTR is 12 digits and matches checksum")
    payment_amount_valid: bool = Field(..., description="True if amount matches expected transaction format")
    
    # Phase 2: Fraud Intelligence
    fraud_fingerprint_match: bool = Field(..., description="True if matched a known scam template")
    fraud_match_confidence: float = Field(default=0.0, description="Confidence of the template match")
    
    # Future Phase Inputs (Mocked for now)
    metadata_anomalies_detected: int = Field(default=0, description="Number of EXIF/compression anomalies")
    layout_inconsistencies_detected: int = Field(default=0, description="Number of UI layout flaws")
    ai_visual_flags: int = Field(default=0, description="Visual anomalies flagged by LLM")

class TrustScoreResult(BaseModel):
    trust_score: float = Field(..., ge=0.0, le=100.0, description="0 to 100 score. Higher is more trustworthy.")
    risk_level: RiskLevel
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    confidence_reasoning: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
