"""
compare_brands.py
Analyzes candidate brands on conversation metrics, response quality, and structure
to substantiate the data-driven brand selection report.
"""

import os
import json
import re
import pandas as pd
from collections import defaultdict

CANDIDATES = ["AppleSupport", "AmazonHelp", "SpotifyCares", "Uber_Support", "Delta"]
RAW_DATA_PATH = os.path.join("data", "raw", "twcs.csv")


def analyze_candidates():
    print(f"Profiling candidate brands: {CANDIDATES}...")
    brand_stats = {
        b: {
            "outbound_count": 0,
            "inbound_count": 0,
            "paired_conversations": 0,
            "avg_customer_len": 0,
            "avg_brand_len": 0,
            "dm_redirect_count": 0,
            "multiturn_threads": 0,
            "sample_texts": [],
        }
        for b in CANDIDATES
    }

    # First pass: map tweets to detect direct pairs
    # Since reading the full dataset into memory at once might take ~1.5GB RAM,
    # let's process in chunks and collect rows relevant to candidates.
    collected_rows = []
    chunksize = 250_000

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
        ],
        low_memory=False,
    ):
        # We want outbound from candidates OR inbound tweets
        outbound_candidate = (~chunk["inbound"]) & (chunk["author_id"].isin(CANDIDATES))
        collected_rows.append(chunk[outbound_candidate])

    outbound_df = pd.concat(collected_rows, ignore_index=True)
    print(f"Total outbound tweets for candidates: {len(outbound_df):,}")

    for brand in CANDIDATES:
        b_df = outbound_df[outbound_df["author_id"] == brand]
        brand_stats[brand]["outbound_count"] = len(b_df)
        brand_stats[brand]["avg_brand_len"] = (
            float(b_df["text"].str.len().mean()) if len(b_df) > 0 else 0
        )

        # Check DM redirects: contains 'dm', 'direct message', 'private message'
        dm_pattern = re.compile(
            r"\b(dm|direct message|private message)\b", re.IGNORECASE
        )
        dm_count = b_df["text"].str.contains(dm_pattern, regex=True).sum()
        brand_stats[brand]["dm_redirect_count"] = int(dm_count)
        brand_stats[brand]["dm_rate"] = (
            float(dm_count / len(b_df)) if len(b_df) > 0 else 0
        )
        brand_stats[brand]["sample_texts"] = b_df["text"].head(5).tolist()

    print("\n--- Candidate Brand Metrics ---")
    for b in CANDIDATES:
        s = brand_stats[b]
        print(
            f"Brand: @{b:<15} Outbound: {s['outbound_count']:,} | Avg Response Len: {s['avg_brand_len']:.1f} chars | DM Rate: {s['dm_rate']*100:.1f}%"
        )

    with open(os.path.join("reports", "candidate_comparison.json"), "w") as f:
        json.dump(brand_stats, f, indent=2)

    return brand_stats


if __name__ == "__main__":
    analyze_candidates()
