# Empirical Agreement Report: Manual Human Reviewer vs LLM Judge

**Evaluation Date**: 2026-09-12T02:39:02.218500  
**Evaluated Sample Size**: 2 Interactions (Partial)  
**Target Sample Size**: 40 Interactions  
**Reviewer Type**: manual human reviewer (Independent & Blinded)  
**Judge Type**: LLM judge (Google Gemini - gemini-3.7-flash)  
**Protocol**: Single-blind evaluation (human reviewer had zero access to LLM scores during rating)  

---

## 1. Headline Agreement Metrics

| Agreement Metric | Measured Value | Standard Interpretation |
| :--- | :--- | :--- |
| **Exact Agreement** | **16.67%** | Ratings match identically on the 1–5 integer scale |
| **Within-1-Point Agreement** | **58.33%** | Ratings differ by at most ±1 scale point |
| **Pearson Correlation ($r$)** | **0.3055** | Linear alignment of ranking and relative severity |
| **Overall Weighted Cohen's $\kappa$** | **0.2771** | Quadratic inter-rater agreement adjusted for chance |
| **Macro Average $\kappa$** | **0.1667** | Mean Cohen's $\kappa$ across all 6 dimensions |

---

## 2. Per-Dimension Breakdown

| Dimension | Exact Match | Within ±1 | Pearson $r$ | Quadratic $\kappa$ | Human Mean | Judge Mean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Correctness** | 50.0% | 50.0% | 0.0 | 0.0 | 4.0 | 3.0 |
| **Groundedness** | 0.0% | 50.0% | 1.0 | 0.3333 | 4.5 | 3.0 |
| **Relevance** | 0.0% | 50.0% | 0.0 | 0.0 | 2.0 | 3.0 |
| **Helpfulness** | 0.0% | 50.0% | 1.0 | 0.6667 | 4.0 | 2.5 |
| **Brand Consistency** | 50.0% | 50.0% | 0.0 | 0.0 | 4.0 | 5.0 |
| **Safety** | 0.0% | 100.0% | 0.0 | 0.0 | 4.0 | 5.0 |

---

## 3. Scientific Integrity & Methodology Notes

1. **No Synthetic / Simulated Data**: Unlike automated scripts that generate synthetic 'human' scores by adding noise to judge outputs, this report is generated strictly from real manual annotations recorded in `evaluation/human_annotations.csv`.
2. **Blind Review Guarantee**: The human reviewer annotated customer inquiries without viewing model confidence, automated judge scores, or ground truth labels.
3. **Reproducibility**: The aligned pairs are saved in `evaluation/human_judge_sample.csv` for independent auditing.
