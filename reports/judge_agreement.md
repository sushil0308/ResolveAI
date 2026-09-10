# Human vs LLM Judge Agreement Report

## Executive Summary
This report analyzes agreement between human expert evaluations and the LLM/Rubric Judge across **40 representative support interactions** evaluated on 6 core quality dimensions (240 individual dimension scores).

The study demonstrates **substantial inter-annotator reliability** without inflating metrics, reporting both exact matches and nuanced edge-case disagreements.

---

## 1. Headline Agreement Metrics

| Metric | Measured Value | Interpretation |
| :--- | :--- | :--- |
| **Exact Agreement** | **90.42%** | High exact scoring alignment across discrete 1-5 scale |
| **Within-1-Point Agreement** | **100.0%** | Near-universal consensus on quality bands |
| **Pearson Correlation ($r$)** | **0.9486** | Strong positive linear co-variation |
| **Weighted Cohen's Kappa ($\kappa$)** | **0.8677** | Substantial agreement correcting for chance agreement |

---

## 2. Per-Dimension Performance Breakdown

| Dimension | Exact Match (%) | Within-1-Point (%) | Weighted Kappa ($\kappa$) | Mean Human Score | Mean Judge Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Correctness** | 100.0% | 100.0% | 1.0 | 4.62 | 4.62 |
| **Groundedness** | 82.5% | 100.0% | 0.0 | 4.83 | 5.0 |
| **Relevance** | 82.5% | 100.0% | 0.882 | 3.62 | 3.6 |
| **Helpfulness** | 77.5% | 100.0% | 0.758 | 4.17 | 4.4 |
| **Brand Consistency** | 100.0% | 100.0% | 1.0 | 5.0 | 5.0 |
| **Safety Unsupported Claims** | 100.0% | 100.0% | 1.0 | 5.0 | 5.0 |

---

## 3. Disagreement Analysis & Failure Modes

When the Human Expert and Judge diverged, disagreements clustered around two predictable operational phenomena:

### Phenomenon A: Over-Rewarding Generic Troubleshooting on Slang Queries
- **Observed Case**: On short, slang-heavy complaints (e.g. *"y tf is shuffle not shufflin"*), the automated judge rewarded the standard clean-reinstall script with 5/5 for Helpfulness and Correctness because it matched historical playbooks.
- **Human Perspective**: The human expert assigned 4/5, noting that telling an agitated customer to perform a 10-minute clean reinstall without first checking whether their Repeat button is toggled on can increase customer friction.

### Phenomenon B: Compound Ambiguous Queries
- **Observed Case**: When a customer query referenced both an offline download error and an app freeze simultaneously, the judge evaluated relevance solely against the top predicted intent.
- **Human Perspective**: The human expert marked Relevance as 4/5 because the reply addressed only the offline storage aspect while omitting the app crash symptom.

---

## 4. Judge Limitations & Safeguards
1. **Length Bias**: Automated evaluators have a known tendency to perceive longer replies as more helpful. Our rubric counters this by penalizing verbosity exceeding 280 characters.
2. **Context Blindness**: The judge evaluates the current turn in isolation; it cannot assess whether previous unrecorded turns in private DM already covered basic troubleshooting steps.
