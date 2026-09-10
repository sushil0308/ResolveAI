# Brand Selection Report: Customer Support on Twitter

## Executive Summary
This report details the data-driven selection of **`@SpotifyCares`** as the target brand for the ResolveAI Customer Support Copilot, chosen from the 108 brands in the Kaggle *Customer Support on Twitter* (`thoughtvector/customer-support-on-twitter`) dataset.

The selection was conducted empirically by profiling candidate brands across total outbound volume, customer-agent pair match rate, response length, language consistency, canned DM-deflection rates, and semantic diversity of support resolutions.

---

## 1. Candidate Brands Considered

From the 2,811,774 total tweets (1,537,843 inbound customer messages, 1,273,931 outbound brand responses), the top candidate brands by outbound volume were evaluated:

| Brand Handle | Outbound Tweets | Matched Customer-Agent Pairs | Avg Response Len (chars) | DM Redirection Rate | Language Diversity | Primary Domains |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **@AmazonHelp** | 169,840 | ~168,000 | 124.0 | 0.6% | Highly Multilingual (JA, DE, ES, HI, EN) | E-commerce orders, delivery tracking, refunds, prime video |
| **@AppleSupport** | 106,860 | 106,646 | 136.6 | 52.5% | Predominantly English | iOS, macOS, battery, iCloud, Apple ID, hardware repair |
| **@SpotifyCares** | **43,265** | **43,092** | **129.6** | **30.8%** | **Predominantly English (>94%)** | **Streaming playback, offline downloads, subscription/billing, account security, app crashes, device pairing** |
| **@Uber_Support** | 56,270 | ~55,000 | 110.1 | 35.2% | Mixed English/Spanish/Portuguese | Trip fares, driver disputes, app location, lost items |
| **@Delta** | 42,253 | ~41,000 | 103.9 | 16.4% | English | Flight delays, baggage, rebooking, seat upgrades |

---

## 2. Quantitative & Qualitative Comparison

### Why NOT @AmazonHelp?
- **Multilingual Fragmentation**: Amazon operates global accounts from a single `@AmazonHelp` handle. Inspection revealed substantial portions in Japanese (`amazon.co.jp`), German, Hindi, and Spanish. Training a single coherent intent taxonomy and grounded retrieval index would require either multilingual translation or aggressive filtering that fragments data consistency.
- **Generic Deflections**: AmazonHelp heavily utilizes templated external URL redirects (e.g., `amzn.to/...`) rather than conversational issue resolution within Twitter.

### Why NOT @AppleSupport?
- **Excessive DM Deflection (52.5%)**: Over half of all AppleSupport tweets are immediate rote deflections to private messages (`"Select the following link to join us in a DM"`). Because Apple policies restrict public discussion of serial numbers and Apple ID credentials, actual resolution steps are obscured from the dataset.
- **Hardware/Firmware Confounding**: Many issues require physical Apple Store Genius Bar appointments, making automated support agent simulation less representative of end-to-end digital resolution.

### Why @SpotifyCares is Optimal
1. **Rich Grounded Resolutions (69.2% non-DM)**: When Spotify agents respond publicly, they provide detailed, step-by-step diagnostic and resolution instructions:
   - Clean reinstall procedures with specific cache paths.
   - Explicit steps to toggle Offline Mode and verify storage space.
   - Specific checks for Student Discount verification via SheerID.
   - Clarifications on Family Plan address verification rules.
   - Bluetooth / Chromecast / Connect audio routing toggles.
2. **Distinct, High-Signal Intent Boundaries**:
   The problem space divides naturally into clear operational categories (Playback Bugs, Offline Cache, Subscription/Billing, Account Compromise, Device Sync, Outages).
3. **Realistic Operational Escalation Boundary**:
   - **Auto-handleable**: Diagnostic checks, clean reinstall instructions, offline mode toggles, local file indexing guidance, playlist restoration links.
   - **Must-escalate**: Account hacked/credentials compromised, unauthorized credit card charges, recurring payment failures, student discount verification failures.
4. **Data Scale**:
   43,092 matched pairs provide a rich historical retrieval corpus while allowing deterministic, sub-second FAISS/vector indexing and fast local reproducible evaluation.

---

## 3. Limitations of Brand Selection

1. **Brand-Specific Jargon**: Models trained or evaluated on Spotify support utilize terms specific to digital audio streaming (`offline sync`, `local files`, `shuffle`, `premium duo`, `extreme quality`).
2. **Platform Format Constraints**: Twitter's 140/280 character limit encourages concise responses, often split across multi-part tweets or ending with agent initials (e.g. `/CH`, `/CB`).
3. **Private Data Truncation**: When an issue involves account-level billing or password reset, the brand inevitably moves the customer to DM (`"Send us a DM with your account's email address"`). The historical dataset does not record the private DM resolution; the agent must recognize this as an escalation event.

---

## 4. Configurability
The selected brand is not hard-coded. It is governed by configuration in `config/config.yaml` (`brand.target_brand: "SpotifyCares"`), allowing the entire pipeline to be retargeted to another brand (e.g., `AppleSupport` or `AmazonHelp`) by changing a single parameter.
