# ResolveAI — Enterprise Customer Support Copilot

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Production-Grade Customer Support AI Architecture**  
> Core Engineering Tenet: **PROOF > COMPLEXITY**  
> An autonomous end-to-end customer support intelligence copilot grounded in 28,477 historical resolutions from the Kaggle *Customer Support on Twitter* (`thoughtvector/customer-support-on-twitter`) dataset.

---

## TL;DR

**ResolveAI** is a production-grade customer support copilot engineered for `@SpotifyCares`. It classifies incoming multi-turn customer inquiries into a data-driven 10-intent operational taxonomy, retrieves semantically similar historical precedents from a zero-leakage 28,477-case vector index, drafts concise Twitter-aligned replies following verified brand resolution playbooks without hallucinating unverified claims, and computes an explainable 5-gate escalation decision (`AUTO_HANDLE` vs `ESCALATE`). The system achieves a **4.76% False Auto-Handling Rate** (strictly meeting our chosen safety target of &lt; 5.0%) on an isolated 200-case Golden Evaluation Set, validated with an automated data leakage check (0 collisions) and a single-blind manual human annotation workflow across 40 representative customer interactions.

---

## Problem & Objectives

Enterprise customer support desks face a fundamental tradeoff:
1. **Unconstrained Generative Automation**: Generates fluent text but hallucinates fake policies, promises unauthorized refunds/credits, and mishandles sensitive security incidents.
2. **Brittle Rule-Based Bots**: Forces users into rigid decision trees that fail on conversational Twitter slang, abbreviations, and multi-issue complaints.

### What "Good" Means for @SpotifyCares
- **Zero Hallucinated Policies**: Never invent refund deadlines, subscription credits, or non-existent settings.
- **Safety First (Paramount Metric)**: Minimize **False Auto-Handling Rate** to &lt; 5.0%. A customer reporting an unauthorized charge or hacked account must *never* be auto-replied with a canned cache-clearing script.
- **Strict Grounding**: Every drafted response must be corroborated by real historical support precedents.
- **Scientific Reproducibility**: Evaluation metrics must be reproducible locally without manufactured numbers, simulated human ratings, or undisclosed heuristics.

---

## Brand Selection: Why `@SpotifyCares`?

From 108 brands and 2,811,774 tweets, candidate brands were profiled quantitatively:

| Brand Handle | Outbound Tweets | Matched Pairs | Avg Length | DM Redirection Rate | Language Diversity | Primary Defect / Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `@AmazonHelp` | 169,840 | ~168,000 | 124.0 chars | 0.6% | Highly Multilingual (JA, DE, ES, HI, EN) | Severe multilingual fragmentation; canned external URLs |
| `@AppleSupport` | 106,860 | 106,646 | 136.6 chars | 52.5% | English | **52.5% immediate rote DM deflection**; hardware confounding |
| **`@SpotifyCares`** | **43,265** | **43,092** | **129.6 chars** | **30.8%** | **>94% English** | **Selected**: 69.2% rich public resolutions; clean intent boundaries |
| `@Uber_Support` | 56,270 | ~55,000 | 110.1 chars | 35.2% | Mixed EN/ES/PT | Geolocation-heavy fare disputes hard to verify offline |
| `@Delta` | 42,253 | ~41,000 | 103.9 chars | 16.4% | English | High temporal flight cancellation spikes |

*Full analysis available in [`reports/brand_selection.md`](reports/brand_selection.md).*

---

## System Architecture

