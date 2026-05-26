import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from tenacity import RetryError

from app.integrations.nvidia_client import (
    NemotronOCRProvider,
    QwenReasoningProvider,
    PhiReasoningProvider,
    OCRResponse,
    ReasoningResponse,
)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for the NVIDIA client."""
    monkeypatch.setattr("app.integrations.nvidia_client.settings.NVIDIA_API_KEY", "test-key")
    monkeypatch.setattr("app.integrations.nvidia_client.settings.NVIDIA_BASE_URL", "https://test.api.com/v1")
    monkeypatch.setattr("app.integrations.nvidia_client.settings.OCR_MODEL", "test-ocr-model")
    monkeypatch.setattr("app.integrations.nvidia_client.settings.QWEN_MODEL", "test-qwen-model")
    monkeypatch.setattr("app.integrations.nvidia_client.settings.FALLBACK_MODEL", "test-phi-model")


@pytest.mark.asyncio
async def test_nemotron_ocr_success(mock_settings):
    """Test successful OCR extraction."""
    provider = NemotronOCRProvider()
    # Mock response matching what NVIDIA's Nemotron OCR might return
    mock_response = {
        "results": [
            {
                "label": "amount",
                "value": "1000",
                "confidence": 0.95
            },
            {
                "label": "status", 
                "value": "success",
                "confidence": 0.9
            }
        ],
        "raw_text": "Amount: 1000\nStatus: success"
    }

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = mock_response

        result = await provider.extract_fields(b"fake image bytes")

        # Check that we got the expected fields
        assert result["amount"] == "1000"
        assert result["status"] == "success"
        assert result["_raw_text"] == "Amount: 1000\nStatus: success"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_nemotron_ocr_malformed_json_fallback(mock_settings):
    """Test fallback parsing when AI returns malformed JSON."""
    provider = NemotronOCRProvider()
    # Simulate a response where the JSON is embedded in text (common with LLMs)
    mock_response = {
        "generated_text": 'Here is the OCR result:\n\n```json\n{"amount": "2000", "status": "failure"}\n```\n\nHope this helps!'
    }

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = mock_response

        result = await provider.extract_fields(b"fake image bytes")

        # The fallback should extract the JSON from the text
        assert result.get("amount") == "2000"
        assert result.get("status") == "failure"


@pytest.mark.asyncio
async def test_nemotron_ocr_timeout_retry(mock_settings):
    """Test timeout triggers retry and eventually fails."""
    provider = NemotronOCRProvider()

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(RetryError):
            await provider.extract_fields(b"fake image bytes")

        # Should have retried 3 times (initial + 2 retries)
        assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_qwen_reasoning_success(mock_settings):
    """Test successful reasoning generation."""
    provider = QwenReasoningProvider()
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "reasons": ["High amount", "Unknown merchant"],
                        "recommendations": ["Verify identity", "Limit transaction"]
                    })
                }
            }
        ]
    }

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = mock_response

        reasons = await provider.generate_reasons({"amount": 5000})
        recommendations = await provider.generate_recommendations("high", {"amount": 5000})

        assert reasons == ["High amount", "Unknown merchant"]
        assert recommendations == ["Verify identity", "Limit transaction"]
        assert mock_post.call_count == 2


@pytest.mark.asyncio
async def test_qwen_reasoning_malformed_json_fallback(mock_settings):
    """Test fallback parsing for reasoning when JSON is malformed."""
    provider = QwenReasoningProvider()
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "- High amount\n- Unknown merchant\n\nRecommendations:\n- Verify identity\n- Limit transaction"
                }
            }
        ]
    }

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = mock_response

        reasons = await provider.generate_reasons({"amount": 5000})
        recommendations = await provider.generate_recommendations("high", {"amount": 5000})

        # The fallback parsing should extract lines starting with '-'
        assert "High amount" in reasons
        assert "Unknown merchant" in reasons
        assert "Verify identity" in recommendations
        assert "Limit transaction" in recommendations


@pytest.mark.asyncio
async def test_phi_reasoning_success(mock_settings):
    """Test Phi reasoning provider."""
    provider = PhiReasoningProvider()
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "- Suspicious pattern\n- High risk location"
                }
            }
        ]
    }

    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = mock_response

        reasons = await provider.generate_reasons({"amount": 3000})
        assert reasons == ["Suspicious pattern", "High risk location"]


if __name__ == "__main__":
    pytest.main([__file__])