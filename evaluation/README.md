# Golden Evaluation Dataset Documentation

## Overview
The Golden Evaluation Dataset consists of **200 manually verified customer inquiries** sampled from the unseen **Test split** of the Customer Support on Twitter (`thoughtvector/customer-support-on-twitter`) dataset for `@SpotifyCares`.

All 200 examples are isolated from both the retrieval database and model tuning, guaranteeing zero leakage and uncompromised evaluation integrity.

---

## 1. Class Distribution

The dataset utilizes **balanced stratified sampling** across all 10 operational support intents:

| Intent | Total Count | Escalation Label Distribution | Primary Difficulty Tiers |
| :--- | :--- | :--- | :--- |
| `playback_streaming_issue` | 20 | AUTO: 19, ESC: 1 | Easy: 11, Noisy: 4, Ambig: 5 |
| `offline_downloads` | 20 | AUTO: 20, ESC: 0 | Easy: 14, Noisy: 1, Ambig: 5 |
| `subscription_billing` | 20 | AUTO: 0, ESC: 20 | Easy: 10, Noisy: 5, Ambig: 5 |
| `account_security_access` | 20 | AUTO: 0, ESC: 20 | Easy: 13, Noisy: 2, Ambig: 5 |
| `app_crash_performance` | 20 | AUTO: 20, ESC: 0 | Easy: 13, Noisy: 2, Ambig: 5 |
| `playlist_library_management` | 20 | AUTO: 20, ESC: 0 | Easy: 14, Noisy: 1, Ambig: 5 |
| `family_duo_plan` | 20 | AUTO: 19, ESC: 1 | Easy: 13, Noisy: 2, Ambig: 5 |
| `device_connectivity` | 20 | AUTO: 20, ESC: 0 | Easy: 14, Noisy: 1, Ambig: 5 |
| `catalog_licensing` | 20 | AUTO: 20, ESC: 0 | Easy: 15, Noisy: 0, Ambig: 5 |
| `feedback_feature_request` | 20 | AUTO: 20, ESC: 0 | Easy: 10, Noisy: 5, Ambig: 5 |

---

## 2. Difficulty Breakdown
- **Easy / Prototypical (127 examples)**: Clear, self-contained inquiries with direct keywords and grammatical structure.
- **Short / Noisy Twitter (23 examples)**: Highly abbreviated syntax, typos, informal slang (e.g. *'y tf is shuffle not shufflin'*), and missing context.
- **Ambiguous / Edge Cases (50 examples)**: Compound inquiries spanning multiple operational domains (e.g., offline downloads crashing during app launch, or payment disputes combined with family invite failures).

---

## 3. Escalation Ground Truth Policy
- **Total `AUTO_HANDLE`**: 158 (79.0%)
- **Total `ESCALATE`**: 42 (21.0%)

### Criteria for Escalation:
1. **Confidential Credentials / Account Security**: Suspected hacking, stolen accounts, or password resets failing require private identity verification.
2. **Financial Transactions**: Duplicate charges, unexpected billing renewals, and refund requests require human lookup in backend payment systems.
3. **Severe Brand Discontent**: Legal threats or extreme frustration requiring human empathy and discretion.

---

## 4. Fields Schema
- `example_id`: Unique identifier (`gold_001` through `gold_200`).
- `intent`: Ground truth intent label.
- `difficulty`: Difficulty tier (`easy`, `short_noisy`, `ambiguous_edge`).
- `escalation_label`: Target operational decision (`AUTO_HANDLE` vs `ESCALATE`).
- `escalation_reason`: Human-readable operational justification.
- `customer_message`: Exact normalized text of the customer inquiry.
- `expected_reply_characteristics`: Objective criteria for grounded response content.
- `historical_brand_text`: The real historical response drafted by Spotify support agents.
- `source_conversation_id`: Traceable conversation ID linking back to the raw dataset.
