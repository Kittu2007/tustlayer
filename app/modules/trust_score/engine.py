from app.modules.trust_score.schemas import TrustScoreInput

class TrustScoreEngine:
    """
    Deterministic base score calculation based on strict weighting.
    UPI Transaction Logic: 28%
    Metadata Intelligence: 22%
    AI Visual Reasoning: 20%
    Fraud Intelligence Match: 18%
    Layout Validation: 12%
    """
    
    @staticmethod
    def calculate_base_score(data: TrustScoreInput) -> float:
        score = 100.0
        
        # 1. UPI Transaction Logic (28%)
        if not data.upi_transaction_id_valid:
            score -= 14.0
        if not data.payment_amount_valid:
            score -= 14.0
            
        # 2. Metadata Intelligence (22%)
        if data.metadata_anomalies_detected > 0:
            # Deduct points linearly up to 22
            deduction = min(22.0, data.metadata_anomalies_detected * 11.0)
            score -= deduction
            
        # 3. AI Visual Reasoning (20%)
        if data.ai_visual_flags > 0:
            deduction = min(20.0, data.ai_visual_flags * 10.0)
            score -= deduction
            
        # 4. Fraud Intelligence Match (18%)
        # If there is a match, we lose points proportional to the match confidence
        if data.fraud_fingerprint_match:
            score -= (18.0 * data.fraud_match_confidence)
            
        # 5. Layout Validation (12%)
        if data.layout_inconsistencies_detected > 0:
            deduction = min(12.0, data.layout_inconsistencies_detected * 6.0)
            score -= deduction
            
        return max(0.0, round(score, 2))
