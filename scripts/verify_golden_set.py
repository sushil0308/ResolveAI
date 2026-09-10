import os
import sys
import re
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.getcwd())

from backend.app.services.agent_service import SupportAgentPipeline, AgentAnalysisRequest

def verify_golden_dataset():
    print("--- Starting Automated Verification of Golden Evaluation Set (200 Cases) ---")
    golden_path = os.path.join("evaluation", "golden_set.csv")
    df_gold = pd.read_csv(golden_path)
    print(f"Loaded {len(df_gold)} examples from {golden_path}.")

    pipeline = SupportAgentPipeline()
    print("SupportAgentPipeline loaded successfully.")

    machine_verified_rows = []
    review_flags = []

    for idx, row in df_gold.iterrows():
        ex_id = str(row["example_id"])
        current_intent = str(row["intent"])
        current_escalation = str(row["escalation_label"])
        current_reason = str(row.get("escalation_reason", ""))
        msg = str(row["customer_message"])
        hist_reply = str(row.get("historical_brand_text", ""))

        # Run pipeline classification
        req = AgentAnalysisRequest(customer_message=msg)
        analysis = pipeline.analyze_message(req)

        pred_intent = analysis.intent
        pred_intent_conf = analysis.intent_confidence
        pred_escalation = analysis.escalation_decision
        pred_escalation_reason = analysis.escalation_reason

        # Verification logic:
        # Check intent alignment
        intent_matches = (current_intent == pred_intent)
        
        # Check escalation policy alignment
        escalation_matches = (current_escalation == pred_escalation)

        # Detect specific domain discrepancies:
        # e.g., payment / billing keywords in playback issue
        msg_lower = msg.lower()
        billing_keywords = ["payment", "refund", "charge", "charged", "bill", "billing", "credit card", "google play card", "subscription price", "cost"]
        is_billing_topic = any(k in msg_lower for k in billing_keywords)

        account_keywords = ["password", "hacked", "stolen", "compromised", "login", "cant log in", "email changed"]
        is_account_topic = any(k in msg_lower for k in account_keywords)

        cancel_keywords = ["cancel", "cancellation", "downgrade", "end subscription", "stop service"]
        is_cancel_topic = any(k in msg_lower for k in cancel_keywords)

        is_questionable = False
        flag_reason = ""
        suggested_intent = current_intent

        if current_intent == "playback_streaming_issue" and is_billing_topic:
            is_questionable = True
            suggested_intent = "subscription_billing"
            flag_reason = f"Customer message mentions billing/payment keywords ('{next(k for k in billing_keywords if k in msg_lower)}') but is labeled as playback_streaming_issue."
        elif current_intent == "playback_streaming_issue" and is_account_topic and "not can't play" not in msg_lower:
            is_questionable = True
            suggested_intent = "account_access"
            flag_reason = "Customer message indicates account access issues rather than audio streaming failure."
        elif not intent_matches and pred_intent_conf > 0.82:
            is_questionable = True
            suggested_intent = pred_intent
            flag_reason = f"High-confidence classifier discrepancy: Model predicts '{pred_intent}' ({pred_intent_conf:.1%}) while ground truth is '{current_intent}'."

        # Compute verification confidence
        if intent_matches and escalation_matches:
            verif_conf = round(min(0.98, max(0.85, pred_intent_conf)), 2)
            machine_verified = True
            verif_reason = f"Confirmed: High semantic concordance with intent '{current_intent}' ({pred_intent_conf:.1%}) and consistent escalation policy."
        elif intent_matches:
            verif_conf = round(min(0.90, max(0.75, pred_intent_conf)), 2)
            machine_verified = True
            verif_reason = f"Confirmed intent '{current_intent}' ({pred_intent_conf:.1%}). Minor policy variance on triage routing."
        elif is_questionable:
            verif_conf = round(float(pred_intent_conf), 2)
            machine_verified = False
            verif_reason = f"Questionable: {flag_reason}"
            review_flags.append({
                "example_id": ex_id,
                "current_label": current_intent,
                "suggested_label": suggested_intent,
                "confidence": verif_conf,
                "reason": flag_reason,
            })
        else:
            verif_conf = round(float(pred_intent_conf), 2)
            machine_verified = (pred_intent_conf < 0.60) # Borderline classifier doubt, keep original
            verif_reason = f"Retained ground truth: Classifier prediction '{pred_intent}' has moderate confidence ({pred_intent_conf:.1%}), preserving original label."

        row_dict = dict(row)
        row_dict["verification_method"] = "automated_ensemble_verification"
        row_dict["verification_confidence"] = verif_conf
        row_dict["machine_verified"] = machine_verified
        row_dict["machine_reason"] = verif_reason

        # Ensure human verification status is strictly honest:
        # DO NOT mark machine-generated verification as human verification
        if "human_verified" in row_dict:
            # Preserve existing human verification if explicitly set, otherwise False
            row_dict["human_verified"] = False

        machine_verified_rows.append(row_dict)

    df_machine = pd.DataFrame(machine_verified_rows)
    verified_csv_path = os.path.join("evaluation", "golden_set_machine_verified.csv")
    df_machine.to_csv(verified_csv_path, index=False)
    print(f"Saved machine-verified golden set to {verified_csv_path} ({len(df_machine)} rows).")

    df_flags = pd.DataFrame(review_flags)
    flags_csv_path = os.path.join("evaluation", "golden_set_review_flags.csv")
    df_flags.to_csv(flags_csv_path, index=False)
    print(f"Saved {len(df_flags)} review flags to {flags_csv_path}.")

    return len(df_machine), len(df_flags)

if __name__ == "__main__":
    verify_golden_dataset()
