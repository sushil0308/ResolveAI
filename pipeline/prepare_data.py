"""
prepare_data.py
Robust data preprocessing and leakage-preventing data splitting pipeline.
Extracts, cleans, pairs, deduplicates, and splits customer support conversations.
"""

import os
import sys
import re
import html
import json
import yaml
import pandas as pd
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

CONFIG_PATH = os.path.join("config", "config.yaml")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "brand": {"target_brand": "SpotifyCares"},
        "data": {
            "raw_path": "data/raw/twcs.csv",
            "processed_dir": "data/processed",
            "min_customer_len": 10,
            "min_brand_len": 10,
        },
        "splits": {
            "train_ratio": 0.70,
            "val_ratio": 0.15,
            "test_ratio": 0.15,
            "random_seed": 42,
        },
    }


def clean_text(text: str, is_brand: bool = False) -> str:
    """
    Normalizes text while preserving semantic meaning:
    - Decodes HTML entities
    - Standardizes URLs to [URL]
    - Normalizes numeric user handles @12345 to @user
    - Normalizes whitespace
    """
    if not isinstance(text, str):
        return ""

    # Decode HTML
    t = html.unescape(text)

    # Normalize URLs
    t = re.sub(r"https?://\S+", "[URL]", t)

    # Normalize user handles (@115858 -> @user, keep @SpotifyCares)
    t = re.sub(r"@\d+", "@user", t)

    # Normalize excessive whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def run_pipeline():
    config = load_config()
    target_brand = config["brand"]["target_brand"]
    raw_path = config["data"]["raw_path"]
    processed_dir = config["data"]["processed_dir"]
    splits_dir = os.path.join(processed_dir, "splits")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(splits_dir, exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print(f"=== Running Preprocessing Pipeline for @{target_brand} ===")
    print(f"Reading raw dataset from: {raw_path}")

    # Pass 1: Collect all outbound brand tweets and map all inbound tweets
    brand_outbound = []
    # Fast dict lookup for inbound: tweet_id -> (text, author_id, created_at)
    inbound_lookup = {}

    chunksize = 250_000
    chunk_idx = 0
    total_raw_rows = 0

    cols = [
        "tweet_id",
        "author_id",
        "inbound",
        "created_at",
        "text",
        "response_tweet_id",
        "in_response_to_tweet_id",
    ]

    for chunk in pd.read_csv(raw_path, chunksize=chunksize, usecols=cols, low_memory=False):
        chunk_idx += 1
        total_raw_rows += len(chunk)

        # Brand outbound
        brand_mask = (~chunk["inbound"]) & (chunk["author_id"] == target_brand)
        if brand_mask.any():
            b_sub = chunk[brand_mask]
            for row in b_sub.itertuples(index=False):
                brand_outbound.append({
                    "tweet_id": int(row.tweet_id),
                    "in_response_to_tweet_id": int(row.in_response_to_tweet_id) if pd.notna(row.in_response_to_tweet_id) else None,
                    "text": str(row.text),
                    "created_at": str(row.created_at),
                })

        # Inbound customer tweets
        inbound_mask = chunk["inbound"] == True
        if inbound_mask.any():
            in_sub = chunk[inbound_mask]
            # Vectorized dict building
            in_ids = in_sub["tweet_id"].values
            in_texts = in_sub["text"].values
            in_authors = in_sub["author_id"].values
            in_times = in_sub["created_at"].values

            for tid, txt, auth, tm in zip(in_ids, in_texts, in_authors, in_times):
                inbound_lookup[int(tid)] = (str(txt), str(auth), str(tm))

        print(f"Read chunk {chunk_idx}: {total_raw_rows:,} rows scanned | {len(brand_outbound):,} brand tweets found.")

    print(f"\nTotal raw rows processed: {total_raw_rows:,}")
    print(f"Total @{target_brand} outbound tweets: {len(brand_outbound):,}")
    print(f"Inbound index cache size: {len(inbound_lookup):,}")

    # Pass 2: Reconstruct pairs
    print("\nReconstructing customer-agent conversation pairs...")
    pairs = []
    unmatched_count = 0

    for b in brand_outbound:
        parent_id = b["in_response_to_tweet_id"]
        if parent_id is not None and parent_id in inbound_lookup:
            cust_text, cust_author, cust_time = inbound_lookup[parent_id]
            pairs.append({
                "conversation_id": f"conv_{parent_id}_{b['tweet_id']}",
                "customer_tweet_id": parent_id,
                "brand_tweet_id": b["tweet_id"],
                "customer_author_id": cust_author,
                "brand_author_id": target_brand,
                "customer_created_at": cust_time,
                "brand_created_at": b["created_at"],
                "customer_text_raw": cust_text,
                "brand_text_raw": b["text"],
            })
        else:
            unmatched_count += 1

    print(f"Successfully matched: {len(pairs):,} pairs ({unmatched_count:,} unmatched).")

    df_pairs = pd.DataFrame(pairs)

    # Pass 3: Cleaning & Filtering
    print("\nApplying text normalization and quality filters...")
    df_pairs["customer_text_clean"] = df_pairs["customer_text_raw"].apply(lambda t: clean_text(t, is_brand=False))
    df_pairs["brand_text_clean"] = df_pairs["brand_text_raw"].apply(lambda t: clean_text(t, is_brand=True))

    initial_pair_count = len(df_pairs)

    # Length filters
    min_c_len = config["data"].get("min_customer_len", 10)
    min_b_len = config["data"].get("min_brand_len", 10)

    len_mask = (df_pairs["customer_text_clean"].str.len() >= min_c_len) & \
               (df_pairs["brand_text_clean"].str.len() >= min_b_len)
    df_pairs = df_pairs[len_mask].copy()
    after_len_count = len(df_pairs)
    filtered_len = initial_pair_count - after_len_count

    # Deduplication on clean customer text:
    # Retain the earliest occurrence of identical customer complaints to eliminate bot spam
    df_pairs.sort_values(by="customer_created_at", inplace=True)
    df_pairs.drop_duplicates(subset=["customer_text_clean"], keep="first", inplace=True)
    after_dedup_count = len(df_pairs)
    filtered_duplicates = after_len_count - after_dedup_count

    # Convert timestamps
    # Twitter format typically: "Tue Nov 07 10:04:12 +0000 2017"
    df_pairs["customer_datetime"] = pd.to_datetime(df_pairs["customer_created_at"], errors="coerce")
    # Sort chronologically to support time-aware splitting
    df_pairs.sort_values(by="customer_datetime", inplace=True)
    df_pairs.reset_index(drop=True, inplace=True)

    print(f"Filtered {filtered_len:,} short/empty messages.")
    print(f"Filtered {filtered_duplicates:,} duplicate/spam messages.")
    print(f"Final clean dataset size: {len(df_pairs):,} conversations.")

    # Pass 4: Time-Aware, Conversation-Disjoint Splitting
    print("\nExecuting time-aware, leakage-free dataset split...")
    n_total = len(df_pairs)
    train_end = int(n_total * config["splits"]["train_ratio"])
    val_end = int(n_total * (config["splits"]["train_ratio"] + config["splits"]["val_ratio"]))

    df_train = df_pairs.iloc[:train_end].copy()
    df_val = df_pairs.iloc[train_end:val_end].copy()
    df_test = df_pairs.iloc[val_end:].copy()

    # Verify zero leakage:
    train_texts = set(df_train["customer_text_clean"].values)
    val_overlap = df_val["customer_text_clean"].isin(train_texts).sum()
    test_overlap = df_test["customer_text_clean"].isin(train_texts).sum()

    print(f"Train split: {len(df_train):,} pairs")
    print(f"Val split:   {len(df_val):,} pairs (overlap with train: {val_overlap})")
    print(f"Test split:  {len(df_test):,} pairs (overlap with train: {test_overlap})")

    if val_overlap > 0 or test_overlap > 0:
        print("Warning: Removing unexpected overlaps from val and test splits...")
        df_val = df_val[~df_val["customer_text_clean"].isin(train_texts)].copy()
        val_and_train_texts = train_texts.union(set(df_val["customer_text_clean"].values))
        df_test = df_test[~df_test["customer_text_clean"].isin(val_and_train_texts)].copy()

    # Save processed outputs
    print("\nSaving processed dataset files...")
    clean_csv = os.path.join(processed_dir, "conversations.csv")
    clean_parquet = os.path.join(processed_dir, "conversations.parquet")
    
    df_pairs.to_csv(clean_csv, index=False, encoding="utf-8")
    try:
        df_pairs.to_parquet(clean_parquet, index=False)
    except Exception as e:
        print(f"Notice: Parquet save error ({e}), CSV is primary.")

    # Save splits
    df_train.to_csv(os.path.join(splits_dir, "train.csv"), index=False, encoding="utf-8")
    df_val.to_csv(os.path.join(splits_dir, "val.csv"), index=False, encoding="utf-8")
    df_test.to_csv(os.path.join(splits_dir, "test.csv"), index=False, encoding="utf-8")

    # Generate preprocessing statistics report
    stats = {
        "target_brand": target_brand,
        "total_raw_rows_scanned": total_raw_rows,
        "total_brand_tweets": len(brand_outbound),
        "inbound_cache_size": len(inbound_lookup),
        "matched_pairs_initial": initial_pair_count,
        "filtered_short_length": filtered_len,
        "filtered_duplicates": filtered_duplicates,
        "final_clean_conversations": len(df_pairs),
        "splits": {
            "train_count": len(df_train),
            "val_count": len(df_val),
            "test_count": len(df_test),
            "train_ratio": round(len(df_train) / len(df_pairs), 3),
            "val_ratio": round(len(df_val) / len(df_pairs), 3),
            "test_ratio": round(len(df_test) / len(df_pairs), 3),
        },
        "leakage_verification": {
            "val_overlap_count": int(val_overlap),
            "test_overlap_count": int(test_overlap),
            "leakage_detected": bool(val_overlap > 0 or test_overlap > 0),
        },
        "earliest_timestamp": str(df_pairs["customer_created_at"].iloc[0]),
        "latest_timestamp": str(df_pairs["customer_created_at"].iloc[-1]),
    }

    stats_path = os.path.join("reports", "preprocessing_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\nPreprocessing complete! Summary saved to {stats_path}")
    return stats


if __name__ == "__main__":
    run_pipeline()
