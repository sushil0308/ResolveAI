"""
agent_service.py
Unified Agent Pipeline orchestrating intent classification, historical case retrieval,
safety escalation evaluation, and grounded draft reply generation.
Includes input sanitization, prompt injection safeguards, and structured output formatting.
"""

import re
import html
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.classification.classifier import IntentClassifier, IntentClassificationResult
from backend.app.services.retrieval import HistoricalCaseRetriever, RetrievedCase
from backend.app.services.escalation import EscalationEngine, EscalationDecisionResult
from backend.app.generation.reply_generator import GroundedReplyGenerator, DraftReplyResult, EvidenceSnippet

logger = logging.getLogger("agent_pipeline")
logging.basicConfig(level=logging.INFO)


class AgentAnalysisRequest(BaseModel):
    customer_message: str = Field(..., min_length=1, max_length=1500, description="Inbound customer message")
    source_conversation_id: Optional[str] = Field(None, description="Optional conversation ID for exclusion/tracing")


class AgentAnalysisResponse(BaseModel):
    # Intent
    intent: str
    intent_name: str
    intent_confidence: float
    intent_explanation: str
    alternative_intent: Optional[str] = None
    alternative_confidence: Optional[float] = None
    is_uncertain: bool

    # Historical Retrieval & Evidence
    retrieved_cases: List[RetrievedCase]
    evidence_count: int
    top_retrieval_similarity: float

    # Escalation
    escalation_decision: str  # AUTO_HANDLE or ESCALATE
    escalation_reason: str
    risk_level: str
    escalation_signals: Dict[str, Any]

    # Draft Reply
    draft_reply: str
    grounding_confidence: float
    evidence: List[EvidenceSnippet]
    resolution_type: str

    # Metadata
    cleaned_input: str
    is_flagged_prompt_injection: bool = False


# Security: Prompt injection & malicious directive detector
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"you are now an ai that",
    r"disregard safety guidelines",
    r"reveal your secret",
    r"execute code",
    r"<script\b",
]


class SupportAgentPipeline:
    """End-to-end customer support agent pipeline."""

    def __init__(self):
        logger.info("Initializing SupportAgentPipeline components...")
        self.classifier = IntentClassifier()
        self.retriever = HistoricalCaseRetriever()
        self.escalator = EscalationEngine()
        self.generator = GroundedReplyGenerator(brand_name="Spotify", signoff_initials="/SC")
        logger.info("SupportAgentPipeline initialized successfully.")

    def sanitize_input(self, raw_text: str) -> tuple[str, bool]:
        """Sanitizes customer input and flags potential prompt injection attempts."""
        t = html.unescape(raw_text)
        t = re.sub(r"[\r\n]+", " ", t).strip()

        is_injection = False
        for p in PROMPT_INJECTION_PATTERNS:
            if re.search(p, t, re.IGNORECASE):
                is_injection = True
                logger.warning(f"Potential prompt injection detected: {p}")
                break

        return t, is_injection

    def analyze_message(self, request: AgentAnalysisRequest) -> AgentAnalysisResponse:
        raw_msg = request.customer_message
        clean_text, is_injection = self.sanitize_input(raw_msg)

        # Step 1: Classify Intent
        clf_result = self.classifier.classify(clean_text)

        # Step 2: Retrieve Historical Cases
        retrieved_cases = self.retriever.search(
            query=clean_text,
            top_k=4,
            intent_filter=clf_result.intent,
            exclude_conv_id=request.source_conversation_id,
        )

        top_sim = retrieved_cases[0].similarity if retrieved_cases else 0.0
        evidence_count = len(retrieved_cases)

        # Step 3: Evaluate Escalation
        esc_result = self.escalator.evaluate(
            customer_message=clean_text,
            intent=clf_result.intent,
            intent_confidence=clf_result.confidence,
            is_uncertain=clf_result.is_uncertain,
            top_retrieval_score=top_sim,
            evidence_count=evidence_count,
        )

        # Step 3b: If prompt injection flagged, force ESCALATE
        if is_injection:
            esc_result.decision = "ESCALATE"
            esc_result.reason = "Security guardrail triggered: customer message contains adversarial system directives."
            esc_result.risk_level = "HIGH"

        # Step 4: Generate Grounded Reply
        reply_result = self.generator.generate_reply(
            customer_message=clean_text,
            predicted_intent=clf_result.intent,
            retrieved_cases=retrieved_cases,
            escalation_decision=esc_result.decision,
            intent_confidence=clf_result.confidence,
        )

        return AgentAnalysisResponse(
            intent=clf_result.intent,
            intent_name=clf_result.intent_name,
            intent_confidence=clf_result.confidence,
            intent_explanation=clf_result.reason,
            alternative_intent=clf_result.alternative_intent,
            alternative_confidence=clf_result.alternative_confidence,
            is_uncertain=clf_result.is_uncertain,
            retrieved_cases=retrieved_cases,
            evidence_count=evidence_count,
            top_retrieval_similarity=top_sim,
            escalation_decision=esc_result.decision,
            escalation_reason=esc_result.reason,
            risk_level=esc_result.risk_level,
            escalation_signals=esc_result.signals.model_dump(),
            draft_reply=reply_result.draft_reply,
            grounding_confidence=reply_result.grounding_confidence,
            evidence=reply_result.evidence,
            resolution_type=reply_result.resolution_type,
            cleaned_input=clean_text,
            is_flagged_prompt_injection=is_injection,
        )
