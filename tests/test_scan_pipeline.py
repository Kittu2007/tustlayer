import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.modules.scan_pipeline.schemas import FinalScanResponse
from app.modules.scan_pipeline.service import ScanPipelineService
from app.modules.ocr.schemas import OCRResult
from app.modules.fraud_intelligence.schemas import FraudMatchResult
from app.modules.trust_score.schemas import TrustScoreResult, RiskLevel

@pytest.mark.asyncio
async def test_successful_pipeline_execution():
    # 1. Mock the heavy underlying services so we don't actually hit APIs or Tesseract
    mock_ocr = AsyncMock()
    mock_ocr.extract_payment_proof.return_value = OCRResult(
        fields={"payment_amount": "₹500.00", "upi_transaction_id": "123456789012"},
        confidence_score=0.9,
        used_fallback=False
    )
    
    mock_fraud = AsyncMock()
    mock_fraud.scan_image.return_value = FraudMatchResult(
        fingerprint_match=False,
        match_confidence=0.0,
        match_count=0
    )
    
    # 2. Inject the mocks into the pipeline
    with patch('app.modules.scan_pipeline.service.get_ocr_service', return_value=mock_ocr), \
         patch('app.modules.scan_pipeline.service.get_fraud_intelligence_service', return_value=mock_fraud):
        
        service = ScanPipelineService()
        
        # We pass dummy bytes since the mocks will catch it
        response = await service.execute_full_scan(b"fake_image_bytes")
        
        # 3. Assertions
        assert response.success is True
        assert "OCR" in response.metadata.modules_executed
        
        # Valid amount and UTR + NO fraud = 100 Trust Score
        assert response.trust_score_data.trust_score == 100.0
        assert response.trust_score_data.risk_level == RiskLevel.LOW
        
        # Ensure underlying data is bubbled up for the frontend
        assert response.ocr_data.fields.payment_amount == "₹500.00"
        assert response.fraud_intelligence_data.fingerprint_match is False
