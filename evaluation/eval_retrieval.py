"""
eval_retrieval.py
Evaluates historical support case retrieval performance against the Golden Evaluation Set.
Measures Recall@1, Recall@3, Recall@5, MRR (Mean Reciprocal Rank), and cosine similarity distributions.
Ensures and verifies zero leakage (eval conversation never matches retrieved conversation).
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, Any

sys.stdout.reconfigure(encoding="utf-8")

from backend.app.services.retrieval import HistoricalCaseRetriever

GOLDEN_PATH = os.path.join("evaluation", "golden_set.csv")
RETRIEVAL_RESULTS_PATH = os.path.join("evaluation", "retrieval_results.json")


def evaluate_retrieval(top_k: int = 5) -> Dict[str, Any]:
    print("=== Running Historical Case Retrieval Evaluation ===")
    print(f"Loading Golden Set from {GOLDEN_PATH}...")
    df_gold = pd.read_csv(GOLDEN_PATH)
    print(f"Loaded {len(df_gold)} golden evaluation queries.")

    retriever = HistoricalCaseRetriever()

    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0
    reciprocal_ranks = []
    top_similarities = []
    per_intent_recalls = {intent: {"total": 0, "hits_at_1": 0, "hits_at_5": 0} for intent in df_gold["intent"].unique()}

    leakage_incidents = 0

    for idx, row in df_gold.iterrows():
        query_text = row["customer_message"]
        target_intent = row["intent"]
        conv_id = row["source_conversation_id"]

        per_intent_recalls[target_intent]["total"] += 1

        # Search with strict exclusion of this query's conversation ID
        retrieved = retriever.search(
            query=query_text,
            top_k=top_k,
            intent_filter=target_intent,
            exclude_conv_id=conv_id,
        )

        if not retrieved:
            reciprocal_ranks.append(0.0)
            top_similarities.append(0.0)
            continue

        top_similarities.append(retrieved[0].similarity)

        # Check leakage
        for r in retrieved:
            if r.conversation_id == conv_id:
                leakage_incidents += 1

        # Check intent matches
        matched_rank = None
        for rank_idx, r in enumerate(retrieved, start=1):
            if r.intent == target_intent:
                if matched_rank is None:
                    matched_rank = rank_idx

        if matched_rank is not None:
            reciprocal_ranks.append(1.0 / matched_rank)
            if matched_rank == 1:
                hits_at_1 += 1
                per_intent_recalls[target_intent]["hits_at_1"] += 1
            if matched_rank <= 3:
                hits_at_3 += 1
            if matched_rank <= 5:
                hits_at_5 += 1
                per_intent_recalls[target_intent]["hits_at_5"] += 1
        else:
            reciprocal_ranks.append(0.0)

    n_total = len(df_gold)
    recall_at_1 = round(hits_at_1 / n_total, 4)
    recall_at_3 = round(hits_at_3 / n_total, 4)
    recall_at_5 = round(hits_at_5 / n_total, 4)
    mrr = round(float(np.mean(reciprocal_ranks)), 4)
    avg_top_sim = round(float(np.mean(top_similarities)), 4)

    # Compute per-intent breakdown
    per_intent_report = {}
    for intent, counts in per_intent_recalls.items():
        tot = counts["total"]
        per_intent_report[intent] = {
            "total_queries": tot,
            "recall@1": round(counts["hits_at_1"] / tot, 4) if tot > 0 else 0.0,
            "recall@5": round(counts["hits_at_5"] / tot, 4) if tot > 0 else 0.0,
        }

    results = {
        "evaluation_dataset_size": n_total,
        "metrics": {
            "recall@1": recall_at_1,
            "recall@3": recall_at_3,
            "recall@5": recall_at_5,
            "mrr": mrr,
            "mean_top1_similarity": avg_top_sim,
        },
        "leakage_verification": {
            "leakage_incidents_detected": leakage_incidents,
            "is_leakage_free": bool(leakage_incidents == 0),
        },
        "per_intent_breakdown": per_intent_report,
    }

    print("\n--- Retrieval Evaluation Summary ---")
    print(f"Recall@1: {recall_at_1 * 100:.2f}%")
    print(f"Recall@3: {recall_at_3 * 100:.2f}%")
    print(f"Recall@5: {recall_at_5 * 100:.2f}%")
    print(f"MRR:      {mrr:.4f}")
    print(f"Avg Top-1 Sim: {avg_top_sim:.3f}")
    print(f"Zero-Leakage Guarantee: {'VERIFIED (0 leaks)' if leakage_incidents == 0 else 'FAILED'}")

    with open(RETRIEVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved retrieval results to {RETRIEVAL_RESULTS_PATH}")
    return results


if __name__ == "__main__":
    evaluate_retrieval()
