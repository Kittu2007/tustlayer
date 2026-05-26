import pytest
from app.modules.trust_score.schemas import TrustScoreInput, RiskLevel
from app.modules.trust_score.service import FinalDecisionAssembler

def test_perfect_trust_score():
    assembler = FinalDecisionAssembler()
    input_data = TrustScoreInput(
        upi_transaction_id_valid=True,
        payment_amount_valid=True,
        fraud_fingerprint_match=False,
        metadata_anomalies_detected=0,
        layout_inconsistencies_detected=0,
        ai_visual_flags=0
    )
    result = assembler.evaluate(input_data)
    
    assert result.trust_score == 100.0
    assert result.risk_level == RiskLevel.LOW
    assert result.fraud_probability == 0.0

def test_fraud_escalation_override():
    assembler = FinalDecisionAssembler()
    input_data = TrustScoreInput(
        upi_transaction_id_valid=True, # Valid UTR
        payment_amount_valid=True,     # Valid amount
        fraud_fingerprint_match=True,  # KNOWN SCAM
        fraud_match_confidence=0.95,
        metadata_anomalies_detected=0,
        layout_inconsistencies_detected=0,
        ai_visual_flags=0
    )
    result = assembler.evaluate(input_data)
    
    # Mathematical score would normally just lose 18% (score ~82)
    # BUT Escalation Rule should force it to 0 and HIGH risk
    assert result.trust_score == 0.0
    assert result.risk_level == RiskLevel.HIGH
    assert result.fraud_probability == 0.99
    assert "Known scam template pattern detected" in result.confidence_reasoning
    assert "Do not release goods or services" in result.recommended_actions
