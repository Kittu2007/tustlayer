from backend.modules.ocr.schemas import OCRResult
from backend.modules.ocr.engine import TesseractEngine
from backend.modules.ocr.reconciliation import ReconciliationEngine
from backend.core.ai_orchestrator import AIOrchestrator
from backend.integrations.nvidia_client import NemotronOCRProvider

class OCRService:
    def __init__(self):
        self.tesseract = TesseractEngine()
        # Initialize the AI fallback orchestrator with Nemotron (NVIDIA NIM)
        self.ai_orchestrator = AIOrchestrator(
            primary=NemotronOCRProvider()
        )
        self.reconciliation = ReconciliationEngine()

    async def extract_payment_proof(self, image_bytes: bytes) -> OCRResult:
        """
        Runs deterministic OCR. If confidence is low, uses AI Vision to enhance.
        """
        # 1. Deterministic Extraction
        tesseract_result = self.tesseract.extract(image_bytes)
        
        # 2. Check Confidence
        # For hackathon MVP, if confidence < 0.6, we trigger the fallback
        print(f"[TRUSTLAYER-DEBUG] OCRService: Deterministic Tesseract confidence is {tesseract_result.confidence_score}.")
        if tesseract_result.confidence_score >= 0.6:
            print("[TRUSTLAYER-DEBUG] OCRService: Confidence is sufficient. Bypassing AI Vision fallback.")
            return tesseract_result
            
        print(f"[TRUSTLAYER-DEBUG] OCRService: Confidence is low ({tesseract_result.confidence_score}). Triggering Nemotron AI Vision fallback...")
        
        # 3. AI Fallback
        try:
            vision_fields = await self.ai_orchestrator.extract_with_fallback(image_bytes)
            
            # 4. Reconciliation
            final_fields = self.reconciliation.reconcile(
                tesseract_fields=tesseract_result.fields,
                vision_fields=vision_fields
            )
            
            # Return updated result
            return OCRResult(
                fields=final_fields,
                confidence_score=0.95, # Assuming AI fallback succeeded nicely
                used_fallback=True,
                raw_text=tesseract_result.raw_text # Keep original raw text for auditing
            )
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] OCRService: Fallback vision AI completely failed: {e}")
            # Return whatever Tesseract got if AI fails entirely
            return tesseract_result

def get_ocr_service() -> OCRService:
    return OCRService()
