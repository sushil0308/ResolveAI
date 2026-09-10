"""
profile_selected_candidates.py
Deeper profile on AppleSupport vs SpotifyCares across the entire 2.81M dataset.
"""

import os
import sys
import json
import pandas as pd
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
RAW_DATA_PATH = os.path.join("data", "raw", "twcs.csv")

TARGET_BRANDS = ["SpotifyCares", "AppleSupport"]


def profile_brands():
    print("Loading tweets for targeted profile...")
    # Read only needed columns
    brand_outbound = defaultdict(list)
    inbound_lookup = {}  # tweet_id -> (text, author_id, created_at)

    chunksize = 250_000
    chunk_idx = 0

    total_candidate_pairs = defaultdict(int)

    for chunk in pd.read_csv(
        RAW_DATA_PATH,
        chunksize=chunksize,
        usecols=[
            "tweet_id",
            "author_id",
            "inbound",
            "text",
            "response_tweet_id",
            "in_response_to_tweet_id",
            "created_at",
        ],
        low_memory=False,
    ):
        chunk_idx += 1
        # Store outbound tweets for target brands
        target_chunk = chunk[
            (~chunk["inbound"]) & (chunk["author_id"].isin(TARGET_BRANDS))
        ]
        for _, row in target_chunk.iterrows():
            brand_outbound[row["author_id"]].append(
                {
                    "tweet_id": row["tweet_id"],
                    "in_response_to_tweet_id": row["in_response_to_tweet_id"],
                    "text": row["text"],
                    "created_at": row["created_at"],
                }
            )

        # Store inbound tweets in a dictionary for fast lookup if parent
        inbound_chunk = chunk[chunk["inbound"]]
        for _, row in inbound_chunk.iterrows():
            inbound_lookup[row["tweet_id"]] = (
                row["text"],
                row["author_id"],
                row["created_at"],
            )

        print(
            f"Processed chunk {chunk_idx} (Inbound index: {len(inbound_lookup):,})..."
        )

    print("\nMatching inbound customer tweets with brand responses...")
    results = {}
    for brand in TARGET_BRANDS:
        tweets = brand_outbound[brand]
        matched_pairs = []
        for t in tweets:
            in_resp = t["in_response_to_tweet_id"]
            if pd.notna(in_resp) and in_resp in inbound_lookup:
                cust_text, cust_author, cust_time = inbound_lookup[in_resp]
                matched_pairs.append(
                    {
                        "brand_tweet_id": t["tweet_id"],
                        "cust_tweet_id": in_resp,
                        "customer_text": cust_text,
                        "brand_text": t["text"],
                        "cust_time": cust_time,
                        "brand_time": t["created_at"],
                    }
                )

        results[brand] = {
            "total_brand_tweets": len(tweets),
            "matched_pairs_count": len(matched_pairs),
            "sample_pairs": matched_pairs[:3],
        }
        print(
            f"Brand: {brand} | Total Outbound: {len(tweets):,} | Matched Customer-Agent Pairs: {len(matched_pairs):,}"
        )

    with open(os.path.join("reports", "targeted_profile.json"), "w") as f:
        json.dump(
            {
                k: {
                    "total_brand_tweets": v["total_brand_tweets"],
                    "matched_pairs_count": v["matched_pairs_count"],
                    "sample_pairs": v["sample_pairs"],
                }
                for k, v in results.items()
            },
            f,
            indent=2,
            default=str,
        )

    print("Saved reports/targeted_profile.json")


if __name__ == "__main__":
    profile_brands()
