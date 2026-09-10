"""
escalation.py
Explainable, multi-signal escalation engine.
Computes AUTO_HANDLE vs ESCALATE decisions using calibrated intent confidence,
sensitive domain gates, retrieval similarity thresholds, and severity keyword safeguards.
Prioritizes minimizing False Auto-Handling Rate to protect customer trust.
"""

import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EscalationSignals(BaseModel):
    intent_confidence: float = Field(..., ge=0.0, le=1.0)
    top_retrieval_score: float = Field(..., ge=0.0, le=1.0)
    evidence_count: int = Field(..., ge=0)
    is_uncertain: bool = Field(...)
    sensitive_intent: bool = Field(...)
    severity_trigger: Optional[str] = Field(None)


class EscalationDecisionResult(BaseModel):
    decision: str = Field(..., description="AUTO_HANDLE or ESCALATE")
    reason: str = Field(..., description="Non-technical human explanation for the decision")
    signals: EscalationSignals
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH")


# Critical sensitive intents that ALWAYS require confidential human resolution
SENSITIVE_INTENTS = {
    "account_security_access": "Account security breaches, password compromises, and account lockouts require confidential human identity verification backstage.",
    "subscription_billing": "Financial charges, refund requests, and recurring billing disputes require human review of billing accounts and payment processors."
}

# High-risk severity terms in customer text
SEVERITY_REGEX = re.compile(
    r"\b(hacked|stolen|compromised|unauthorized|charged twice|double charge|refund my money|bank chargeback|fraud|dispute|lawsuit|sue you)\b",
    re.IGNORECASE
)


class EscalationEngine:
    """Computes explainable, safety-first escalation decisions."""

    def __init__(
        self,
        min_intent_confidence: float = 0.45,
        min_retrieval_similarity: float = 0.15,
        require_evidence_count: int = 1,
    ):
        self.min_intent_confidence = min_intent_confidence
        self.min_retrieval_similarity = min_retrieval_similarity
        self.require_evidence_count = require_evidence_count

    def evaluate(
        self,
        customer_message: str,
        intent: str,
        intent_confidence: float,
        is_uncertain: bool,
        top_retrieval_score: float,
        evidence_count: int,
    ) -> EscalationDecisionResult:
        t_clean = (customer_message or "").strip().lower()

        # Check severity keywords
        severity_match = SEVERITY_REGEX.search(t_clean)
        severity_term = severity_match.group(0) if severity_match else None

        signals = EscalationSignals(
            intent_confidence=round(intent_confidence, 3),
            top_retrieval_score=round(top_retrieval_score, 3),
            evidence_count=evidence_count,
            is_uncertain=is_uncertain,
            sensitive_intent=bool(intent in SENSITIVE_INTENTS),
            severity_trigger=severity_term,
        )

        # Rule 1: Mandatory Sensitive Intent Gate
        if intent in SENSITIVE_INTENTS:
            return EscalationDecisionResult(
                decision="ESCALATE",
                reason=SENSITIVE_INTENTS[intent],
                signals=signals,
                risk_level="HIGH",
            )

        # Rule 2: High-Risk Severity Keyword Gate
        if severity_term:
            return EscalationDecisionResult(
                decision="ESCALATE",
                reason=f"Customer inquiry contains high-risk severity indicator ('{severity_term}'); escalated for manual review to protect user security.",
                signals=signals,
                risk_level="HIGH",
            )

        # Rule 3: Classification Uncertainty Gate (Protect against False Auto-Handling)
        if is_uncertain or intent_confidence < self.min_intent_confidence:
            return EscalationDecisionResult(
                decision="ESCALATE",
                reason=f"The customer's inquiry is ambiguous or classification confidence is low ({intent_confidence*100:.1f}%); escalated to a human agent to avoid misleading automated guidance.",
                signals=signals,
                risk_level="MEDIUM",
            )

        # Rule 4: Insufficient Corroborating Historical Evidence Gate
        if evidence_count < self.require_evidence_count or top_retrieval_score < self.min_retrieval_similarity:
            return EscalationDecisionResult(
                decision="ESCALATE",
                reason="The system found insufficient historical support precedent for this query; routed to human agent to ensure proper resolution.",
                signals=signals,
                risk_level="MEDIUM",
            )

        # Rule 5: Safe Auto-Handling
        return EscalationDecisionResult(
            decision="AUTO_HANDLE",
            reason="The inquiry involves standard technical troubleshooting with high classification confidence and strong corroborating historical resolution precedent.",
            signals=signals,
            risk_level="LOW",
        )
