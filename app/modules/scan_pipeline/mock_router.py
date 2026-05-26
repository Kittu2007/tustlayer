from fastapi import APIRouter, HTTPException, status
from app.modules.scan_pipeline.schemas import FinalScanResponse, ScanMetadata
from app.modules.trust_score.schemas import TrustScoreResult, RiskLevel
from app.modules.ocr.schemas import OCRResult, ExtractedFields
from app.modules.fraud_intelligence.schemas import FraudMatchResult

router = APIRouter(prefix="/api/v1/mock", tags=["Mock Scenarios"])

@router.get("/scenario/{scenario_name}", response_model=FinalScanResponse)
async def get_mock_scenario(scenario_name: str):
    """
    Returns pre-calculated JSON payloads without hitting heavy ML models.
    Perfect for bulletproof live demos.
    Scenarios: perfect_receipt, fraud_template_match, photoshop_detected
    """
    
    if scenario_name == "perfect_receipt":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1200, modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=100.0,
                risk_level=RiskLevel.LOW,
                fraud_probability=0.0,
                confidence_reasoning=["All deterministic and visual checks passed successfully"],
                recommended_actions=["Payment proof appears authentic"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="123456789012", payment_amount="1000.00"),
                confidence_score=0.95, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(fingerprint_match=False, match_confidence=0.0, match_count=0)
        )
        
    elif scenario_name == "fraud_template_match":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1450, modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=0.0,
                risk_level=RiskLevel.HIGH,
                fraud_probability=0.99,
                confidence_reasoning=["Known scam template pattern detected"],
                recommended_actions=["Do not release goods or services", "Request live transfer verification or alternative proof"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="555555555555", payment_amount="50000.00"),
                confidence_score=0.88, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(
                fingerprint_match=True, match_confidence=0.98, match_count=1, fraud_type="Cloned Paytm Receipt"
            )
        )
        
    elif scenario_name == "photoshop_detected":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1300, modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=78.0,
                risk_level=RiskLevel.MEDIUM,
                fraud_probability=0.22,
                confidence_reasoning=["Image metadata indicates post-capture editing"],
                recommended_actions=["Verify payment receipt directly in your banking app"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="987654321098", payment_amount="250.00"),
                confidence_score=0.90, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(fingerprint_match=False, match_confidence=0.0, match_count=0)
        )
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock scenario not found.")
