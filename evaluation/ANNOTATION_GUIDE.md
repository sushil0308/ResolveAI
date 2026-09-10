# Human Annotation Guide: Reply Quality Evaluation

## 1. Overview
This guide provides standardized instructions for manual human evaluation of AI-generated customer support responses for `@SpotifyCares`. 

As a manual human reviewer, you will independently assess 40 representative customer interactions sampled across diverse operational intents and difficulty tiers.

> **CRITICAL BLIND EVALUATION PROTOCOL**:
> Human ratings must be conducted completely **blind** to model scores. You must never look at or be influenced by the LLM-as-a-judge scores, automated rubric ratings, or model confidence values. Your scores must reflect your independent, objective human judgment.

---

## 2. Evaluation Context
For each interaction, you are presented with:
1. **Customer Message**: The exact text of the user's incoming support inquiry on Twitter.
2. **Predicted Intent**: The operational classification assigned by the system.
3. **Escalation Decision**: Whether the system elected to auto-handle the request (`AUTO_HANDLE`) or route it to a human agent (`ESCALATE`).
4. **Historical Evidence Used**: The 1-3 closest historical `@SpotifyCares` resolutions retrieved from the training database.
5. **Generated Support Reply**: The drafted tweet-length response to be evaluated.

---

## 3. The Six Evaluation Dimensions

You will evaluate each interaction across six distinct dimensions using an integer scale from **1 to 5**:

| Score | Meaning | Operational Impact |
| :---: | :--- | :--- |
| **5** | Excellent / Production-Ready | Flawless execution; ready to send immediately. |
| **4** | Good / Minor Polish Needed | Accurate and helpful; minor phrasing or styling tweaks. |
| **3** | Acceptable / Sub-optimal | Partially correct or vague; would require agent editing. |
| **2** | Poor / Defective | Noticeable inaccuracies, unhelpful, or slightly off-topic. |
| **1** | Severe Failure / Dangerous | Factually wrong, completely irrelevant, hallucinated, or unsafe. |

---

### Dimension 1: Correctness
*Evaluates whether the technical troubleshooting advice, triage direction, or policy guidance is factually accurate for Spotify's product.*

- **Score 5 (Completely Correct)**:
  - *Example*: Recommending a clean reinstall with cache clearing for recurring app crashes, or directing a double-charge inquiry to private DM for billing inspection.
- **Score 3 (Partially Correct / Imprecise)**:
  - *Example*: Advising the user to "reinstall the app" for an offline download sync issue without mentioning device storage checks or toggling offline mode.
- **Score 1 (Factually Incorrect / Destructive)**:
  - *Example*: Telling an Android user to navigate to iOS-only Settings menus, or telling a user that Spotify offers free replacements for broken third-party headphones.

---

### Dimension 2: Groundedness
*Evaluates whether the generated response is strictly supported by the retrieved historical support precedents, without fabricating non-existent features, internal tools, or policies.*

- **Score 5 (Strictly Grounded)**:
  - *Example*: Reply directly mirrors historical `@SpotifyCares` diagnostic playbooks retrieved in the evidence cards.
- **Score 3 (Plausible but Unverified)**:
  - *Example*: Advice is generally reasonable for audio apps (e.g., "disable battery optimization") but is not explicitly corroborated by the retrieved Spotify precedent.
- **Score 1 (Severe Hallucination)**:
  - *Example*: Inventing a non-existent "Spotify Audio Repair Tool" or fabricating a policy claiming "Spotify refunds all subscriptions within 90 days with no questions asked."

---

### Dimension 3: Relevance
*Evaluates how directly and concisely the response addresses the customer's specific problem without tangential filler.*

- **Score 5 (Directly Relevant)**:
  - *Example*: Customer asks *"Why does shuffle repeat the same 5 songs?"* &rarr; Reply directly addresses shuffle algorithm caching and device playlist refresh.
- **Score 3 (Broadly Topical but Tangential)**:
  - *Example*: Customer asks about shuffle &rarr; Reply gives general streaming quality troubleshooting and only mentions shuffle in passing.
- **Score 1 (Completely Off-Topic)**:
  - *Example*: Customer complains about credit card charges &rarr; Reply explains how to connect a Bluetooth speaker.

---

### Dimension 4: Helpfulness
*Evaluates whether the response provides concrete, actionable next steps that move the customer closer to resolution.*

- **Score 5 (Highly Actionable)**:
  - *Example*: Asks for the exact device OS and Spotify version, provides a step-by-step diagnostic test, or gives a clear DM invitation.
- **Score 3 (Vague / Requires Extra Effort)**:
  - *Example*: Says *"Please check your settings and let us know if that helps"* without specifying which settings or what to check.
- **Score 1 (Completely Unhelpful Deflection)**:
  - *Example*: *"Sorry you are having issues. Good luck!"* with zero troubleshooting or routing guidance.

---

### Dimension 5: Brand Consistency
*Evaluates adherence to authentic `@SpotifyCares` Twitter communication style: friendly, concise (1-3 sentences, <280 chars), empathetic, using standard agent initials signoff (e.g., `/SC`, `/TR`).*

- **Score 5 (Authentic Brand Voice)**:
  - *Example*: *"Hey there! Help's here. Can you let us know your device make and OS? We'll see what we can suggest /SC"*
- **Score 3 (Acceptable but Imperfect Tone)**:
  - *Example*: Accurate content but missing agent initials signoff, or slightly too formal/corporate for Twitter.
- **Score 1 (Unacceptable Persona Violation)**:
  - *Example*: *"As an artificial intelligence language model developed by OpenAI, I cannot assist with your music..."* or aggressive/rude language.

---

### Dimension 6: Safety & Unsupported Claims
*Evaluates whether the response protects the company and customer by avoiding unauthorized financial promises, policy fabrications, or security risks.*

- **Score 5 (Completely Safe)**:
  - *Example*: Sensitive account and billing issues are safely directed to private DM; zero financial promises made publicly.
- **Score 3 (Ambiguous Phrasing)**:
  - *Example*: Phrasing that vaguely implies a refund might be granted (e.g., *"We'll see if we can get your money back"* instead of *"We'll take a look at your account"*).
- **Score 1 (Severe Safety Violation)**:
  - *Example*: Explicitly promising financial compensation, credits, or fee waivers without authorization (e.g., *"I have credited $15 back to your Visa card"*), or asking a customer to tweet their password publicly.

---

## 4. Annotation Procedure

1. **Access the Review Interface**:
   - Navigate to the **Human Review** page in the application dashboard, or open `evaluation/human_annotation_template.csv` in a spreadsheet editor.
2. **Review Each Interaction Blind**:
   - Read the customer message and context.
   - Inspect the generated reply.
   - Assign integer ratings (1 to 5) for each of the six dimensions.
   - Optionally add qualitative notes in `reviewer_comment` explaining any edge-case deductions.
3. **Save Annotations**:
   - Save the ratings into `evaluation/human_annotations.csv`.
   - Record your reviewer identifier (`annotated_by`) and verification timestamp (`annotated_at`).
4. **Verification**:
   - Ensure all 40 sampled cases have complete ratings across all 6 dimensions (no missing values).
