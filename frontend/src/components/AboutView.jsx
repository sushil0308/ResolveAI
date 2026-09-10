import React from 'react';

export default function AboutView() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Overview Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">About ResolveAI Support Copilot</h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Autonomous engineering implementation of an enterprise AI customer support copilot
            </p>
          </div>
          <span className="badge badge-auto">PROOF &gt; COMPLEXITY</span>
        </div>

        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6, marginTop: '8px' }}>
          This system is an enterprise-grade AI customer-support copilot built on the Kaggle <em>Customer Support on Twitter</em> dataset (2.81M tweets). It classifies customer messages into 10 practical operational intents, retrieves semantically similar historical precedents from 28,477 resolved conversations, drafts grounded replies following verified brand resolution playbooks without hallucinating unverified claims, and computes an explainable escalation decision to minimize the critical <strong>False Auto-Handling Rate</strong>.
        </p>
      </div>

      {/* Mandatory Section: What is Misleading About My Headline Number? */}
      <div className="card" style={{ borderLeft: '4px solid var(--brand-amber)' }}>
        <div className="card-header">
          <h3 className="card-title" style={{ fontSize: '16px', color: '#92400e' }}>
            What is misleading about my headline number?
          </h3>
          <span className="badge badge-neutral">Critical Intellectual Honesty</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <p>
            While our main intent classifier achieves <strong>61.0% Accuracy (59.9% Macro F1)</strong> and our reply quality judge reports <strong>4.63 / 5</strong>, an experienced engineer must scrutinize what these numbers do and do not represent:
          </p>

          <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <li>
              <strong>1. Balanced Golden Set vs Real-World Class Skew</strong>:
              Our 200-example Golden Evaluation Set uses a uniform 20-samples-per-intent distribution (10% per class). In real Twitter production, over 35% of all incoming inquiries are billing or playback complaints. If evaluated on the raw imbalanced stream, overall micro-accuracy would appear higher (~70%), but at the expense of concealing poor recall on minority intents like <code>device_connectivity</code> and <code>catalog_licensing</code>.
            </li>
            <li>
              <strong>2. Offline Text Rubric vs Real Customer Satisfaction (CSAT)</strong>:
              An offline score measures whether the drafted reply addresses the stated complaint using verified brand diagnostic playbooks. However, offline text cannot evaluate whether the customer’s phone actually started playing music, or whether the user was annoyed by being asked to perform a clean reinstall.
            </li>
            <li>
              <strong>3. High False Escalation Overhead</strong>:
              Our escalation engine achieves a stellar <strong>4.76% False Auto-Handling Rate</strong> (only 2 out of 42 true escalations missed). However, this safety comes at the cost of a <strong>72.8% False Escalation Rate</strong> on ambiguous or noisy queries. In production, this would route many benign but poorly phrased inquiries to human agents, requiring calibrated tiering before full deployment.
            </li>
            <li>
              <strong>4. Historical Twitter Data vs Current Spotify Support Policy</strong>:
              The Twitter dataset captures historical resolutions from past app versions. Corporate policies, UI settings, student discounts, and international catalog rights evolve over time; historical tweets must not be treated as immutable legal policy.
            </li>
            <li>
              <strong>5. Moderate Real-World Intent Accuracy (61.0% Accuracy / 59.9% Macro F1)</strong>:
              While outperforming classical ML baselines (+5.0% F1 lift), a ~60% macro F1 reflects the genuine challenge of conversational Twitter messages. Tweets combining multiple complaints (e.g. offline download sync failure followed by app crash) and extreme informal slang remain difficult for single-label classifiers.
            </li>
            <li>
              <strong>6. LLM Judge Scores as an Evaluator Proxy</strong>:
              LLM-as-a-judge scores provide scalable evaluation signal but have inherent model preferences (e.g. verbosity, formatting). They must never be conflated with absolute ground truth or human consensus.
            </li>
          </ol>
        </div>
      </div>

      {/* Mandatory Section: What I Would Do With One More Week */}
      <div className="card" style={{ borderLeft: '4px solid var(--brand-blue)' }}>
        <div className="card-header">
          <h3 className="card-title" style={{ fontSize: '16px', color: 'var(--brand-blue)' }}>
            What I would do with one more week
          </h3>
          <span className="badge badge-neutral">Engineering Roadmap</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <p>Tied directly to the observed failure modes in our empirical failure analysis:</p>

          <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <li>
              <strong>1. Multi-Label Intent Architecture</strong>:
              Transition from single-label softmax to multi-label sigmoid classification to handle compound complaints (e.g. offline download failures that trigger an app crash).
            </li>
            <li>
              <strong>2. Fine-Tuned Dense Bi-Encoder Embeddings</strong>:
              Fine-tune a lightweight sentence-transformer (<code>all-MiniLM-L6-v2</code>) using MultipleNegativesRankingLoss on our 40,682 customer-agent pairs to boost retrieval Recall@5 from 36.5% to &gt;65%.
            </li>
            <li>
              <strong>3. Adaptive Per-Intent Escalation Calibration</strong>:
              Replace global confidence thresholds with intent-specific cutoffs: allow lower confidence (35%) for harmless informational "how-to" settings queries while maintaining strict 80% gates for billing.
            </li>
            <li>
              <strong>4. Tweet Slang Normalization Preprocessor</strong>:
              Build a character-level byte-pair or edit-distance normalizer to standardize informal Twitter inflections (e.g. <em>"y tf is shuffle not shufflin"</em> &rarr; <em>"why is shuffle not working"</em>).
            </li>
            <li>
              <strong>5. Online Shadow Mode & Human Agent Feedback Loop</strong>:
              Deploy the copilot in "Shadow Mode" inside the support agent inbox: display draft replies to human agents and log single-click accepts, edits, and rejections to generate real DPO (Direct Preference Optimization) training pairs.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
