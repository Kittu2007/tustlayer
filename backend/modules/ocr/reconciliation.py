from backend.modules.ocr.schemas import ExtractedFields

class ReconciliationEngine:
    @staticmethod
    def reconcile(tesseract_fields: ExtractedFields, vision_fields: dict) -> ExtractedFields:
        """
        Merges deterministic Tesseract fields with Vision LLM fallback fields.
        Prioritizes Vision LLM for complex fields (names, apps, timestamps),
        but respects Tesseract for rigid IDs if Vision hallucinated them.
        """
        final_fields = ExtractedFields()
        
        # Merge UTR
        # If tesseract found it, trust tesseract. Otherwise trust vision.
        if tesseract_fields.upi_transaction_id:
            final_fields.upi_transaction_id = tesseract_fields.upi_transaction_id
        else:
            final_fields.upi_transaction_id = vision_fields.get("upi_transaction_id")
            
        # Merge Amount
        if tesseract_fields.payment_amount:
            final_fields.payment_amount = tesseract_fields.payment_amount
        else:
            final_fields.payment_amount = str(vision_fields.get("amount", ""))

        # Merge Complex Fields (Vision is usually better at this)
        final_fields.receiver_name = vision_fields.get("receiver_name") or tesseract_fields.receiver_name
        final_fields.timestamp = vision_fields.get("timestamp") or tesseract_fields.timestamp
        final_fields.payment_app_name = vision_fields.get("app_name") or tesseract_fields.payment_app_name
        
        return final_fields
