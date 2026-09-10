# Empirical Data Leakage Audit Report

**Date**: 2026-09-11  
**Target Evaluation Set**: `evaluation/golden_set.csv` (200 test cases)  
**Comparison Corpora**:
- Training Set: `data/processed/splits/train.csv` (28,477 records)
- Tuning / Validation Set: `data/processed/splits/val.csv` (6,102 records)
- Historical Retrieval Index: `data/processed/retrieval_index.pkl` (28,477 indexed cases)

---

## 1. Executive Summary

A strict normalized text and conversation ID collision audit was conducted across all 200 cases of the Golden Evaluation Set to ensure absolute test-set integrity and prevent data leakage.

| Audit Surface | Metric Name | Result | Assessment |
| :--- | :--- | :---: | :--- |
| **Retrieval Index** | `retrieval_overlap_count` | **0** | **Clean**: Zero conversational or text collision |
| **Retrieval Index (Conv IDs)** | `retrieval_conv_overlap_count` | **0** | **Clean**: Zero conversation overlap |
| **Training Split** | `training_overlap_count` | **2** | **Trivial Courtesy**: Non-substantive greetings |
| **Tuning / Val Split** | `tuning_overlap_count` | **2** | **Trivial Courtesy**: Non-substantive greetings |

---

## 2. Collision Breakdown & Affected Examples

Normalized text matching (stripping punctuation, case folding, and whitespace normalization) identified **2 text collisions** against training and validation splits. Both collisions involve ultra-short generic gratitude expressions under the `feedback_appreciation` intent:

### Collision 1: `gold_191`
- **Golden Set Case ID**: `gold_191` (Intent: `feedback_appreciation`)
- **Golden Message**: `@SpotifyCares Thank you 🙂` (Conv ID: `conv_554147_554149`)
- **Matched Training Record**: `@SpotifyCares thank you 💖💖` (Conv ID: `conv_233147_233146`)
- **Matched Validation Record**: `@SpotifyCares THANK YOU!!` (Conv ID: `conv_2584495_2584497`)
- **Root Cause**: The normalized representation `spotifycares thank you` is a ubiquitous Twitter support closing. The actual conversation threads and underlying user IDs are distinct.

### Collision 2: `gold_194`
- **Golden Set Case ID**: `gold_194` (Intent: `feedback_appreciation`)
- **Golden Message**: `@SpotifyCares thank you` (Conv ID: `conv_466811_466810`)
- **Matched Training Record**: `@SpotifyCares thank you 💖💖` (Conv ID: `conv_233147_233146`)
- **Matched Validation Record**: `@SpotifyCares THANK YOU!!` (Conv ID: `conv_2584495_2584497`)
- **Root Cause**: Identical trivial courtesy text collision.

---

## 3. Substantive Inquiry & Problem Case Analysis

When filtering for substantive support inquiries (>15 characters, excluding generic greetings/pleasantries):
- **Substantive Problem Inquiries Overlap**: **0 / 198 (0.00%)**
- **Zero Technical Leakage**: None of the technical troubleshooting, billing queries, playlist bugs, account recovery, or cancellation scenarios in the Golden Set appear in the training or retrieval data.
- **Zero Retrieval Index Leakage**: The retrieval vector space and metadata store contain zero cases from the 200 Golden evaluation conversations, ensuring RAG evaluation (Recall@K, MRR) evaluates genuinely unseen user problems.

---

## 4. Verification Protocol

The audit was executed via `scripts/leakage_detector.py` using direct pairwise set intersections over normalized tokens and source conversation identifiers.
