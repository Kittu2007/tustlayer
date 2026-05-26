from backend.modules.trust_score.schemas import TrustScoreInput
from backend.modules.ocr.schemas import OCRResult
from backend.modules.fraud_intelligence.schemas import FraudMatchResult
from backend.modules.app_forensics.schemas import AppForensicsResult

class ResultAggregator:
    @staticmethod
    def normalize_to_trust_input(
        ocr: OCRResult, 
        fraud: FraudMatchResult, 
        metadata_anomalies: int,
        app_forensics: AppForensicsResult
    ) -> TrustScoreInput:
        """
        Translates raw modular outputs into the strict schema required by the Trust Score Engine.
        """
        
        # 1. Validate UTR (Basic deterministic check: 12 digits)
        utr = ocr.fields.upi_transaction_id
        is_utr_valid = bool(utr and len(utr) == 12 and utr.isdigit())
        
        # 2. Validate Amount
        amount = ocr.fields.payment_amount
        is_amount_valid = bool(amount and len(amount) > 0)
        
        # 3. Dynamic layout inconsistencies from App Forensics
        layout_flaws = 0
        if app_forensics.suspected_clone:
            layout_flaws += 2
        if app_forensics.layout_consistency == "LOW":
            layout_flaws += 1
            
        # 4. Dynamic AI visual flags
        ai_flags = 0
        if app_forensics.font_consistency in ["SUSPICIOUS", "INCONSISTENT"]:
            ai_flags += 1
        if app_forensics.app_authenticity_score < 0.6:
            ai_flags += 1
        
        # Assemble for Phase 4
        return TrustScoreInput(
            upi_transaction_id_valid=is_utr_valid,
            payment_amount_valid=is_amount_valid,
            fraud_fingerprint_match=fraud.fingerprint_match,
            fraud_match_confidence=fraud.match_confidence,
            
            metadata_anomalies_detected=metadata_anomalies, 
            layout_inconsistencies_detected=layout_flaws,
            ai_visual_flags=ai_flags
        )

