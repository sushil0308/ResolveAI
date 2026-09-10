"""
classifier.py
Production-grade Main Intent Classifier for Spotify Customer Support.
Combines calibrated n-gram TF-IDF representations, intent taxonomy anchors,
and multi-signal heuristic disambiguation into a structured, explainable output schema.
"""

import os
import re
import yaml
import joblib
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

CONFIG_PATH = os.path.join("config", "config.yaml")
INTENTS_PATH = os.path.join("config", "intents.yaml")
MODEL_PATH = os.path.join("data", "processed", "baseline_tfidf_model.pkl")


class IntentClassificationResult(BaseModel):
    intent: str = Field(..., description="Top predicted intent ID")
    intent_name: str = Field(..., description="Human-readable intent title")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score")
    reason: str = Field(..., description="Clear explanation for the classification decision")
    alternative_intent: Optional[str] = Field(None, description="Second highest ranked intent")
    alternative_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence of alternative intent")
    is_uncertain: bool = Field(False, description="Whether prediction confidence falls below reliability threshold")
    all_probabilities: Dict[str, float] = Field(default_factory=dict, description="Full probability distribution")


# Domain anchors and disambiguation patterns for operational accuracy
DISAMBIGUATION_RULES = {
    "family_duo_plan": [
        r"\b(address|invite|invitation|member|members|home|family plan|duo plan)\b"
    ],
    "playback_streaming_issue": [
        r"\b(shuffle|repeat|paus|stutter|skip|skipping|stops playing|cuts out|volume normalize|distort|buffer)\b"
    ],
    "offline_downloads": [
        r"\b(download|offline|greyed out|grayed out|storage|sd card|waiting to download)\b"
    ],
    "account_security_access": [
        r"\b(hack|compromis|password|reset link|stolen account|email changed|cant log|can't log|locked out)\b"
    ],
    "feedback_feature_request": [
        r"\b(feature request|suggest|suggestion|lyrics|bring back|hate the new|ui redesign|recommendation)\b"
    ],
    "app_crash_performance": [
        r"\b(crash|freez|black screen|blank screen|closes on open|unresponsive|force close)\b"
    ],
    "device_connectivity": [
        r"\b(bluetooth|chromecast|carplay|android auto|ps4|xbox|sonos|speaker|spotify connect|airplay)\b"
    ],
    "catalog_licensing": [
        r"\b(country|region|rights|licens|censored|explicit|not on spotify|unavailable|removed from spotify)\b"
    ],
    "subscription_billing": [
        r"\b(charged?|billing|receipt|payment|refund|sheerid|student discount|cancell?ed?|charged twice)\b"
    ],
    "playlist_library_management": [
        r"\b(playlist|local files|liked songs|disappeared playlist|queue)\b"
    ],
}


class IntentClassifier:
    """Main intent classification engine."""

    def __init__(self, model_path: str = MODEL_PATH, intents_path: str = INTENTS_PATH):
        self.model_path = model_path
        self.intents_path = intents_path
        self.model = None
        self.intents_cfg = {}
        self.classes: List[str] = []
        self._load_artifacts()

    def _load_artifacts(self):
        # Load taxonomy configuration
        if os.path.exists(self.intents_path):
            with open(self.intents_path, "r", encoding="utf-8") as f:
                raw_cfg = yaml.safe_load(f)
                self.intents_cfg = raw_cfg.get("intents", {})
        else:
            print(f"Warning: Intents file not found at {self.intents_path}")

        # Load trained baseline TF-IDF model
        if os.path.exists(self.model_path):
            saved = joblib.load(self.model_path)
            self.model = saved
            self.classes = list(saved["classifier"].classes_)
        else:
            print(f"Warning: Model not found at {self.model_path}. Train baselines first.")
            self.classes = list(self.intents_cfg.keys()) if self.intents_cfg else []

    def classify(self, message: str) -> IntentClassificationResult:
        if not message or not message.strip():
            return IntentClassificationResult(
                intent="feedback_feature_request",
                intent_name="Feedback & Feature Suggestions",
                confidence=0.10,
                reason="Customer message is empty or whitespace.",
                alternative_intent=None,
                alternative_confidence=None,
                is_uncertain=True,
                all_probabilities={},
            )

        clean_text = message.strip()
        t_lower = clean_text.lower()

        # Step 1: Base ML Probabilities
        if self.model:
            vec = self.model["vectorizer"]
            clf = self.model["classifier"]
            base_probs = clf.predict_proba(vec.transform([clean_text]))[0]
            scores = np.copy(base_probs)
        else:
            # Fallback uniform
            scores = np.ones(len(self.classes)) / len(self.classes)

        # Step 2: Multi-Signal Disambiguation & Anchor Boosting
        matched_anchors = {}
        for c_idx, c_name in enumerate(self.classes):
            patterns = DISAMBIGUATION_RULES.get(c_name, [])
            for p in patterns:
                m = re.findall(p, t_lower)
                if m:
                    scores[c_idx] += 0.35 * len(m)
                    matched_anchors[c_name] = m

        # Step 3: Softmax Normalization for Calibrated Probabilities
        exp_scores = np.exp(scores * 2.0)
        final_probs = exp_scores / np.sum(exp_scores)

        # Sort indices by probability
        ranked_indices = np.argsort(final_probs)[::-1]
        top_idx = ranked_indices[0]
        alt_idx = ranked_indices[1] if len(ranked_indices) > 1 else None

        top_intent = self.classes[top_idx]
        top_conf = round(float(final_probs[top_idx]), 3)

        alt_intent = self.classes[alt_idx] if alt_idx is not None else None
        alt_conf = round(float(final_probs[alt_idx]), 3) if alt_idx is not None else None

        # Human-readable intent display name
        intent_info = self.intents_cfg.get(top_intent, {})
        intent_name = intent_info.get("name", top_intent.replace("_", " ").title())

        # Step 4: Explainable Reason Generation
        reason = self._generate_reason(clean_text, top_intent, intent_info, matched_anchors.get(top_intent, []))

        # Check uncertainty threshold
        is_uncertain = bool(top_conf < 0.45 or (alt_conf and (top_conf - alt_conf < 0.10)))

        all_prob_dict = {
            self.classes[i]: round(float(final_probs[i]), 3)
            for i in ranked_indices
        }

        return IntentClassificationResult(
            intent=top_intent,
            intent_name=intent_name,
            confidence=top_conf,
            reason=reason,
            alternative_intent=alt_intent,
            alternative_confidence=alt_conf,
            is_uncertain=is_uncertain,
            all_probabilities=all_prob_dict,
        )

    def _generate_reason(self, text: str, intent: str, info: Dict[str, Any], anchors: List[Any]) -> str:
        intent_desc = info.get("description", "")
        if anchors:
            flat_anchors = [a if isinstance(a, str) else a[0] for a in anchors[:2]]
            anchor_str = ", ".join(f"'{a}'" for a in flat_anchors)
            return f"Customer inquiry contains key indicators ({anchor_str}) indicating {intent_desc.lower()}"
        return f"Message pattern and semantic vocabulary strongly align with {intent_desc.lower()}"
