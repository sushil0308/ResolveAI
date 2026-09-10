# Golden Set Manual Verification Guide

## Purpose
This guide establishes the standardized protocol for manual human verification of the 200-example Golden Evaluation Dataset (`evaluation/golden_set.csv`). 

To ensure absolute scientific integrity, all initial programmatically filtered examples are treated as **draft labels** until explicitly reviewed and confirmed by a human annotator. No example may be marked `human_verified = True` without manual inspection.

---

## 1. Provenance Schema
Every record in `evaluation/golden_set.csv` contains the following fields:

| Field | Type | Description |
| :--- | :--- | :--- |
| `example_id` | String | Unique identifier (`gold_001` to `gold_200`) |
| `intent` | String | Operational intent category (one of 10 supported classes) |
| `difficulty` | String | Stratification tier: `easy`, `short_noisy`, or `ambiguous_edge` |
| `escalation_label` | String | Ground-truth routing: `AUTO_HANDLE` or `ESCALATE` |
| `escalation_reason` | String | Explicit justification for escalation routing |
| `customer_message` | String | Exact customer tweet text (unmodified) |
| `expected_reply_characteristics` | String | Verified brand response guidelines |
| `historical_brand_text` | String | Historical `@SpotifyCares` response text for reference |
| `source_conversation_id` | String | Source conversation identifier from test split |
| `customer_tweet_id` | Integer | Original Kaggle tweet ID for customer |
| `brand_tweet_id` | Integer | Original Kaggle tweet ID for brand |
| `human_verified` | Boolean | `False` (draft) until verified, `True` once manually inspected |
| `verified_by` | String | Name or ID of the human reviewer |
| `verified_at` | ISO-8601 | Timestamp of verification |

---

## 2. Intent Taxonomy & Classification Rules

When verifying the `intent` field, apply the following mutually exclusive operational definitions:

### 1. `playback_streaming_issue`
- **Definition**: Music/podcast will not play, songs randomly pause, tracks stutter/buffer, shuffle algorithm behaves abnormally, or volume/sound fails.
- **Key Indicators**: *"skips"*, *"won't play"*, *"pauses randomly"*, *"shuffle not working"*, *"no sound"*, *"stutters"*.
- **Default Escalation**: `AUTO_HANDLE` (clean reinstall, restart device, toggle offline mode).

### 2. `offline_downloads`
- **Definition**: Downloaded songs greyed out, tracks refusing to download for offline listening, SD card/storage errors, or download limit reached.
- **Key Indicators**: *"downloaded songs greyed out"*, *"offline mode not working"*, *"storage full"*, *"won't download"*.
- **Default Escalation**: `AUTO_HANDLE` (check storage space, toggle offline mode, verify device limit).

### 3. `subscription_billing`
- **Definition**: Inquiries regarding recurring charges, double billing, receipt inquiries, student discount (SheerID), refund requests, pricing changes, or payment method failures.
- **Key Indicators**: *"charged twice"*, *"receipt"*, *"cancel premium"*, *"refund"*, *"SheerID"*, *"credit card failed"*.
- **Default Escalation**: `ESCALATE` (requires human inspection of private billing records in DM).

### 4. `account_security_access`
- **Definition**: Compromised/hacked accounts, unauthorized password resets, unexpected logouts, email changed without consent, or total login lockout.
- **Key Indicators**: *"hacked"*, *"password reset not working"*, *"someone logged into my account"*, *"email changed"*, *"locked out"*.
- **Default Escalation**: `ESCALATE` (critical safety incident requiring confidential identity verification in DM).

### 5. `app_crash_performance`
- **Definition**: Application crashes immediately on launch, freezes on black/blank screen, high battery drain, memory leaks, or unresponsiveness following an update.
- **Key Indicators**: *"app crashes on startup"*, *"freezes on black screen"*, *"update broke the app"*, *"keeps closing"*.
- **Default Escalation**: `AUTO_HANDLE` (OS compatibility check, cache clear, clean reinstall).

