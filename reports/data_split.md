# Data Splitting and Leakage Prevention Report

## Executive Summary
This report establishes the rigorous methodology employed to split the 40,682 cleaned `@SpotifyCares` customer-support conversations into isolated Train, Validation, and Test subsets while guaranteeing zero data leakage into evaluation or retrieval candidate pools.

---

## 1. Dataset Split Architecture

The dataset was sorted strictly chronologically using parsed Twitter customer message timestamps (`customer_datetime`) to replicate real-world deployment conditions (where future queries must be handled using only historical precedents):

| Split | Conversation Count | Percentage | Temporal Range | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Train / Retrieval** | 28,477 | 70.0% | Earliest historical cases | Historical case retrieval index; Training baseline ML classifiers |
| **Validation** | 6,102 | 15.0% | Intermediate cases | Hyperparameter tuning; Classification threshold calibration |
| **Test / Golden Pool** | 6,103 | 15.0% | Latest unseen cases | Final independent evaluation; Golden set sampling pool |
| **Total Cleaned** | **40,682** | **100.0%** | Full observed window | End-to-end dataset |

---

## 2. Leakage Prevention Mechanisms

Data leakage is the most common cause of artificially inflated performance in customer-support AI systems. We enforced the following deterministic protections:

### A. Conversation-Level Disjointness
- A single customer interaction often involves multiple back-and-forth turns.
- Splitting at the individual message level would allow earlier turns from conversation $C_i$ into Train and later turns from $C_i$ into Test, enabling models to memorize user-specific context.
- **Enforcement**: All splits are partitioned strictly at the conversation root level (`conversation_id`). No two splits share any part of the same interaction.

### B. Retrieval Isolation (Strict Zero-Leakage Guarantee)
- The vector retrieval index is built **exclusively from the 28,477 historical records in the Train split**.
- Neither Validation nor Test conversations are ever inserted into the vector index.
- During evaluation on Test or Golden Set examples, the ground-truth conversation is guaranteed to be absent from the retrieval database.

### C. Exact Duplicate Filtering Across Splits
- Customers frequently copy-paste identical tweets, or bots repeatedly retweet identical complaints.
- We pre-filtered 2,357 duplicate customer messages prior to splitting.
- Post-split automated verification:
  - **Validation overlap with Train**: **0** exact matches.
  - **Test overlap with Train**: **0** exact matches.

### D. Temporal Realism (Time-Aware Splitting)
- Instead of random shuffling (which leaks future knowledge into historical retrieval), we applied chronological ordering.
- The retrieval index only possesses historical precedent that existed *prior* to the validation and test evaluation queries.

---

## 3. Remaining Risks and Mitigations

1. **User Idiosyncrasies / Power Users**:
   - *Risk*: A single vocal customer might tweet across multiple weeks, appearing in both Train and Test under different conversations.
   - *Mitigation*: Customer handles are normalized to `@user` during text preprocessing, eliminating handle memorization.
2. **Recurring Systematic Incidents (e.g., Major App Updates)**:
   - *Risk*: An iOS or Android app release in the Test period introduces new UI issues not present in the Train period.
   - *Analysis*: This distribution shift tests real generalization, exposing whether the agent recognizes low-similarity queries and safely triggers escalation.
