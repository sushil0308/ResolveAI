import React, { useState } from 'react';

const SAMPLES = [
  {
    label: "Playback Pausing",
    text: "Songs keep pausing after 10 seconds on my iPhone even with full Wi-Fi.",
    intentTag: "Playback"
  },
  {
    label: "Double Charge Dispute",
    text: "I was charged twice for Spotify Premium on my credit card this month, I want a refund right now!",
    intentTag: "Billing"
  },
  {
    label: "Account Hacked",
    text: "Someone hacked into my account and changed the email address, please help me get it back!",
    intentTag: "Security"
  },
  {
    label: "Offline Greyed Out",
    text: "My downloaded playlists are suddenly showing as greyed out and won't play offline.",
    intentTag: "Offline"
  },
  {
    label: "Family Address Error",
    text: "My brother lives at the same house but it says our addresses don't match for the Family plan invite.",
    intentTag: "Family"
  }
];

export default function AgentCopilot({ apiBaseUrl = "https://resolveai-backend-nsws.onrender.com" }) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [expandedEvidence, setExpandedEvidence] = useState({});

  const handleAnalyze = async (textToAnalyze = message) => {
    if (!textToAnalyze.trim()) return;
    setLoading(true);
    setError(null);
    setCopied(false);

    try {
      const resp = await fetch(`${apiBaseUrl}/api/agent/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_message: textToAnalyze })
      });

      if (!resp.ok) {
        throw new Error(`Server returned ${resp.status}: ${resp.statusText}`);
      }

      const data = await resp.json();
      setResult(data);
      // Auto expand first evidence
      setExpandedEvidence({ 0: true });
    } catch (err) {
      console.error("Analysis error:", err);
      setError(`Failed to connect to backend: ${err.message}. Make sure the FastAPI server is running on port 8000.`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result && result.draft_reply) {
      navigator.clipboard.writeText(result.draft_reply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const toggleEvidence = (idx) => {
    setExpandedEvidence(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner / Prompt Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title" style={{ fontSize: '17px' }}>Customer Inquiry Triage & Resolution</h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Type an incoming customer message or select a sample query to inspect classification, evidence, and safety decisions.
            </p>
          </div>
          <span className="badge badge-neutral">Target: @SpotifyCares</span>
        </div>

        {/* Sample Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', alignSelf: 'center' }}>
            Try a real scenario:
          </span>
          {SAMPLES.map((sample, idx) => (
            <button
              key={idx}
              className="btn btn-secondary"
              style={{ fontSize: '12px', padding: '5px 12px' }}
              onClick={() => {
                setMessage(sample.text);
                handleAnalyze(sample.text);
              }}
            >
              <span style={{ color: 'var(--brand-green)', fontWeight: 700 }}>•</span> {sample.label}
            </button>
          ))}
        </div>

        {/* Input Area */}
        <div style={{ position: 'relative' }}>
          <textarea
            id="customer-message-input"
            rows={3}
            placeholder="Enter a customer message (e.g., 'My playlist won't play offline' or 'I was charged twice')..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            style={{
              width: '100%',
              padding: '14px 16px',
              borderRadius: '8px',
              border: '1px solid var(--card-border)',
              fontSize: '14px',
              fontFamily: 'var(--font-sans)',
              resize: 'vertical',
              outline: 'none',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)',
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {message.length} characters
          </span>
          <button
            id="analyze-message-btn"
            className="btn btn-primary"
            disabled={loading || !message.trim()}
            onClick={() => handleAnalyze()}
          >
            {loading ? (
              <>
                <span className="spinner"></span> Analyzing Case...
              </>
            ) : (
              "Analyze Message"
            )}
          </button>
        </div>

        {error && (
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#b91c1c', fontSize: '13px' }}>
            {error}
          </div>
        )}
      </div>

      {/* Structured Result Display */}
      {result && (
        <div className="copilot-layout-grid">
          {/* Column 1: Intent & Escalation Decisions (5 cols on desktop, full width on mobile) */}
          <div className="copilot-col-side">
            {/* Intent Card */}
            <div className="card">
              <div className="card-header">
                <span className="kpi-label">Classified Intent</span>
                <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--brand-blue)' }}>
                  {(result.intent_confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
                {result.intent_name}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '14px' }}>
                {result.intent_explanation}
              </p>

              {result.alternative_intent && (
                <div style={{ paddingTop: '12px', borderTop: '1px solid var(--card-border)', display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Alternative Intent:</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {result.alternative_intent} ({(result.alternative_confidence * 100).toFixed(1)}%)
                  </span>
                </div>
              )}
            </div>

            {/* Recommended Action Card */}
            <div className="card" style={{
              borderLeft: result.escalation_decision === "ESCALATE" ? '4px solid var(--brand-rose)' : '4px solid var(--brand-green)'
            }}>
              <div className="card-header">
                <span className="kpi-label">Operational Routing</span>
                <span className={`badge ${result.escalation_decision === "ESCALATE" ? "badge-escalate" : "badge-auto"}`}>
                  Risk: {result.risk_level}
                </span>
              </div>

              <div style={{ margin: '8px 0 14px' }}>
                <span
                  id="escalation-decision-badge"
                  style={{
                    display: 'inline-block',
                    padding: '6px 14px',
                    borderRadius: '6px',
                    fontSize: '15px',
                    fontWeight: 800,
                    letterSpacing: '0.04em',
                    backgroundColor: result.escalation_decision === "ESCALATE" ? '#fee2e2' : '#d1fae5',
                    color: result.escalation_decision === "ESCALATE" ? '#991b1b' : '#065f46',
                  }}
                >
                  {result.escalation_decision === "ESCALATE" ? "ESCALATE TO HUMAN" : "AUTO-HANDLE"}
                </span>
              </div>

              <div>
                <h4 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Decision Rationale
                </h4>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {result.escalation_reason}
                </p>
              </div>

              {/* Signals summary */}
              <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid var(--card-border)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '12px' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Top Similarity: </span>
                  <strong>{(result.top_retrieval_similarity * 100).toFixed(1)}%</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Corroborating Cases: </span>
                  <strong>{result.evidence_count}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Column 2: Draft Reply & Grounded Evidence (7 cols on desktop, full width on mobile) */}
          <div className="copilot-col-main">
            {/* Draft Reply Card */}
            <div className="card">
              <div className="card-header">
                <div>
                  <span className="kpi-label">Proposed Agent Reply</span>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Type: {result.resolution_type} (Grounding: {(result.grounding_confidence * 100).toFixed(0)}%)
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button
                    id="copy-reply-btn"
                    className="btn btn-secondary"
                    style={{ fontSize: '12px', padding: '6px 12px' }}
                    onClick={handleCopy}
                  >
                    {copied ? "Copied to Clipboard!" : "Copy Reply"}
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: '12px', padding: '6px 12px' }}
                    onClick={() => handleAnalyze()}
                  >
                    Regenerate
                  </button>
                </div>
              </div>

              {/* Message Box */}
              <div style={{
                backgroundColor: '#f8fafc',
                border: '1px solid var(--card-border)',
                borderRadius: '8px',
                padding: '16px',
                fontSize: '14px',
                lineHeight: 1.6,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                fontFamily: 'var(--font-sans)',
              }}>
                {result.draft_reply}
              </div>

              <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)', flexWrap: 'wrap', gap: '4px' }}>
                <span>Brand: Spotify Support Tone</span>
                <span>{result.draft_reply.length} / 280 chars</span>
              </div>
            </div>

            {/* Historical Evidence Panel */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Historical Evidence Precedents</h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Retrieved historical support conversations backing this reply (Zero Leakage Verified)
                  </p>
                </div>
                <span className="badge badge-neutral">{result.retrieved_cases?.length || 0} Cases Retrieved</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {result.retrieved_cases && result.retrieved_cases.length > 0 ? (
                  result.retrieved_cases.map((c, idx) => (
                    <div
                      key={idx}
                      style={{
                        border: '1px solid var(--card-border)',
                        borderRadius: '6px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        onClick={() => toggleEvidence(idx)}
                        style={{
                          padding: '10px 14px',
                          backgroundColor: '#f8fafc',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          cursor: 'pointer',
                          fontSize: '13px',
                          flexWrap: 'wrap',
                          gap: '8px',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                          <span style={{
                            fontSize: '11px',
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: '4px',
                            backgroundColor: '#e2e8f0',
                            color: '#334155'
                          }}>
                            {(c.similarity * 100).toFixed(1)}% Sim
                          </span>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            Case #{c.conversation_id}
                          </span>
                          <span className="badge badge-neutral" style={{ fontSize: '11px', padding: '2px 6px' }}>
                            {c.intent || "general"}
                          </span>
                        </div>
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                          {expandedEvidence[idx] ? "▲ Collapse" : "▼ View"}
                        </span>
                      </div>


                      {expandedEvidence[idx] && (
                        <div style={{ padding: '14px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px', backgroundColor: '#ffffff' }}>
                          <div>
                            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Historical Customer:</span>
                            <p style={{ color: 'var(--text-secondary)', marginTop: '2px' }}>{c.customer_message}</p>
                          </div>
                          <div style={{ borderTop: '1px dashed var(--card-border)', paddingTop: '6px' }}>
                            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--brand-green)', textTransform: 'uppercase' }}>Spotify Agent Resolution:</span>
                            <p style={{ color: 'var(--text-primary)', marginTop: '2px', fontStyle: 'italic' }}>"{c.brand_response}"</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No historical cases met the similarity threshold.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
