# Intent Taxonomy Report: Spotify Customer Support

## Executive Summary
This document defines the 10-intent operational taxonomy discovered from empirical analysis of 40,682 customer-support interactions with `@SpotifyCares`. The taxonomy balances operational granularity with mutual exclusivity, ensuring customer queries map to unambiguous resolution workflows while establishing clear boundaries for automated self-service versus human escalation.

---

## 1. Intent Discovery Methodology

Rather than applying an arbitrary generic schema (such as Banking77, which is tailored to financial banking operations), the taxonomy was extracted directly from the empirical training corpus (`data/processed/splits/train.csv`):
1. **Salient N-gram Extraction**: Top TF-IDF unigrams, bigrams, and trigrams were ranked across 28,477 training examples.
2. **Co-occurrence Analysis**: Terms like `offline` & `download`, `shuffle` & `skip`, `student` & `discount`, `hacked` & `password`, `carplay` & `bluetooth` formed tight semantic clusters.
3. **Historical Resolution Pattern Mapping**: Each intent corresponds to a distinct resolution playbook employed by Spotify agents:
   - Cache clearing & clean reinstall (`playback_streaming_issue`, `app_crash_performance`)
   - Storage / SD card management (`offline_downloads`)
   - SheerID & billing investigation via private DM (`subscription_billing`)
   - Immediate security triage & account recovery (`account_security_access`)
   - Local network / firewall troubleshooting (`playlist_library_management`)
   - Exact postal code verification (`family_duo_plan`)
   - Bluetooth pairing & audio routing (`device_connectivity`)
   - Rightsholder licensing explanation (`catalog_licensing`)
   - Community idea submission link (`feedback_feature_request`)

---

## 2. Taxonomy Specifications

| Intent ID | Display Name | Expected Action | Key Triggers | Example Customer Message |
| :--- | :--- | :--- | :--- | :--- |
| `playback_streaming_issue` | Playback & Streaming Audio Glitches | AUTO_HANDLE | buffering, pauses, skipping, shuffle bug, sound quality | *"Songs keep pausing after 10 seconds on my iPhone even with full Wi-Fi."* |
| `offline_downloads` | Offline Mode & Download Issues | AUTO_HANDLE | download stuck, offline mode, greyed out downloads, SD card | *"My downloaded playlists are suddenly showing as greyed out and won't play offline."* |
| `subscription_billing` | Subscription & Billing Inquiries | **ESCALATE** | double charge, card declined, student discount, refund, cancel | *"I was charged twice for Premium this month on my credit card statement."* |
| `account_security_access` | Account Security & Access | **ESCALATE** | hacked, locked out, password reset failing, unauthorized email change | *"Someone hacked into my account and changed the email address, please help!"* |
| `app_crash_performance` | App Crash & Technical Bugs | AUTO_HANDLE | crash on launch, black screen, frozen app, unresponsive | *"Every time I open the app on iOS 11 it instantly crashes to the home screen."* |
| `playlist_library_management`| Playlist, Library & Local Files | AUTO_HANDLE | deleted playlist, local files won't sync, liked songs count | *"My local files from my PC are not showing up on my iPhone app."* |
| `family_duo_plan` | Family & Duo Plan Administration | AUTO_HANDLE | address verification mismatch, invite link expired, slot change | *"My brother lives at the same house but it says our addresses don't match."* |
| `device_connectivity` | Device Connectivity & Integration | AUTO_HANDLE | Bluetooth, Chromecast, Apple CarPlay, PS4, Sonos Connect | *"Spotify Connect cannot find my Sonos speaker even though we are on the same Wi-Fi."* |
| `catalog_licensing` | Content Catalog & Licensing | AUTO_HANDLE | album removed, greyed out in country, explicit filter | *"Why was Jay-Z's discography removed from Spotify?"* |
| `feedback_feature_request` | Feedback & Feature Suggestions | AUTO_HANDLE | UI complaints, lyrics request, new feature idea, feedback | *"Please bring back the old swipe-to-queue gesture in the next update!"* |

---

## 3. Mutual Exclusivity and Boundary Rules

To avoid classification ambiguity:
- **Offline Downloads vs Streaming Playback**: If the customer specifically mentions downloading, offline mode, or airplane mode, it is `offline_downloads`. If playback is glitching while streaming live over Wi-Fi/LTE, it is `playback_streaming_issue`.
- **Billing Dispute vs Family Plan Address**: Payment failures for Family plans are `subscription_billing`. Issues where members cannot join due to physical street address mismatch are `family_duo_plan`.
- **Security Breach vs Routine Login**: If the customer suspects unauthorized intrusion or their email was altered without consent, it is classified as high-priority `account_security_access`.
- **App Crash vs Audio Glitch**: If the app UI shuts down completely or freezes into an OS crash dialog, it is `app_crash_performance`. If the app stays open and music simply stops or distorts, it is `playback_streaming_issue`.
