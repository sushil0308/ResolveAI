# Deep Failure Analysis: Top 5 Real Failure Modes

## Overview
This document conducts an unvarnished root-cause investigation into the top failure modes discovered during end-to-end evaluation of the ResolveAI Support Copilot on the 200 Golden Evaluation Set interactions. None of these failure modes are hypothetical; all are drawn directly from empirical errors logged in `evaluation/results.json`.

---

### Failure Mode 1: Entity Polysemy & Dominant Noun Hijacking ("Playlist" vs "Playback")
- **Frequency**: 28 instances (35.9% of all intent misclassifications).
- **Real Example** (`gold_003`):
  > *"@user @user It just skips through my playlist without playing a single song"*
- **Expected Intent**: `playback_streaming_issue` (Action: `AUTO_HANDLE` with audio/cache troubleshooting).
- **Actual Output**: `playlist_library_management` (Confidence: 0.62).
  - *Draft Reply*: Suggested recovering deleted playlists on spotify.com.
- **Why the System Failed**:
  The word *"playlist"* appears in 1,656 training examples for library management. Even though the customer's active verb is *"skips through without playing"*, the strong unigram weight of *"playlist"* overpowered the streaming playback signal.
- **Hypothesis for Improvement**:
  Implement dependency-parsing or verb-noun relation extraction (e.g. `skips -> playlist` should bind to playback actions rather than noun-level bag-of-words presence).

---

### Failure Mode 2: Multi-Intent Compound Complaints
- **Frequency**: 19 instances (24.4% of intent misclassifications).
- **Real Example** (`gold_018`):
  > *"My downloaded songs are greyed out and every time I click them the app crashes immediately to my home screen."*
- **Expected Intent**: `offline_downloads` OR `app_crash_performance` (compound failure).
- **Actual Output**: Predicted `offline_downloads` (Confidence: 0.58).
  - *Draft Reply*: Addressed only storage settings and download toggles; completely ignored the crash on launch.
- **Why the System Failed**:
  The system assumes a single-label classification architecture. When customer inquiries present a causal chain (an offline sync error triggering a fatal memory crash), forced single-label prediction leaves half the customer's problem unaddressed.
- **Hypothesis for Improvement**:
  Upgrade to multi-label intent detection where primary and secondary intents can both condition a composite reply template (e.g., advising clean reinstall for the crash, followed by re-downloading playlists).

---

### Failure Mode 3: Extreme Slang & Missing Context in Short Tweets
- **Frequency**: 14 instances (17.9% of intent misclassifications).
- **Real Example** (`gold_042`):
  > *"y tf is shuffle not shufflin"*
- **Expected Intent**: `playback_streaming_issue` (Shuffle glitch).
- **Actual Output**: `feedback_feature_request` (Confidence: 0.44, Flagged Uncertain).
- **Why the System Failed**:
  The customer message contains zero formal vocabulary, utilizing colloquial abbreviations (*"y tf"*) and informal inflection (*"shufflin"*). The lemmatizer and sublinear n-gram models failed to match canonical tokens like `shuffle playback`.
- **Hypothesis for Improvement**:
  Incorporate character-level subword embeddings or a fine-tuned tweet-normalizing byte-pair encoding (BPE) model to map colloquial Twitter slang into standard support semantics.

---

### Failure Mode 4: Over-Conservative Escalation (High False Escalation Rate)
- **Frequency**: 115 instances (72.8% of ground-truth Auto-Handle cases).
- **Real Example** (`gold_029`):
  > *"How do I change the audio streaming quality on mobile data in the settings menu?"*
- **Expected Escalation**: `AUTO_HANDLE` (Standard configuration question).
- **Actual Output**: `ESCALATE` (Reason: Low intent classification confidence / retrieval similarity cutoff).
- **Why the System Failed**:
  To guarantee that the **False Auto-Handling Rate** remained strictly below 5% (actual: 4.76%), the escalation safety gates enforce conservative thresholds: whenever intent confidence falls below 0.45 or top retrieval similarity is modest, the query is routed to human support.
- **Hypothesis for Improvement**:
  Calibrate confidence thresholds adaptively per intent: allow lower retrieval thresholds for purely informational "how-to" settings queries while maintaining strict gates for billing and security.

---

### Failure Mode 5: Third-Party Ecosystem & Platform Ambiguity
- **Frequency**: 9 instances (11.5% of intent misclassifications).
- **Real Example** (`gold_005`):
  > *"@SpotifyCares i want upgrade to premium but cant with Google Play Card balances?"*
- **Expected Intent**: `subscription_billing` (Action: `ESCALATE`).
- **Actual Output**: Misrouted initially due to *"Google Play"* triggering playback/play tokens before disambiguation.
- **Why the System Failed**:
  Third-party store billing (Google Play Store, Apple App Store, Roku, Sony PlayStation Store) uses different billing infrastructure than Spotify Direct. The presence of the word *"Play"* acts as a false friend for music playback.
- **Hypothesis for Improvement**:
  Add an explicit third-party payment entity gazetteer (`Google Play balance`, `iTunes gift card`, `PlayStation network wallet`) that maps directly into third-party subscription triage.
