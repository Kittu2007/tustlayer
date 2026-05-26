from typing import Tuple
from backend.modules.trust_score.schemas import TrustScoreInput, RiskLevel

class RiskEscalationLayer:
    """
    Deterministic overrides. Rules decide.
    Overrides math if absolute fraud signals are detected.
    """
    
    @staticmethod
    def evaluate(data: TrustScoreInput, base_score: float) -> Tuple[float, RiskLevel, float]:
        """
        Returns (final_score, risk_level, fraud_probability)
        """
        # ESCALATION RULE 1: Known Scam Match
        if data.fraud_fingerprint_match and data.fraud_match_confidence > 0.8:
            # Absolute override
            return (0.0, RiskLevel.HIGH, 0.99)
            
        # ESCALATION RULE 2: Critical Transaction Fields Missing
        if not data.upi_transaction_id_valid and not data.payment_amount_valid:
            # Extremely high risk, override math
            return (min(base_score, 10.0), RiskLevel.HIGH, 0.90)
            
        # Standard Risk Band Classification
        if base_score >= 85.0:
            risk = RiskLevel.LOW
            prob = (100.0 - base_score) / 100.0
        elif base_score >= 60.0:
            risk = RiskLevel.MEDIUM
            prob = (100.0 - base_score) / 100.0
        else:
            risk = RiskLevel.HIGH
            prob = (100.0 - base_score) / 100.0
            
        return (base_score, risk, round(prob, 2))