### 6. `playlist_library_management`
- **Definition**: Accidentally deleted playlists, missing Liked Songs, local files not syncing over Wi-Fi, or playlist ordering issues.
- **Key Indicators**: *"recovering deleted playlist"*, *"liked songs vanished"*, *"local files won't sync"*, *"queue broken"*.
- **Default Escalation**: `AUTO_HANDLE` (direct user to spotify.com/account/recover-playlists or check local network firewall).

### 7. `family_duo_plan`
- **Definition**: Setup, invitations, and home address verification failures for Premium Family or Duo plans.
- **Key Indicators**: *"family plan invite"*, *"address verification failed"*, *"duo member cannot join"*, *"same address"*.
- **Default Escalation**: `AUTO_HANDLE` / `ESCALATE` (informational address advice is auto-handled; failed invitations requiring plan management escalation).

### 8. `device_connectivity`
- **Definition**: Spotify Connect pairing, Bluetooth speaker disconnection, Chromecast streaming failures, PlayStation/Xbox app pairing, or car audio integration.
- **Key Indicators**: *"won't connect to speaker"*, *"Spotify Connect missing"*, *"Bluetooth cuts out"*, *"Chromecast"*, *"PS4 app"*.
- **Default Escalation**: `AUTO_HANDLE` (restart router/speaker, verify same Wi-Fi network, re-pair Bluetooth).

### 9. `catalog_licensing`
- **Definition**: A specific artist, album, or song is greyed out, unavailable in the customer's region/country, or disappeared from the catalog due to rights agreements.
- **Key Indicators**: *"why is this album greyed out"*, *"song removed"*, *"not available in my country"*, *"artist catalog"*.
- **Default Escalation**: `AUTO_HANDLE` (explain licensing agreements fluctuate by region; link to community rights updates).

### 10. `feedback_feature_request`
- **Definition**: General feedback, UI complaints, requests for new features, or compliments/complaints not describing a technical defect.
- **Key Indicators**: *"bring back old UI"*, *"feature idea"*, *"love the app"*, *"suggestion for developers"*.
- **Default Escalation**: `AUTO_HANDLE` (thank user and route to Spotify Community Idea Exchange).

---

## 3. Escalation Decision Rules

When verifying `escalation_label`, adhere strictly to the enterprise safety protocol:

### Route to `ESCALATE` IF ANY of the following apply:
1. **Financial Transaction / Billing Dispute**: Customer was charged twice, requests a refund, questions a price hike, or has card payment errors.
2. **Account Security / Privacy Breach**: Mentions of hacked accounts, unauthorized email/password modifications, or sensitive user data.
3. **Severe Brand Risk / Frustration**: Highly distressed language indicating imminent churn or legal/regulatory escalation.
4. **Requires Private Internal Database Access**: Any issue where resolution requires looking up the user's account backend or transaction logs (which cannot be done publicly on Twitter).

### Route to `AUTO_HANDLE` ONLY IF:
1. The issue has a verified, public, self-service resolution (e.g., clean reinstall, clearing local cache, toggling offline mode, checking router Wi-Fi, navigating to account recovery page).
2. The customer inquiry contains sufficient context to diagnose the issue without asking for confidential personal data.

---

## 4. Verification Workflow
1. Open `evaluation/golden_set.csv` or navigate to the verification view in the application.
2. Read the customer message carefully.
3. Compare against `historical_brand_text` to verify what actual `@SpotifyCares` agents did.
4. If the draft `intent` is inaccurate, correct it to the true operational category.
5. If the draft `escalation_label` is incorrect, adjust between `AUTO_HANDLE` and `ESCALATE`, updating `escalation_reason`.
6. Set `human_verified` to `True`, set `verified_by` to your reviewer identifier, and set `verified_at` to the current ISO-8601 timestamp.
