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
            While our main intent classifier achieves <strong>61.0% Accuracy (59.9% Macro F1)</strong> and our escalation safety gate achieves a <strong>4.76% False Auto-Handling Rate</strong>, an experienced engineer must scrutinize what headline benchmarks do and do not represent:
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
            <li>
              <strong>7. Human Agreement Reflects a Single Human Reviewer</strong>:
              Our 40-case manual annotation set was evaluated by a single human reviewer ($N = 1$). While single-blind and rigorous, it reflects the subjective standard of one annotator rather than a multi-annotator crowd consensus or inter-annotator Fleiss' kappa.
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
