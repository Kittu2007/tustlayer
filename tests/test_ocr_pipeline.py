import pytest
from app.modules.ocr.schemas import ExtractedFields, OCRResult
from app.modules.ocr.reconciliation import ReconciliationEngine

def test_reconciliation_logic():
    # Simulate a partial Tesseract read
    tesseract_fields = ExtractedFields(
        payment_amount="1000",
        upi_transaction_id=None, # Tesseract missed the UTR
        receiver_name=None
    )
    
    # Simulate a high-quality Vision LLM read
    vision_fields = {
        "amount": 1000.0,
        "upi_transaction_id": "123456789012",
        "receiver_name": "Rahul Kumar",
        "app_name": "Google Pay"
    }
    
    # Reconcile
    final_fields = ReconciliationEngine.reconcile(tesseract_fields, vision_fields)
    
    # Assertions
    assert final_fields.payment_amount == "1000" # Prioritized Tesseract for exact string
    assert final_fields.upi_transaction_id == "123456789012" # Filled in by Vision
    assert final_fields.receiver_name == "Rahul Kumar" # Filled in by Vision
    assert final_fields.payment_app_name == "Google Pay" # Filled in by Vision
