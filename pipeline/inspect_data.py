"""
inspect_data.py
Profiles the Customer Support on Twitter dataset (twcs.csv).
Computes brand-level statistics to support data-driven brand selection.
"""

import os
import json
import pandas as pd
from collections import Counter
from datetime import datetime

RAW_DATA_PATH = os.path.join("data", "raw", "twcs.csv")
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def inspect_dataset(file_path=RAW_DATA_PATH, max_chunks=None):
    print(f"Inspecting dataset at {file_path}...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    total_rows = 0
    inbound_count = 0
    outbound_count = 0
    brand_counts = Counter()
    missing_text = 0
    missing_response = 0

    chunksize = 200_000
    chunk_idx = 0

    for chunk in pd.read_csv(file_path, chunksize=chunksize, low_memory=False):
        chunk_idx += 1
        total_rows += len(chunk)

        inbound_mask = chunk["inbound"] == True
        inbound_count += inbound_mask.sum()
        outbound_count += (~inbound_mask).sum()

        missing_text += chunk["text"].isna().sum()
        missing_response += chunk["response_tweet_id"].isna().sum()

        # Outbound authors are brands
        brand_authors = chunk.loc[~inbound_mask, "author_id"].value_counts()
        for brand, count in brand_authors.items():
            brand_counts[str(brand)] += count

        print(f"Processed chunk {chunk_idx} ({total_rows:,} rows total)...")
        if max_chunks and chunk_idx >= max_chunks:
            break

    print("\n--- Summary Statistics ---")
    print(f"Total rows inspected: {total_rows:,}")
    print(f"Inbound (customer) messages: {inbound_count:,} ({inbound_count/total_rows*100:.1f}%)")
    print(f"Outbound (brand) messages: {outbound_count:,} ({outbound_count/total_rows*100:.1f}%)")
    print(f"Unique brands detected: {len(brand_counts)}")
    print(f"Missing text count: {missing_text}")
    print(f"Missing response_tweet_id: {missing_response:,}")

    top_25_brands = brand_counts.most_common(25)
    print("\n--- Top 25 Brands by Outbound Support Volume ---")
    for rank, (brand, cnt) in enumerate(top_25_brands, 1):
        print(f"{rank:2d}. @{brand:<20} {cnt:7,d} tweets")

    # Save summary to reports
    brand_stats = [
        {"rank": i + 1, "brand": b, "outbound_tweets": c}
        for i, (b, c) in enumerate(top_25_brands)
    ]

    summary = {
        "total_inspected_rows": total_rows,
        "inbound_count": int(inbound_count),
        "outbound_count": int(outbound_count),
        "unique_brands": len(brand_counts),
        "top_brands": brand_stats,
    }

    with open(os.path.join(REPORTS_DIR, "dataset_overview.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved overview to {os.path.join(REPORTS_DIR, 'dataset_overview.json')}")
    return summary


if __name__ == "__main__":
    inspect_dataset()