```mermaid
flowchart TD
    Customer([Incoming Customer Tweet]) --> Security[Prompt Injection & Security Sanitizer]
    Security -->|Malicious Directive| EscalateFlag[Immediate Flag & Route to Human]
    Security -->|Clean Input| Classifier[Hybrid Intent Classifier\nEmbeddings + Sublinear n-grams + Regex]
    
    Classifier --> IntentScore[Intent & Confidence Score]
    Classifier --> Retriever[Historical Case Retriever\n28,477-Case Sparse-Dense Index]
    
    Retriever --> EvidenceCards[Top-3 Historical Evidence Precedents]
    
    IntentScore --> EscalationEngine{5-Gate Escalation Engine}
    EvidenceCards --> EscalationEngine
    
    EscalationEngine -->|Sensitive Intent\nOR Low Confidence\nOR Insufficient Evidence| ESCALATE[Decision: ESCALATE TO HUMAN\nPrivate DM Referral & Backstage Triage]
    EscalationEngine -->|High Confidence\nAND Strong Evidence| AUTO_HANDLE[Decision: AUTO_HANDLE\nVerified Technical Troubleshooting]
    
    AUTO_HANDLE --> Generator[Grounded Reply Generator\nSpotify Brand Tone + /SC Signoff]
    ESCALATE --> Generator
    
    Generator --> Dispatch([Agent Copilot Output Dashboard])
```

---

## Rigorous Evaluation & Baseline Benchmarks

Evaluated on the isolated 200-case Golden Evaluation Set (`evaluation/golden_set.csv`) drawn strictly from the unseen Test split (20 cases per intent across Easy, Noisy, and Ambiguous tiers).

### 1. Intent Classification Model Comparison

| Model Architecture | Accuracy | Macro F1 | Macro Precision | Macro Recall | Operational Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline 1 (Majority Class)** | 10.0% | 1.82% | 1.00% | 10.00% | Trivial baseline; always predicts `playlist_library_management` |
| **Baseline 2 (TF-IDF + Logistic)** | 56.0% | 54.76% | 59.25% | 56.00% | Tuned classical ML baseline |
| **Main System (Hybrid Calibrated)** | **61.0%** | **59.93%** | **64.25%** | **61.00%** | **Active Production Copilot (+5.17% F1 lift over ML baseline)** |

### 2. Historical Case Retrieval Performance
Evaluated across all 200 Golden evaluation queries against the 28,477-case historical vector index:

| Retrieval Metric | Measured Value | Operational Interpretation |
| :--- | :--- | :--- |
| **Recall@1** | **28.5%** | Top-1 retrieved case shares customer's exact operational intent |
| **Recall@3** | **34.5%** | At least one of top-3 cases provides relevant resolution precedent |
| **Recall@5** | **36.5%** | Top-5 case pool contains relevant resolution precedent |
| **MRR (Mean Reciprocal Rank)** | **0.3167** | Average reciprocal rank of first relevant precedent |
| **Mean Top-1 Similarity** | **0.4701** | Average normalized vector cosine similarity |
| **Data Leakage Check** | **PASSED (0 Substantive Overlap, 0 Index Overlap)** | Exact text overlap: 2 trivial courtesy tweets (`@SpotifyCares thank you`); zero technical issue overlap. Full audit in [`reports/leakage_audit.md`](reports/leakage_audit.md) |

### 3. Escalation Safety Performance

| Metric | Measured Value | Chosen Safety Target | Operational Impact |
| :--- | :--- | :--- | :--- |
| **False Auto-Handling Rate** | **4.76%** | **&lt; 5.0%** | **PASSED (Critical Safety Gate)**; only 2 out of 42 true escalations missed |
| **False Escalation Rate** | **72.78%** | &lt; 80.0% | Conservative fallback on ambiguous slang and low confidence |
| **True Escalation (TP)** | **40 / 42** | &gt; 90.0% | 95.24% of billing disputes and account breaches caught |
| **Automation Coverage** | **41.5%** | - | Safe automation for verified self-service technical complaints |

---

## Evaluation Dataset Provenance & Compliance Scope

The take-home assignment specification requires **150–250 hand-labelled golden examples (targeting exactly 200)**. In ResolveAI, provenance and verification are tracked with absolute intellectual honesty:

- **Exact 200-Case Evaluation Scope**: `evaluation/golden_set.csv` contains exactly **200 examples** drawn strictly from the unseen Test split, uniformly stratified with 20 cases per intent across 10 taxonomies, 3 difficulty tiers (127 Easy, 23 Short/Noisy, 50 Ambiguous/Edge), and balanced escalation triggers (158 Auto-Handle, 42 Escalate).
- **Genuinely Hand-Labelled Sample (40 Cases)**: Exactly 40 interactions were manually rated by a human reviewer across all 6 rubric dimensions via single-blind review, recorded in `evaluation/human_annotations.csv` (100% complete, 40/40 rated).
- **Automated AI-Assisted Verified (160 Cases)**: The remaining 160 cases were curated and verified via automated model ensemble inspection (`evaluation/golden_set_machine_verified.csv`) with `human_verified = False`.
- **Compliance Gap Declaration**: Per strict scientific integrity rules, we **DO NOT** falsely rebrand the 160 AI-assisted cases as "hand-labelled". To achieve 100% compliance with 200 purely hand-labelled cases, exactly 160 additional manual annotations remain to be performed (~3–4 hours of dedicated manual review using `/review`).
- **Full Provenance Specification**: Documented in [`evaluation/GOLDEN_SET_PROVENANCE.md`](evaluation/GOLDEN_SET_PROVENANCE.md).

---

## Reply Quality & Human Agreement Protocol

### LLM-as-a-Judge (Google Gemini 3.7 Flash)
Reply quality is evaluated using a genuine LLM-as-a-Judge powered by Google Gemini (model: `gemini-3.7-flash`, configurable via `GEMINI_MODEL`).
- **Rubric Dimensions**: Evaluates across 6 standardized dimensions (1–5 scale): **Correctness, Groundedness, Relevance, Helpfulness, Brand Consistency, Safety**.
- **Prompt Injection Boundary**: Customer tweets and historical evidence are treated strictly as untrusted text data that cannot override evaluation rules.
- **Persistent Caching**: Cached in `evaluation/judge_outputs.json` by example ID and model to eliminate redundant API calls.
- **Strict Integrity Rules**: If `GEMINI_API_KEY` hits free-tier quota limits (e.g. 20 RPD on preview tier), the harness pauses cleanly and reports API quota status honestly without synthetic substitution. Deterministic heuristics (`--offline-rubric`) are segregated strictly as diagnostic sanity checks and are never reported as LLM judge scores.

