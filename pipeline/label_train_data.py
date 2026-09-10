"""
label_train_data.py
Applies weak supervision / high-precision regex rules grounded in config/intents.yaml
to produce a large, clean labeled training set for baseline ML training.
"""

import os
import sys
import re
import pandas as pd
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

TRAIN_PATH = os.path.join("data", "processed", "splits", "train.csv")
VAL_PATH = os.path.join("data", "processed", "splits", "val.csv")
OUTPUT_TRAIN = os.path.join("data", "processed", "train_labeled.csv")
OUTPUT_VAL = os.path.join("data", "processed", "val_labeled.csv")

# Intent patterns tailored to ensure high precision
PATTERNS = {
    "subscription_billing": re.compile(
        r"\b(charged?|billing|receipt|payment|credit card|refund|sheerid|student discount|cancell?ed?|renewal|renew|charged twice|subscriptio)\b",
        re.IGNORECASE,
    ),
    "account_security_access": re.compile(
        r"\b(password|reset link|hacked|compromised|stolen account|email changed|cant log in|can't log in|login error|locked out)\b",
        re.IGNORECASE,
    ),
    "playback_streaming_issue": re.compile(
        r"\b(buffering|pause|pausing|pauses|skipping|skips|shuffle|repeat|song stops|music stops|cuts out|stutter|volume normalize|distort)\b",
        re.IGNORECASE,
    ),
    "offline_downloads": re.compile(
        r"\b(downloaded?|downloading|downloads|offline mode|greyed out|grayed out|waiting to download|sd card storage)\b",
        re.IGNORECASE,
    ),
    "app_crash_performance": re.compile(
        r"\b(crash|crashes|crashing|freeze|freezes|freezing|black screen|blank screen|closes on open|unresponsive|force closes)\b",
        re.IGNORECASE,
    ),
    "playlist_library_management": re.compile(
        r"\b(playlist|playlists|local files|liked songs|disappeared playlist|syncing local|recover playlist|library vanished)\b",
        re.IGNORECASE,
    ),
    "family_duo_plan": re.compile(
        r"\b(family plan|family account|duo plan|address verification|address does not match|invite link|family member)\b",
        re.IGNORECASE,
    ),
    "device_connectivity": re.compile(
        r"\b(bluetooth|chromecast|carplay|android auto|ps4|xbox|sonos|spotify connect|speaker|airplay)\b",
        re.IGNORECASE,
    ),
    "catalog_licensing": re.compile(
        r"\b(country|region|licens|rights|album missing|song missing|track missing|removed from spotify|censored|clean version|explicit|not on spotify|unavailable|greyed out in|why is .* removed)\b",
        re.IGNORECASE,
    ),
    "feedback_feature_request": re.compile(
        r"\b(feature request|suggest|suggestion|hate the new|bring back|lyrics feature|feedback|ui redesign|terrible update|worst update|new update looks|recommendation)\b",
        re.IGNORECASE,
    ),
}


def label_dataset(input_path, output_path):
    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    texts = df["customer_text_clean"].fillna("").values
    conv_ids = df["conversation_id"].values
    brand_texts = df["brand_text_clean"].fillna("").values
    cust_tweet_ids = df["customer_tweet_id"].values

    labeled_rows = []

    for c_id, t_id, text, b_text in zip(conv_ids, cust_tweet_ids, texts, brand_texts):
        matches = []
        for intent, regex in PATTERNS.items():
            if regex.search(text):
                matches.append(intent)

        # High precision: assign if exactly one pattern matches
        if len(matches) == 1:
            labeled_rows.append({
                "conversation_id": c_id,
                "customer_tweet_id": t_id,
                "customer_text_clean": text,
                "brand_text_clean": b_text,
                "intent": matches[0],
            })

    df_out = pd.DataFrame(labeled_rows)
    df_out.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Saved {len(df_out):,} high-precision labeled examples to {output_path}")
    print(df_out["intent"].value_counts())
    return df_out


if __name__ == "__main__":
    label_dataset(TRAIN_PATH, OUTPUT_TRAIN)
    label_dataset(VAL_PATH, OUTPUT_VAL)
