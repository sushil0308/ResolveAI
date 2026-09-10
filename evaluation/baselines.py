"""
baselines.py
Implements and evaluates Baseline 1 (Majority Class) and Baseline 2 (TF-IDF + Logistic Regression)
against the isolated Golden Evaluation Set (evaluation/golden_set.csv).
Outputs metrics, confusion matrices, and per-class reports.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

sys.stdout.reconfigure(encoding="utf-8")

GOLDEN_PATH = os.path.join("evaluation", "golden_set.csv")
TRAIN_LABELED_PATH = os.path.join("data", "processed", "train_labeled.csv")
VAL_LABELED_PATH = os.path.join("data", "processed", "val_labeled.csv")
MODEL_SAVE_PATH = os.path.join("data", "processed", "baseline_tfidf_model.pkl")
RESULTS_DIR = "evaluation"


class MajorityClassBaseline:
    """Baseline 1: Predicts the most frequent training class unconditionally."""

    def __init__(self):
        self.majority_class_ = None

    def fit(self, y_train):
        counts = pd.Series(y_train).value_counts()
        self.majority_class_ = counts.index[0]
        print(f"MajorityClassBaseline fit: Majority class is '{self.majority_class_}' (freq: {counts.iloc[0]})")
        return self

    def predict(self, texts):
        return np.array([self.majority_class_] * len(texts))


class TfidfLogisticBaseline:
    """Baseline 2: Classical TF-IDF n-grams + L2-regularized Logistic Regression."""

    def __init__(self, C=2.0, ngram_range=(1, 2), max_features=10000):
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            sublinear_tf=True,
            stop_words="english",
        )
        self.classifier = LogisticRegression(
            C=C,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )
        self.classes_ = None

    def fit(self, texts, labels):
        print(f"Fitting TF-IDF on {len(texts):,} training samples...")
        X = self.vectorizer.fit_transform(texts)
        print("Training Logistic Regression classifier...")
        self.classifier.fit(X, labels)
        self.classes_ = self.classifier.classes_
        return self

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        return self.classifier.predict(X)

    def predict_proba(self, texts):
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)


def evaluate_predictions(y_true, y_pred, labels, model_name="Model"):
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    per_class_prec, per_class_rec, per_class_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )

    per_class_results = {}
    for i, label in enumerate(labels):
        per_class_results[label] = {
            "precision": round(float(per_class_prec[i]), 4),
            "recall": round(float(per_class_rec[i]), 4),
            "f1": round(float(per_class_f1[i]), 4),
        }

    conf_mat = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    report = {
        "model_name": model_name,
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(prec), 4),
        "macro_recall": round(float(rec), 4),
        "macro_f1": round(float(f1), 4),
        "per_class": per_class_results,
        "labels": list(labels),
        "confusion_matrix": conf_mat,
    }
    return report


def run_baselines():
    print("=== Running Baselines Evaluation ===")
    print(f"Loading Golden Set from {GOLDEN_PATH}...")
    df_gold = pd.read_csv(GOLDEN_PATH)
    y_gold = df_gold["intent"].values
    X_gold = df_gold["customer_message"].values

    print(f"Loading Training Data from {TRAIN_LABELED_PATH}...")
    df_train = pd.read_csv(TRAIN_LABELED_PATH)
    X_train = df_train["customer_text_clean"].values
    y_train = df_train["intent"].values

    unique_labels = sorted(list(df_gold["intent"].unique()))
    print(f"Unique intent labels ({len(unique_labels)}): {unique_labels}")

    # --- Baseline 1: Majority Class ---
    print("\n--- Evaluating Baseline 1: Majority Class Predictor ---")
    b1 = MajorityClassBaseline().fit(y_train)
    y_pred_b1 = b1.predict(X_gold)
    b1_results = evaluate_predictions(y_gold, y_pred_b1, unique_labels, "Baseline 1: Majority Class")

    print(f"Baseline 1 Accuracy: {b1_results['accuracy']*100:.2f}%")
    print(f"Baseline 1 Macro F1: {b1_results['macro_f1']*100:.2f}%")

    # --- Baseline 2: TF-IDF + Logistic Regression ---
    print("\n--- Evaluating Baseline 2: TF-IDF + Logistic Regression ---")
    b2 = TfidfLogisticBaseline(C=2.0)
    b2.fit(X_train, y_train)

    # Save model artifact
    joblib.dump({"vectorizer": b2.vectorizer, "classifier": b2.classifier}, MODEL_SAVE_PATH)
    print(f"Saved trained Baseline 2 model to {MODEL_SAVE_PATH}")

    y_pred_b2 = b2.predict(X_gold)
    b2_results = evaluate_predictions(y_gold, y_pred_b2, unique_labels, "Baseline 2: TF-IDF + Logistic Regression")

    print(f"Baseline 2 Accuracy: {b2_results['accuracy']*100:.2f}%")
    print(f"Baseline 2 Macro F1: {b2_results['macro_f1']*100:.2f}%")
    print(f"Baseline 2 Macro Precision: {b2_results['macro_precision']*100:.2f}%")
    print(f"Baseline 2 Macro Recall: {b2_results['macro_recall']*100:.2f}%")

    # Save baseline results JSON
    baselines_output = {
        "baseline_1_majority": b1_results,
        "baseline_2_tfidf_logistic": b2_results,
    }

    out_file = os.path.join(RESULTS_DIR, "baseline_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(baselines_output, f, indent=2)

    print(f"\nSaved baseline evaluation results to {out_file}")
    return baselines_output


if __name__ == "__main__":
    run_baselines()
