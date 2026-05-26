import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.modules.scan_pipeline.session import _in_memory_sessions

@pytest.fixture(autouse=True)
def clear_sessions():
    _in_memory_sessions.clear()

def test_guest_session_generation():
    client = TestClient(app)
    # Mock OCR and Fraud services so we don't call external ML models
    with patch('app.modules.scan_pipeline.service.get_ocr_service') as mock_ocr, \
         patch('app.modules.scan_pipeline.service.get_fraud_intelligence_service') as mock_fraud:
        
        mock_ocr.return_value.executor.ocr_service.extract_payment_proof = AsyncMock()
        mock_fraud.return_value.executor.fraud_service.scan_image = AsyncMock()
        
        # Call execute endpoint without headers
        response = client.post(
            "/api/v1/scan/execute",
            files={"file": ("test.png", b"fake_bytes", "image/png")}
        )
        
        assert response.status_code == 200
        json_data = response.json()
        assert "anonymous_session_id" in json_data
        assert json_data["anonymous_session_id"] is not None
        assert json_data["remaining_scans"] == 4  # First scan, 5 - 1 = 4 remaining
        
        # Verify custom response headers
        assert "X-Anonymous-Session-ID" in response.headers
        assert response.headers["X-Remaining-Scans"] == "4"

def test_guest_session_rate_limit():
    client = TestClient(app)
    # Mock services
    with patch('app.modules.scan_pipeline.service.get_ocr_service') as mock_ocr, \
         patch('app.modules.scan_pipeline.service.get_fraud_intelligence_service') as mock_fraud:
        
        mock_ocr.return_value.executor.ocr_service.extract_payment_proof = AsyncMock()
        mock_fraud.return_value.executor.fraud_service.scan_image = AsyncMock()
        
        session_id = "test-session-123"
        headers = {"X-Anonymous-Session-ID": session_id}
        
        # Trigger 5 scans (limit is 5)
        for i in range(5):
            response = client.post(
                "/api/v1/scan/execute",
                files={"file": ("test.png", b"fake_bytes", "image/png")},
                headers=headers
            )
            assert response.status_code == 200
            assert response.headers["X-Remaining-Scans"] == str(4 - i)
            
        # The 6th scan should trigger 429
        response = client.post(
            "/api/v1/scan/execute",
            files={"file": ("test.png", b"fake_bytes", "image/png")},
            headers=headers
        )
        assert response.status_code == 429
        assert "limit exceeded" in response.json()["detail"]

def test_authenticated_user_bypass():
    client = TestClient(app)
    with patch('app.modules.scan_pipeline.service.get_ocr_service') as mock_ocr, \
         patch('app.modules.scan_pipeline.service.get_fraud_intelligence_service') as mock_fraud, \
         patch('app.core.security.verify_token', return_value={"uid": "auth-user"}):
        
        mock_ocr.return_value.executor.ocr_service.extract_payment_proof = AsyncMock()
        mock_fraud.return_value.executor.fraud_service.scan_image = AsyncMock()
        
        headers = {"Authorization": "Bearer valid_token"}
        
        # Authenticated users should have -1 remaining scans (unlimited)
        for _ in range(7):
            response = client.post(
                "/api/v1/scan/execute",
                files={"file": ("test.png", b"fake_bytes", "image/png")},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["remaining_scans"] == -1
            assert response.headers["X-Remaining-Scans"] == "-1"
