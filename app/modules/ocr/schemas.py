from pydantic import BaseModel, Field
from typing import Optional

class ExtractedFields(BaseModel):
    payment_amount: Optional[str] = Field(None, description="The extracted payment amount, e.g., '1000.00'")
    upi_transaction_id: Optional[str] = Field(None, description="12-digit UPI transaction reference number")
    receiver_name: Optional[str] = Field(None, description="Name of the person receiving the payment")
    timestamp: Optional[str] = Field(None, description="Date and time of the transaction")
    payment_app_name: Optional[str] = Field(None, description="App used (e.g., 'Google Pay', 'PhonePe')")

class OCRResult(BaseModel):
    fields: ExtractedFields
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence of the extraction")
    used_fallback: bool = Field(default=False, description="True if Vision AI was used to enhance Tesseract output")
    raw_text: Optional[str] = Field(None, description="Raw text extracted (mainly for debugging)")
