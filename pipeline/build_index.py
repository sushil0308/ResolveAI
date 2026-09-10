"""
build_index.py
Builds the lightweight, high-performance historical case retrieval vector index
strictly from the Train split (28,477 records), guaranteeing zero evaluation leakage.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding="utf-8")

TRAIN_PATH = os.path.join("data", "processed", "splits", "train.csv")
TRAIN_LABELED_PATH = os.path.join("data", "processed", "train_labeled.csv")
INDEX_SAVE_PATH = os.path.join("data", "processed", "retrieval_index.pkl")


def build_retrieval_index():
    print(f"Loading training data from {TRAIN_PATH}...")
    df_train = pd.read_csv(TRAIN_PATH)
    print(f"Total training conversations to index: {len(df_train):,}")

    # Merge with labeled intents where available
    intent_map = {}
    if os.path.exists(TRAIN_LABELED_PATH):
        df_lab = pd.read_csv(TRAIN_LABELED_PATH)
        for _, r in df_lab.iterrows():
            intent_map[r["conversation_id"]] = r["intent"]

    # Build metadata list
    metadata = []
    texts_to_embed = []

    for _, row in df_train.iterrows():
        c_id = str(row["conversation_id"])
        c_text = str(row["customer_text_clean"])
        b_text = str(row["brand_text_clean"])
        intent = intent_map.get(c_id, "general_inquiry")

        metadata.append({
            "conversation_id": c_id,
            "customer_tweet_id": int(row["customer_tweet_id"]) if pd.notna(row["customer_tweet_id"]) else None,
            "customer_message": c_text,
            "brand_response": b_text,
            "intent": intent,
            "timestamp": str(row.get("customer_created_at", "")),
        })
        texts_to_embed.append(c_text)

    print("Fitting retrieval vectorizer (sublinear TF-IDF word+char n-grams)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=35000,
        sublinear_tf=True,
        stop_words="english",
        min_df=2,
    )
    X = vectorizer.fit_transform(texts_to_embed)
    print(f"Matrix shape: {X.shape} (sparsity: {100.0 * X.nnz / (X.shape[0] * X.shape[1]):.2f}%)")

    # Save artifact
    index_data = {
        "vectorizer": vectorizer,
        "matrix": X,
        "metadata": metadata,
        "total_documents": len(metadata),
    }

    os.makedirs(os.path.dirname(INDEX_SAVE_PATH), exist_ok=True)
    joblib.dump(index_data, INDEX_SAVE_PATH, compress=3)
    print(f"Successfully saved retrieval index to {INDEX_SAVE_PATH}")
    print(f"File size: {os.path.getsize(INDEX_SAVE_PATH) / (1024*1024):.2f} MB")
    return index_data


if __name__ == "__main__":
    build_retrieval_index()
