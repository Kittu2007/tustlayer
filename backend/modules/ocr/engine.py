import re
from PIL import Image
import io
import pytesseract
from backend.modules.ocr.schemas import ExtractedFields, OCRResult

class TesseractEngine:
    def __init__(self):
        # Regex patterns for deterministic hackathon extraction
        self.utr_pattern = re.compile(r'\b\d{12}\b')
        # Looks for currency symbols followed by numbers, handling some spaces
        self.amount_pattern = re.compile(r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)', re.IGNORECASE)

    def extract(self, image_bytes: bytes) -> OCRResult:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Basic preprocessing could go here (e.g., converting to grayscale)
            
            raw_text = pytesseract.image_to_string(image)
            
            fields = ExtractedFields()
            
            # Find UTR
            utr_match = self.utr_pattern.search(raw_text)
            if utr_match:
                fields.upi_transaction_id = utr_match.group(0)
                
            # Find Amount
            amount_match = self.amount_pattern.search(raw_text)
            if amount_match:
                fields.payment_amount = amount_match.group(1).replace(',', '')
                
            # Calculate naive confidence
            # If we found both a 12-digit UTR and an Amount, we are fairly confident.
            confidence = 0.0
            if fields.upi_transaction_id:
                confidence += 0.5
            if fields.payment_amount:
                confidence += 0.4
                
            # A little bump if we extracted any text at all
            if len(raw_text.strip()) > 10:
                confidence += 0.1

            return OCRResult(
                fields=fields,
                confidence_score=round(min(1.0, confidence), 2),
                used_fallback=False,
                raw_text=raw_text
            )
        except Exception as e:
            # If tesseract fails entirely (e.g. not installed), return 0 confidence
            print(f"Tesseract failed: {e}")
            return OCRResult(
                fields=ExtractedFields(),
                confidence_score=0.0,
                used_fallback=False
            )
