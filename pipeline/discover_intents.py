"""
discover_intents.py
Discovers empirical intent clusters and topic patterns in Spotify customer messages
using TF-IDF n-grams and frequency analysis on the training set.
"""

import os
import sys
import re
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding="utf-8")

TRAIN_PATH = os.path.join("data", "processed", "splits", "train.csv")


def analyze_topics():
    print(f"Loading training data from {TRAIN_PATH}...")
    df = pd.read_csv(TRAIN_PATH)
    texts = df["customer_text_clean"].dropna().tolist()
    print(f"Loaded {len(texts):,} customer messages.")

    # Top unigrams and bigrams
    vec = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=2000,
        stop_words="english",
        min_df=5,
    )
    X = vec.fit_transform(texts)
    terms = vec.get_feature_names_out()
    sums = X.sum(axis=0).A1
    top_indices = sums.argsort()[::-1][:100]

    print("\n--- Top Salient Terms & Phrases in Spotify Customer Inquiries ---")
    for rank, idx in enumerate(top_indices[:40], 1):
        print(f"{rank:2d}. {terms[idx]:<25} (weight: {sums[idx]:.1f})")

    # Group into heuristic clusters and inspect matching counts
    intents_definition = {
        "playback_audio_issue": [
            r"\b(play|playing|plays|skip|skips|skipping|pause|pausing|shuffle|repeat|song stops|cuts out|stutter|sound|volume|buffer|buffering)\b"
        ],
        "offline_download_issue": [
            r"\b(download|downloads|downloaded|downloading|offline|offline mode|greyed out|grayed out|storage|sd card)\b"
        ],
        "subscription_billing": [
            r"\b(charge|charged|billing|bill|subscription|premium|receipt|payment|card|pay|refund|cost|price|discount|student|sheerid|renew|cancel|cancellation)\b"
        ],
        "account_access_security": [
            r"\b(login|log in|logging in|password|reset|hacked|compromised|stolen|email changed|username|access account|logged out|cant log)\b"
        ],
        "app_crash_technical": [
            r"\b(crash|crashes|crashing|freeze|freezes|freezing|blank screen|black screen|closes|bug|glitch|update broke|unresponsive|reinstall)\b"
        ],
        "playlist_library_sync": [
            r"\b(playlist|playlists|local files|library|saved songs|liked songs|disappeared|missing songs|sync|syncing|queue)\b"
        ],
        "device_connectivity": [
            r"\b(bluetooth|chromecast|carplay|android auto|ps4|xbox|alexa|sonos|speaker|connect|car|airplay)\b"
        ],
        "family_duo_plan": [
            r"\b(family|family plan|duo|address|address verification|invite|invitation|member|members|home)\b"
        ],
        "content_availability": [
            r"\b(song missing|album missing|artist|unavailable|country|region|rights|license|explicit|censored)\b"
        ],
        "service_outage_general": [
            r"\b(down|server|is spotify down|outage|offline for everyone|broken|fix this|terrible|hate the new)\b"
        ],
    }

    print("\n--- Heuristic Intent Coverage on Train Set ---")
    matched_counts = Counter()
    unmatched = 0

    sample_by_intent = {k: [] for k in intents_definition}

    for t in texts:
        matched = False
        for intent, patterns in intents_definition.items():
            for p in patterns:
                if re.search(p, t, re.IGNORECASE):
                    matched_counts[intent] += 1
                    matched = True
                    if len(sample_by_intent[intent]) < 5:
                        sample_by_intent[intent].append(t)
                    break
        if not matched:
            unmatched += 1

    total = len(texts)
    for intent, cnt in matched_counts.most_common():
        print(f"Intent: {intent:<25} Count: {cnt:6,d} ({cnt/total*100:4.1f}%)")
    print(f"Unmatched/General inquiries: {unmatched:6,d} ({unmatched/total*100:4.1f}%)")

    return matched_counts, sample_by_intent


if __name__ == "__main__":
    analyze_topics()
