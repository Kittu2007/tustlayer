import base64
import json
import re
import time
from typing import Dict, List, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.ai_orchestrator import VisionProvider, ReasoningProvider


# Pydantic models for OCR response
class OCRField(BaseModel):
    label: str
    value: str
    confidence: Optional[float] = None

class OCRResponse(BaseModel):
    fields: List[OCRField]
    raw_text: Optional[str] = None


# Pydantic models for reasoning response
class ReasoningResponse(BaseModel):
    reasons: List[str]
    recommendations: List[str]


class NemotronOCRProvider(VisionProvider):
    """Vision provider using NVIDIA's Nemotron OCR model."""

    def __init__(self):
        self.api_url = f"{settings.NVIDIA_BASE_URL}/vision/ocr"
        self.model = settings.OCR_MODEL
        self.client = httpx.AsyncClient(timeout=10.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        start = time.time()
        print(f"[TRUSTLAYER-DEBUG] NVIDIA_API: Requesting OCR model '{self.model}'...")
        response = await self.client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        elapsed = int((time.time() - start) * 1000)
        print(f"[TRUSTLAYER-DEBUG] NVIDIA_API: Received response from OCR model in {elapsed}ms")
        return response.json()

    async def extract_fields(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract fields from an image using Nemotron OCR."""
        # Prepare the payload for the OCR model
        # Encode image bytes to base64 string as required by most APIs
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        payload = {
            "model": self.model,
            "input": {
                "image": image_base64
            }
        }

        try:
            result = await self._make_request(payload)
            # Parse and validate the response using Pydantic
            parsed = OCRResponse(**result)
            # Convert to the expected dictionary format
            fields_dict = {field.label: field.value for field in parsed.fields}
            if parsed.raw_text:
                fields_dict["_raw_text"] = parsed.raw_text
            print(f"[TRUSTLAYER-DEBUG] NemotronOCRProvider: Successfully parsed {len(fields_dict)} fields.")
            return fields_dict
        except (ValidationError, KeyError) as e:
            print("[TRUSTLAYER-DEBUG] NemotronOCRProvider: Validation error on strict JSON parsing. Attempting regex fallback extraction...")
            # Fallback parsing: try to extract JSON from the response text if possible
            if isinstance(result, dict):
                # Check for common fields where the AI response might be stored
                for field in ["generated_text", "text", "content", "message"]:
                    if field in result and isinstance(result[field], str):
                        extracted = self._extract_json_from_text(result[field])
                        if extracted:  # Only return if we actually found JSON
                            print("[TRUSTLAYER-DEBUG] NemotronOCRProvider: Regex fallback extraction succeeded.")
                            return extracted
            # If we still have no structured data, raise the original error
            print(f"[TRUSTLAYER-DEBUG] NemotronOCRProvider: Fallback extraction failed. Error: {e}")
            raise e

    async def detect_anomalies(self, image_bytes: bytes) -> List[str]:
        """Detect anomalies in an image using the OCR model (if supported) or return empty list."""
        # For now, we don't have an anomaly detection endpoint, so we return empty.
        # Alternatively, we could use the same OCR to look for suspicious patterns.
        return []

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Attempt to extract JSON from text using regex."""
        # Look for JSON-like patterns
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        # If no JSON found, return an empty dict or raise an error
        return {}


class QwenReasoningProvider(ReasoningProvider):
    """Reasoning provider using NVIDIA's Qwen model."""

    def __init__(self):
        self.api_url = f"{settings.NVIDIA_BASE_URL}/chat/completions"
        self.model = settings.QWEN_MODEL
        self.client = httpx.AsyncClient(timeout=10.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        start = time.time()
        print(f"[TRUSTLAYER-DEBUG] NVIDIA_API: Requesting reasoning model '{self.model}'...")
        response = await self.client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        elapsed = int((time.time() - start) * 1000)
        print(f"[TRUSTLAYER-DEBUG] NVIDIA_API: Received response from reasoning model in {elapsed}ms")
        return response.json()

    async def generate_reasons(self, context_data: Dict[str, Any]) -> List[str]:
        """Generate reasons for a given context using Qwen."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial risk analyst. Provide concise reasons for the risk assessment based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context: {json.dumps(context_data)}\nProvide a list of reasons for the risk assessment."
                }
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            print(f"[TRUSTLAYER-DEBUG] QwenReasoningProvider: Generated content: {content[:100]}...")
            return self._parse_reasoning_response(content)
        except (KeyError, IndexError) as e:
            print(f"[TRUSTLAYER-DEBUG] QwenReasoningProvider: KeyError/IndexError parsing JSON format. Using text extraction fallback.")
            # Fallback parsing
            return self._extract_reasons_from_text(str(result))

    async def generate_recommendations(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a given risk level and context using Qwen."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial risk analyst. Provide actionable recommendations based on the risk level and context."
                },
                {
                    "role": "user",
                    "content": f"Risk Level: {risk_level}\nContext: {json.dumps(context_data)}\nProvide a list of recommendations."
                }
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }

        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_recommendations_response(content)
        except (KeyError, IndexError) as e:
            return self._extract_recommendations_from_text(str(result))

    def _parse_reasoning_response(self, content: str) -> List[str]:
        """Parse the reasoning response content into a list of reasons."""
        # Try to parse as JSON first
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "reasons" in parsed:
                return parsed["reasons"] if isinstance(parsed["reasons"], list) else [str(parsed["reasons"])]
        except json.JSONDecodeError:
            pass
        # Fallback: split by lines or bullet points
        lines = content.split('\n')
        reasons = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('1.')):
                reasons.append(line.lstrip('-*. '))
            elif line and not reasons:
                reasons.append(line)
        return reasons if reasons else [content]

    def _parse_recommendations_response(self, content: str) -> List[str]:
        """Parse the recommendations response content into a list of recommendations."""
        return self._parse_reasoning_response(content)  # Reuse the same logic

    def _extract_reasons_from_text(self, text: str) -> List[str]:
        """Fallback to extract reasons from text."""
        # Simple extraction: look for lines that seem like reasons
        lines = text.split('\n')
        reasons = [line.strip() for line in lines if line.strip() and not line.startswith('{') and not line.endswith('}')]
        return reasons[:5]  # Limit to 5

    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """Fallback to extract recommendations from text."""
        return self._extract_reasons_from_text(text)


class PhiReasoningProvider(ReasoningProvider):
    """Reasoning provider using Microsoft's Phi model as fallback."""

    def __init__(self):
        self.api_url = f"{settings.NVIDIA_BASE_URL}/chat/completions"
        self.model = settings.FALLBACK_MODEL
        self.client = httpx.AsyncClient(timeout=10.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        response = await self.client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def generate_reasons(self, context_data: Dict[str, Any]) -> List[str]:
        """Generate reasons using Phi model."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial risk analyst. Provide concise reasons for the risk assessment."
                },
                {
                    "role": "user",
                    "content": f"Context: {json.dumps(context_data)}\nProvide reasons."
                }
            ],
            "temperature": 0.5,
            "max_tokens": 300
        }

        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_reasoning_response(content)
        except (KeyError, IndexError):
            return ["Phi model: Unable to generate reasons due to formatting issues."]

    async def generate_recommendations(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations using Phi model."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial risk analyst. Provide actionable recommendations."
                },
                {
                    "role": "user",
                    "content": f"Risk Level: {risk_level}\nContext: {json.dumps(context_data)}\nProvide recommendations."
                }
            ],
            "temperature": 0.5,
            "max_tokens": 300
        }

        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_recommendations_response(content)
        except (KeyError, IndexError):
            return ["Phi model: Unable to generate recommendations due to formatting issues."]

    def _parse_reasoning_response(self, content: str) -> List[str]:
        """Parse reasoning response."""
        lines = content.split('\n')
        reasons = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                reasons.append(line.lstrip('-*.0123456789. '))
            elif line and not reasons:
                reasons.append(line)
        return reasons if reasons else [content]

    def _parse_recommendations_response(self, content: str) -> List[str]:
        """Parse recommendations response."""
        return self._parse_reasoning_response(content)