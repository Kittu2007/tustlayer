from app.modules.trust_score.schemas import TrustScoreInput, TrustScoreResult
from app.modules.trust_score.engine import TrustScoreEngine
from app.modules.trust_score.escalation import RiskEscalationLayer
from app.modules.trust_score.reasoning import ConfidenceReasoningGenerator, RecommendationEngine
from app.core.ai_orchestrator import AIReasoningOrchestrator
from app.integrations.nvidia_client import QwenReasoningProvider, PhiReasoningProvider

class FinalDecisionAssembler:
    """
    Orchestrates the deterministic scoring pipeline.
    """
    def __init__(self):
        self.engine = TrustScoreEngine()
        self.escalation = RiskEscalationLayer()
        self.ai_orchestrator = AIReasoningOrchestrator(
            primary=QwenReasoningProvider(),
            fallback=PhiReasoningProvider()
        )
        self.reasoning = ConfidenceReasoningGenerator(self.ai_orchestrator)
        self.recommendations = RecommendationEngine(self.ai_orchestrator)
        
    async def evaluate(self, data: TrustScoreInput) -> TrustScoreResult:
        # 1. Base deterministic math
        base_score = self.engine.calculate_base_score(data)
        
        # 2. Risk Escalation (Overrides)
        final_score, risk_level, fraud_prob = self.escalation.evaluate(data, base_score)
        
        # 3. Psychological Translation (via AI)
        reasons = await self.reasoning.generate_reasons(data)
        actions = await self.recommendations.generate_recommendations(risk_level, data)
        
        # 4. Assemble Result
        return TrustScoreResult(
            trust_score=final_score,
            risk_level=risk_level,
            fraud_probability=fraud_prob,
            confidence_reasoning=reasons,
            recommended_actions=actions
        )

def get_final_decision_assembler() -> FinalDecisionAssembler:
    return FinalDecisionAssembler()
