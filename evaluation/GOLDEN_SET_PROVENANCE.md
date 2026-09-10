# Golden Evaluation Dataset Provenance & Methodology

**Dataset Artifact**: `evaluation/golden_set.csv` (200 test cases)  
**Machine Verification Artifact**: `evaluation/golden_set_machine_verified.csv`  
**Review Flags Artifact**: `evaluation/golden_set_review_flags.csv`  
**Evaluation Scope**: Benchmark dataset for Intent Classification, RAG Case Retrieval, Escalation Safety, and Reply Quality.

---

## 1. Provenance Statement & Integrity Declaration

> **Scientific Integrity Notice**:  
> The 200-example Golden Evaluation Set is a **curated 200-example evaluation set with automated/AI-assisted verification**.  
> It is **NOT** claimed to be "200 hand-labelled examples". Human verification in this repository is strictly restricted to the **40 representative single-blind human annotations** manually recorded in `evaluation/human_annotations.csv`.

---

## 2. Original Data Source

- **Raw Origin**: Twitter Customer Support Corpus (`data/raw/twcs.csv`), subsetted strictly to the `@SpotifyCares` support handle.
- **Corpus Scale**: 66,742 total interaction turns across Spotify customer support conversations.
- **Preprocessing**: Grouped into two-turn conversation pairs $(u_i, r_i)$ where $u_i$ is an inbound customer query and $r_i$ is the official brand support response.
- **Normalization**: User handle masking (`@user`, `@SpotifyCares`), URL canonicalization (`[URL]`), and whitespace deduplication.

---

## 3. Train / Validation / Test Splitting Strategy

- **Splitting Unit**: All splits were partitioned at the **conversation ID level** rather than the individual tweet level, preventing thread leakage:
  - **Training Split (`data/processed/splits/train.csv`)**: 28,477 records (80%)
  - **Validation / Tuning Split (`data/processed/splits/val.csv`)**: 6,102 records (20%)
  - **Golden Evaluation Set (`evaluation/golden_set.csv`)**: 200 cases isolated for evaluation.
- **Retrieval Index Barrier**: The BM25 / TF-IDF retrieval index (`data/processed/retrieval_index.pkl`) indexes only training split conversations. Zero Golden Set conversation IDs exist in the retrieval index.

---

## 4. Sampling Strategy & Class Balance

- **Intent Coverage**: Evaluates across all 10 customer support taxonomies:
  1. `playback_streaming_issue` (20 examples)
  2. `subscription_billing` (20 examples)
  3. `account_access` (20 examples)
  4. `playlist_library_management` (20 examples)
  5. `offline_listening_downloads` (20 examples)
  6. `device_connectivity` (20 examples)
  7. `catalog_licensing` (20 examples)
  8. `family_duo_plan` (20 examples)
  9. `app_crash_performance` (20 examples)
  10. `feedback_feature_request` (20 examples)
- **Class Stratification**: Exactly 20 examples per intent class ($10\%$ uniform distribution) to prevent majority-class bias from obscuring minority failure modes.
- **Escalation Split**: 158 auto-handleable technical triage cases ($79.0\%$) and 42 human-escalation cases ($21.0\%$) covering sensitive billing disputes, legal requests, account security, and explicit human escalation requests.

---

## 5. Automated Verification Methodology

To verify the 200 cases without manual entry or fabricating human provenance:
1. **Model & Rule Ensemble**: Each case was evaluated using `SupportAgentPipeline` (`scripts/verify_golden_set.py`), inspecting:
   - Inbound customer message text.
   - Ground truth intent vs. multi-class classification prediction and softmax confidence.
   - Escalation policy concordance (security/billing/legal escalation criteria).
   - Historical brand reply alignment.
2. **Confidence Assignment**:
   - High concordance (intent & escalation agreement): Confidence $0.85 - 0.98$.
   - Moderate concordance (intent agreement with minor routing divergence): Confidence $0.75 - 0.90$.
   - Flagged cases: Flagged with explicit diagnostic rationale.
3. **Artifact Output**:
   - `evaluation/golden_set_machine_verified.csv`: Full 200 cases annotated with `verification_method`, `verification_confidence`, `machine_verified`, and `machine_reason`. `human_verified` is explicitly set to `False`.
   - `evaluation/golden_set_review_flags.csv`: 4 flagged borderline cases requiring domain review (e.g. `gold_005` Google Play Card balance issue labeled as `playback_streaming_issue`).

---

## 6. Leakage Prevention & Audit Results

As documented in `reports/leakage_audit.md`:
- **Retrieval Index Overlap**: **0 / 200 (0.0%)**. No golden conversation IDs or customer text exist in the retrieval index.
- **Substantive Training Text Overlap**: **0 / 198 (0.0%)**. Zero technical, billing, account, or playlist queries appear in the training corpus.
- **Trivial Courtesy Overlap**: 2 generic closing pleasantries (`@SpotifyCares thank you`) matched ubiquitous greeting phrases across splits, with zero overlap in technical issue content.

---

## 7. Known Limitations

1. **Balanced Distribution vs. Production Skew**: In live Twitter support traffic, billing and playback complaints represent $>35\%$ of volume, whereas the Golden Set enforces a uniform $10\%$ balance.
2. **Historical Policy Drift**: Historical Twitter support precedents reflect policies at the time of tweet publication and may differ from contemporary Spotify tier rules.
3. **Machine Verification Upper Bound**: AI-assisted verification is susceptible to classifier blind spots on ambiguous slang or multi-intent requests.