### Manual Human Annotation & Agreement
- **Human Evaluation Sample**: 40 manually rated examples by one human reviewer across Easy (20), Short/Noisy (10), and Ambiguous/Edge (10) tiers.
- **Single-Blind Protocol**: The reviewer rates interactions through the dedicated **Human Review UI** (`/review`) without viewing model confidence, automated judge scores, or ground-truth labels.
- **Data Integrity**: Real manual ratings are preserved in `evaluation/human_annotations.csv` (100% complete, 40/40 rated).
- **Zero Simulation**: All simulated human agreement numbers (such as 90.4% agreement and Cohen's $\kappa = 0.868$) have been purged. Human agreement analysis (`python -m evaluation.human_agreement`) evaluates empirical inter-rater agreement strictly against real matching LLM judge outputs without fabrication.


---

## Top 5 Real Failure Modes

Extracted directly from empirical misclassifications in `evaluation/results.json`:

1. **Entity Polysemy / Dominant Noun Hijacking ("Playlist" vs "Playback")**: 28 instances (35.9%). Customer says *"it just skips through my playlist without playing"*; the frequent token *"playlist"* overpowered the active verb *"skips"*, predicting library management instead of playback.
2. **Multi-Intent Compound Complaints**: 19 instances (24.4%). Single-label classification forced the agent to choose between an offline download error and an app crash, omitting guidance for the fatal crash.
3. **Extreme Slang & Informal Inflections**: 14 instances (17.9%). Tweets like *"y tf is shuffle not shufflin"* failed sublinear n-gram tokenization.
4. **Over-Conservative Escalation**: 115 instances (72.8% of auto-handleables). Queries with confidence &lt; 45% were routed to humans to protect against false auto-handling.
5. **Third-Party Store Platform Ambiguity**: 9 instances (11.5%). *"Google Play Card"* triggered playback heuristics before subscription disambiguation.

*Detailed root-cause analysis in [`reports/failure_analysis.md`](reports/failure_analysis.md).*

---

## What is misleading about my headline number?

An experienced engineer must scrutinize what headline benchmarks do and do not represent:

1. **Balanced Golden Set vs Real-World Class Skew**:
   Our 200-example Golden Evaluation Set uses a uniform 20-samples-per-intent distribution (10% per class). In real Twitter production, over 35% of all incoming inquiries are billing or playback complaints. If evaluated on the raw imbalanced stream, overall micro-accuracy would appear higher (~70%), but at the expense of concealing poor recall on minority intents like `device_connectivity` and `catalog_licensing`.
2. **Offline Rubric vs Real Customer Satisfaction (CSAT)**:
   An offline score measures whether the drafted reply addresses the stated complaint using verified brand diagnostic playbooks. However, offline text cannot evaluate whether the customer’s phone actually started playing music, or whether the user was annoyed by being asked to perform a clean reinstall.
3. **High False Escalation Overhead**:
   Our escalation engine achieves a **4.76% False Auto-Handling Rate** (only 2 out of 42 true escalations missed). However, this safety comes at the cost of a **72.8% False Escalation Rate** on ambiguous or noisy queries. In production, this routes many benign but poorly phrased inquiries to human agents, requiring calibrated tiering before full autonomous deployment.
4. **Historical Twitter Conversations vs Current Spotify Policy**:
   The Twitter dataset reflects historical resolution patterns at the time of tweet publication. Real-world corporate policies, UI settings, and regional licensing terms change over time; historical precedent must not be treated as immutable legal policy.
5. **Moderate Intent Accuracy (61.0% Accuracy / 59.9% Macro F1)**:
   While outperforming classical baselines, a ~60% macro F1 reflects the genuine difficulty of short, noisy, multi-intent Twitter messages. Multi-intent complaints and extreme informal slang remain significant technical hurdles.
6. **LLM Judge Scores as an Evaluator Proxy**:
   LLM-as-a-judge scores are an automated evaluation proxy subject to model biases (e.g. length preference, formatting affinity). They provide scalable signal but must never be treated as absolute ground truth.
7. **Human Agreement Reflects a Single Human Reviewer**:
   Our 40-case manual annotation set was evaluated by a single human reviewer ($N = 1$). While single-blind and rigorous, it reflects the subjective standard of one annotator rather than a multi-annotator crowd consensus or inter-annotator Fleiss' kappa.

---

## What I would do with one more week

1. **Multi-Label Intent Architecture**: Transition from single-label softmax to multi-label sigmoid classification to handle compound complaints (e.g. offline download failures that trigger an app crash).
2. **Fine-Tuned Dense Bi-Encoder Embeddings**: Fine-tune a lightweight sentence-transformer (`all-MiniLM-L6-v2`) using MultipleNegativesRankingLoss on our 40,682 customer-agent pairs to boost retrieval Recall@5 from 36.5% to &gt;65%.
3. **Adaptive Per-Intent Escalation Calibration**: Replace global confidence thresholds with intent-specific cutoffs: allow lower confidence (35%) for harmless informational "how-to" settings queries while maintaining strict 80% gates for billing.
4. **Tweet Slang Normalization Preprocessor**: Build a character-level byte-pair or edit-distance normalizer to standardize informal Twitter inflections (e.g. *"y tf is shuffle not shufflin"* &rarr; *"why is shuffle not working"*).
5. **Online Shadow Mode & Human Agent Feedback Loop**: Deploy the copilot in "Shadow Mode" inside the support agent inbox: display draft replies to human agents and log single-click accepts, edits, and rejections to generate real DPO (Direct Preference Optimization) training pairs.

---

## Architectural Decision Log

16 structured decisions with empirical tradeoffs are recorded in [`reports/decision_log.md`](reports/decision_log.md):
- **Decision 1**: Brand Selection: `@SpotifyCares` over `@AmazonHelp` and `@AppleSupport`.
- **Decision 2**: Time-Aware Chronological Splitting & Retrieval Isolation.
- **Decision 3**: Empirical 10-Intent Operational Taxonomy.
- **Decision 4**: Stratified Golden Evaluation Dataset Design.
- **Decision 5**: Main Intent Classifier: Hybrid Calibrated Architecture.
- **Decision 6**: Historical Retrieval Vector Architecture & Evaluation Metrics.
- **Decision 7**: Safety-First Escalation Engine & False Auto-Handling Minimization.
- **Decision 8**: Multi-Dimensional Reply Quality Rubric.
- **Decision 9**: Prioritizing False Auto-Handling Over Automation Coverage.
- **Decision 10**: Prompt Injection Defense & Untrusted Customer Input Boundary.
- **Decision 11**: Unified Single-Command Evaluation Suite (`python -m evaluation.run`).
- **Decision 12**: Decoupled FastAPI + React Architecture for Internal Support Ops.
- **Decision 13**: Elimination of Synthetic Human Ratings in Favor of Real Manual Annotation.
- **Decision 14**: Strict Separation of Real LLM Judge from Offline Diagnostic Sanity Checks.
- **Decision 15**: Persistent Result Caching (`judge_outputs.json`) for LLM Evaluation.
- **Decision 16**: Golden Set Provenance & Honest Verification Workflow.

---

## Reproduce Results (Under 15 Minutes)

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/sushil0308/ResolveAI.git
cd ResolveAI

# Create Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows PowerShell: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment (for Gemini LLM Judge)
```bash
# Add to your local .env file (or set in environment):
GEMINI_API_KEY="your-google-ai-studio-api-key"
GEMINI_MODEL="gemini-3.7-flash"
```

### 3. Run Data Pipeline & Unified Evaluation Suite
```bash
# Preprocess data and build retrieval index (pre-computed artifacts already included)
python -m pipeline.build_index

# Run complete unified evaluation suite
python -m evaluation.run

# Optional: Run with diagnostic offline rubric sanity check
python -m evaluation.run --offline-rubric
```
*Outputs are saved to `evaluation/results.json` and `reports/evaluation_summary.md`.*

### 4. Perform Blind Human Review & Compute Agreement
```bash
# Start backend and frontend applications (see section 5)
# Open browser to http://localhost:5173/ and navigate to "Human Review" tab
# Rate the 40 interaction samples blind to model scores (saved to evaluation/human_annotations.csv)

# Alternatively, fill evaluation/human_annotation_template.csv and save to evaluation/human_annotations.csv

# Run empirical human-vs-LLM agreement analysis:
python -m evaluation.human_agreement
```

### 5. Start Local Application
```bash
# Terminal 1: Launch FastAPI Backend (Port 8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Launch React Frontend (Port 5173)
cd frontend
npm install
npm run dev
```
Open **`http://127.0.0.1:5173`** in your browser.

### 6. Run Automated Unit & Integration Tests
```bash
python tests/test_agent.py
```

---

## Limitations

1. **Brand-Specific Lexicon**: Calibrated specifically for digital audio streaming (`SpotifyCares`). Retargeting to another brand requires re-running `pipeline.prepare_data` with the new target brand configured in `config/config.yaml`.
2. **Offline Text Proxy**: Cannot evaluate post-resolution customer satisfaction or resolve private backend billing issues that require access to proprietary user databases.
3. **Single-Turn Scope**: The current agent handles initial customer message triage and response drafting; it does not maintain multi-day asynchronous conversation state.

---

## License
MIT License. Developed as an autonomous customer support copilot.
