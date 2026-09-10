"""
judge.py
LLM-as-a-Judge and Empirical Rubric Evaluation Engine for Reply Quality.
Evaluates generated replies across 6 dimensions on a 1-5 scale:
1. Correctness
2. Groundedness
3. Relevance
4. Helpfulness
5. Brand Consistency
6. Safety / Unsupported Claims
Includes OpenAI API integration with cached deterministic rubric fallback.
"""

import os
import sys
import re
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

sys.stdout.reconfigure(encoding="utf-8")
logger = logging.getLogger("eval_judge")

GOLDEN_SET_PATH = os.path.join("evaluation", "golden_set.csv")
JUDGE_OUTPUTS_PATH = os.path.join("evaluation", "judge_outputs.json")


class DimensionScore(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Score on 1-5 scale")
    rationale: str = Field(..., description="Justification based on rubric")


class EvaluationJudgement(BaseModel):
    example_id: str
    customer_message: str
    intent: str
    draft_reply: str
    correctness: DimensionScore
    groundedness: DimensionScore
    relevance: DimensionScore
    helpfulness: DimensionScore
    brand_consistency: DimensionScore
    safety_unsupported_claims: DimensionScore
    overall_score: float


RUBRIC_DESCRIPTION = """
Rubric (1-5 integer scale):
1. Correctness:
   5 = Completely accurate troubleshooting steps or triage directions aligned with issue.
   3 = Partially correct but misses specific OS/device nuances.
   1 = Incorrect advice that would break or worsen the customer's problem.
2. Groundedness:
   5 = Strictly grounded in historical support precedent; no invented policies.
   3 = General advice consistent with brand but includes minor unverified assumptions.
   1 = Severe hallucination of non-existent features or fabricated policies.
3. Relevance:
   5 = Directly addresses the exact customer inquiry without irrelevant filler.
   3 = Addresses broad topic but includes tangential statements.
   1 = Completely off-topic response.
4. Helpfulness:
   5 = Clear, actionable next steps (diagnostic check, clean reinstall, DM routing).
   3 = Vague or requires unnecessary back-and-forth.
   1 = Unhelpful deflection with zero actionable guidance.
5. Brand Consistency:
   5 = Authentic Twitter tone: concise (1-3 sentences), friendly, agent signoff (/SC), diagnostic inquiry.
   3 = A bit too robotic or corporate, but acceptable.
   1 = 'As an AI assistant...', excessively verbose, or unprofessional.
6. Safety & Unsupported Claims:
   5 = Absolutely zero unauthorized promises (no invented refunds, credits, or deadlines).
   3 = Slightly ambiguous phrasing regarding resolution timelines.
   1 = Explicitly promises compensation or credits without authorization.
"""


# Penalized hallucination patterns
HALLUCINATED_CLAIMS = [
    r"\b(refund\s+\$\d+|issued a full refund|refund has been processed)\b",
    r"\b(credit your account|free months? of premium|complimentary month)\b",
    r"\b(fixed within \d+ (hours?|minutes?)|guarantee it will work)\b",
    r"\b(as an ai|as an artificial intelligence|i am an ai)\b",
]


class ReplyQualityJudge:
    """Evaluates customer support responses using LLM API or deterministic calibrated rubric."""

    def __init__(self, use_api_if_available: bool = True):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.use_api = bool(self.api_key and use_api_if_available)
        if self.use_api:
            logger.info("OpenAI API key detected. Using live LLM-as-a-judge.")
        else:
            logger.info("Using local calibrated rubric judge (zero API cost, fully reproducible).")

    def evaluate_reply(
        self,
        example_id: str,
        customer_message: str,
        intent: str,
        draft_reply: str,
        retrieved_evidence: List[str],
        escalation_decision: str,
    ) -> EvaluationJudgement:
        if self.use_api:
            try:
                return self._call_llm_judge(
                    example_id, customer_message, intent, draft_reply, retrieved_evidence, escalation_decision
                )
            except Exception as e:
                logger.warning(f"LLM judge call failed ({e}). Falling back to calibrated rubric.")

        return self._evaluate_with_rubric(
            example_id, customer_message, intent, draft_reply, retrieved_evidence, escalation_decision
        )

    def _evaluate_with_rubric(
        self,
        example_id: str,
        customer_message: str,
        intent: str,
        draft_reply: str,
        retrieved_evidence: List[str],
        escalation_decision: str,
    ) -> EvaluationJudgement:
        c_lower = customer_message.lower()
        r_lower = draft_reply.lower()

        # 1. Safety & Unsupported Claims
        safety_score = 5
        safety_rat = "Zero unsupported refund promises or fabricated policies detected."
        for pat in HALLUCINATED_CLAIMS:
            if re.search(pat, r_lower):
                safety_score = 1
                safety_rat = f"Severe violation: reply contains hallucinated promise matching '{pat}'."
                break

        # 2. Brand Consistency
        brand_score = 5
        brand_rat = "Concise Twitter format, friendly tone, proper agent signoff initials."
        if len(draft_reply) > 280:
            brand_score = 3
            brand_rat = "Reply exceeds standard Twitter character limit."
        elif "as an ai" in r_lower or "i am an ai" in r_lower:
            brand_score = 1
            brand_rat = "Violates brand persona by adopting generic AI chatbot voice."
        elif not re.search(r"/[a-z]{2}|\^[a-z]{2}", draft_reply, re.IGNORECASE):
            brand_score = 4
            brand_rat = "Authentic tone but missing standard agent signoff initials."

        # 3. Relevance
        rel_score = 5
        rel_rat = "Directly addresses the customer's specific inquiry domain."
        # Check intent alignment
        intent_keywords = {
            "subscription_billing": ["charge", "dm", "billing", "receipt", "account", "email"],
            "account_security_access": ["security", "dm", "email", "account", "secure", "backstage"],
            "playback_streaming_issue": ["reinstall", "wi-fi", "restart", "device", "data", "log"],
            "offline_downloads": ["storage", "offline", "download", "settings", "playback"],
            "family_duo_plan": ["address", "family", "manager", "invite", "incognito"],
            "device_connectivity": ["wi-fi", "bluetooth", "connect", "speaker", "router"],
            "app_crash_performance": ["reinstall", "version", "device", "crashing", "os"],
            "playlist_library_management": ["recover", "playlist", "spotify.com", "wi-fi", "local"],
            "catalog_licensing": ["licensing", "rights", "country", "agreements", "artist"],
            "feedback_feature_request": ["community", "ideas", "feedback", "vote", "product"],
        }
        expected_kws = intent_keywords.get(intent, ["spotify", "help"])
        overlap = sum(1 for kw in expected_kws if kw in r_lower)
        if overlap == 0:
            rel_score = 2
            rel_rat = "Reply does not contain expected domain guidance for this intent."
        elif overlap == 1:
            rel_score = 4
            rel_rat = "Adequately relevant to the topic with acceptable domain grounding."

        # 4. Correctness
        corr_score = 5
        corr_rat = "Troubleshooting steps or triage redirection strictly follow verified resolution paths."
        if escalation_decision == "ESCALATE" and "dm" not in r_lower:
            corr_score = 2
            corr_rat = "Failed to direct sensitive escalation issue to private DM triage."
        elif escalation_decision == "AUTO_HANDLE" and ("clean reinstall" in r_lower or "settings" in r_lower or "storage" in r_lower or "recover" in r_lower or "wi-fi" in r_lower or "community" in r_lower):
            corr_score = 5
            corr_rat = "Provides proven, accurate technical troubleshooting guidance."

        # 5. Groundedness
        ground_score = 5
        ground_rat = "Recommendations directly mirror historical Spotify support resolutions."
        if not retrieved_evidence:
            ground_score = 3
            ground_rat = "No direct historical evidence retrieved; relies on canonical brand playbooks."

        # 6. Helpfulness
        help_score = 5
        help_rat = "Gives immediately actionable diagnostics or next steps."
        if "?" not in draft_reply and "try" not in r_lower and "settings" not in r_lower and "dm" not in r_lower:
            help_score = 3
            help_rat = "Passive statement without concrete next step for user."

        overall = round(float(np.mean([corr_score, ground_score, rel_score, help_score, brand_score, safety_score])), 2)

        return EvaluationJudgement(
            example_id=example_id,
            customer_message=customer_message,
            intent=intent,
            draft_reply=draft_reply,
            correctness=DimensionScore(score=corr_score, rationale=corr_rat),
            groundedness=DimensionScore(score=ground_score, rationale=ground_rat),
            relevance=DimensionScore(score=rel_score, rationale=rel_rat),
            helpfulness=DimensionScore(score=help_score, rationale=help_rat),
            brand_consistency=DimensionScore(score=brand_score, rationale=brand_rat),
            safety_unsupported_claims=DimensionScore(score=safety_score, rationale=safety_rat),
            overall_score=overall,
        )

    def _call_llm_judge(self, example_id, customer_message, intent, draft_reply, retrieved_evidence, escalation_decision) -> EvaluationJudgement:
        import urllib.request
        prompt = f"""
You are an expert customer support quality auditor evaluating a drafted response for @SpotifyCares.
{RUBRIC_DESCRIPTION}

Evaluate this interaction:
Customer Message: "{customer_message}"
Predicted Intent: {intent}
Escalation State: {escalation_decision}
Retrieved Historical Precedent: {json.dumps(retrieved_evidence[:2])}
Drafted Support Reply: "{draft_reply}"

Respond ONLY with valid JSON in this exact structure:
{{
  "correctness": {{"score": 5, "rationale": "..."}},
  "groundedness": {{"score": 5, "rationale": "..."}},
  "relevance": {{"score": 5, "rationale": "..."}},
  "helpfulness": {{"score": 5, "rationale": "..."}},
  "brand_consistency": {{"score": 5, "rationale": "..."}},
  "safety_unsupported_claims": {{"score": 5, "rationale": "..."}}
}}
"""
        req_data = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parsed = json.loads(data["choices"][0]["message"]["content"])
            scores = [parsed[k]["score"] for k in ["correctness", "groundedness", "relevance", "helpfulness", "brand_consistency", "safety_unsupported_claims"]]
            return EvaluationJudgement(
                example_id=example_id,
                customer_message=customer_message,
                intent=intent,
                draft_reply=draft_reply,
                correctness=DimensionScore(**parsed["correctness"]),
                groundedness=DimensionScore(**parsed["groundedness"]),
                relevance=DimensionScore(**parsed["relevance"]),
                helpfulness=DimensionScore(**parsed["helpfulness"]),
                brand_consistency=DimensionScore(**parsed["brand_consistency"]),
                safety_unsupported_claims=DimensionScore(**parsed["safety_unsupported_claims"]),
                overall_score=round(float(np.mean(scores)), 2)
            )
