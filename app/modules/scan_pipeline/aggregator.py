from app.modules.trust_score.schemas import TrustScoreInput
from app.modules.ocr.schemas import OCRResult
from app.modules.fraud_intelligence.schemas import FraudMatchResult

class ResultAggregator:
    @staticmethod
    def normalize_to_trust_input(ocr: OCRResult, fraud: FraudMatchResult, metadata_anomalies: int) -> TrustScoreInput:
        """
        Translates raw modular outputs into the strict schema required by the Trust Score Engine.
        """
        
        # 1. Validate UTR (Basic deterministic check: 12 digits)
        utr = ocr.fields.upi_transaction_id
        is_utr_valid = bool(utr and len(utr) == 12 and utr.isdigit())
        
        # 2. Validate Amount
        amount = ocr.fields.payment_amount
        is_amount_valid = bool(amount and len(amount) > 0)
        
        # Assemble for Phase 4
        return TrustScoreInput(
            upi_transaction_id_valid=is_utr_valid,
            payment_amount_valid=is_amount_valid,
            fraud_fingerprint_match=fraud.fingerprint_match,
            fraud_match_confidence=fraud.match_confidence,
            
            metadata_anomalies_detected=metadata_anomalies, 
            layout_inconsistencies_detected=0, # Still stubbed
            ai_visual_flags=0 # Stubbed
        )
