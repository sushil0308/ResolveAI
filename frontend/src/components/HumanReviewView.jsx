import React, { useState, useEffect } from 'react';

export default function HumanReviewView({ apiBaseUrl = "http://localhost:8000" }) {
  const [cases, setCases] = useState([]);
  const [annotations, setAnnotations] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [saveMessage, setSaveMessage] = useState(null);

  // Form state for current interaction (starts unselected - explicit human input required)
  const [scores, setScores] = useState({
    correctness: 0,
    groundedness: 0,
    relevance: 0,
    helpfulness: 0,
    brand_consistency: 0,
    safety: 0,
  });
  const [comment, setComment] = useState("");
  const [reviewerName, setReviewerName] = useState("manual_human_reviewer");

  const dimensions = [
    { key: "correctness", label: "Correctness", desc: "Factual troubleshooting accuracy for Spotify products" },
    { key: "groundedness", label: "Groundedness", desc: "Supported by historical evidence; zero invented policies" },
    { key: "relevance", label: "Relevance", desc: "Directly addresses the customer's specific problem" },
    { key: "helpfulness", label: "Helpfulness", desc: "Clear, actionable next steps or diagnostics provided" },
    { key: "brand_consistency", label: "Brand Consistency", desc: "Authentic Twitter style (<280 chars), friendly, /SC signoff" },
    { key: "safety", label: "Safety", desc: "No unauthorized refund promises, credits, or password leaks" },
  ];

  // Fetch review cases and existing annotations
  useEffect(() => {
    Promise.all([
      fetch(`${apiBaseUrl}/api/review/cases`).then(r => {
        if (!r.ok) throw new Error("Failed to load review sample cases");
        return r.json();
      }),
      fetch(`${apiBaseUrl}/api/review/annotations`).then(r => {
        if (!r.ok) throw new Error("Failed to load existing annotations");
        return r.json();
      }),
    ])
      .then(([casesData, annData]) => {
        setCases(casesData);
        const existing = annData.annotations || {};
        setAnnotations(existing);

        // Populate current case if already reviewed
        if (casesData.length > 0) {
          const firstId = casesData[0].example_id;
          if (existing[firstId]) {
            setScores(existing[firstId].scores);
            setComment(existing[firstId].reviewer_comment || "");
            if (existing[firstId].annotated_by) {
              setReviewerName(existing[firstId].annotated_by);
            }
          }
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, [apiBaseUrl]);

  // Handle navigating between cases
  const loadCase = (index) => {
    if (index < 0 || index >= cases.length) return;
    setCurrentIndex(index);
    setSaveMessage(null);
    const targetCase = cases[index];
    const existing = annotations[targetCase.example_id];

    if (existing) {
      setScores(existing.scores);
      setComment(existing.reviewer_comment || "");
      if (existing.annotated_by) setReviewerName(existing.annotated_by);
    } else {
      // Clear rating inputs - explicit human input required
      setScores({
        correctness: 0,
        groundedness: 0,
        relevance: 0,
        helpfulness: 0,
        brand_consistency: 0,
        safety: 0,
      });
      setComment("");
    }
  };

  const handleScoreChange = (dimKey, val) => {
    setScores(prev => ({ ...prev, [dimKey]: val }));
  };

  const isCurrentComplete = () => {
    return Object.values(scores).every(s => s >= 1 && s <= 5);
  };

  const handleSave = async (advance = true) => {
    if (!isCurrentComplete()) {
      alert("Please select a 1–5 rating for all six dimensions before saving.");
      return;
    }

    const currentCase = cases[currentIndex];
    setSaving(true);
    setSaveMessage(null);

    const payload = {
      example_id: currentCase.example_id,
      correctness: scores.correctness,
      groundedness: scores.groundedness,
      relevance: scores.relevance,
      helpfulness: scores.helpfulness,
      brand_consistency: scores.brand_consistency,
      safety: scores.safety,
      reviewer_comment: comment,
      annotated_by: reviewerName || "manual_human_reviewer",
    };

    try {
      const res = await fetch(`${apiBaseUrl}/api/review/annotations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      // Update local state
      setAnnotations(prev => ({
        ...prev,
        [currentCase.example_id]: {
          example_id: currentCase.example_id,
          scores: { ...scores },
          reviewer_comment: comment,
          annotated_by: reviewerName,
          human_verified: true,
        },
      }));

      setSaveMessage("Saved successfully to evaluation/human_annotations.csv");
      setSaving(false);

      if (advance && currentIndex < cases.length - 1) {
        setTimeout(() => {
          loadCase(currentIndex + 1);
        }, 300);
      }
    } catch (err) {
      console.error(err);
      alert(`Error saving annotation: ${err.message}`);
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <span className="spinner" style={{ borderColor: 'rgba(0,0,0,0.1)', borderTopColor: 'var(--brand-green)', width: '24px', height: '24px' }}></span>
        <p style={{ marginTop: '12px', color: 'var(--text-secondary)' }}>Loading blind human review sample...</p>
      </div>
    );
  }

  if (error || cases.length === 0) {
    return (
      <div className="card" style={{ borderColor: '#fecaca', backgroundColor: '#fef2f2', color: '#991b1b' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Review Cases Unavailable</h3>
        <p style={{ marginTop: '6px', fontSize: '13px' }}>{error || "No review sample cases found."}</p>
      </div>
    );
  }

  const current = cases[currentIndex];
  const completedCount = Object.keys(annotations).length;
  const isAllComplete = completedCount >= cases.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #1e1b4b, #312e81)', color: '#ffffff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#a5b4fc', fontWeight: 700 }}>
              Independent Manual Evaluation Protocol
            </span>
            <h2 style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>
              Human Review — Reply Quality Assessment
            </h2>
            <p style={{ fontSize: '13px', color: '#c7d2fe', marginTop: '4px' }}>
              Single-blind rating: Model scores and automated rubric judgments are hidden to preserve evaluation integrity.
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '22px', fontWeight: 800, color: isAllComplete ? '#34d399' : '#fbbf24' }}>
              {completedCount} / {cases.length}
            </div>
            <p style={{ fontSize: '11px', color: '#e0e7ff', marginTop: '2px' }}>
              {isAllComplete ? "All 40 Sample Ratings Completed" : "Annotations in Progress"}
            </p>
          </div>
        </div>
      </div>

      {/* Progress Chips Selector */}
      <div className="card" style={{ padding: '14px 18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Review Sample Navigation: Case {currentIndex + 1} of {cases.length} ({current.example_id})
          </span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '12px', color: 'var(--text-muted)' }}>
            <span>Reviewer ID:</span>
            <input
              type="text"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              style={{ padding: '3px 8px', fontSize: '12px', borderRadius: '4px', border: '1px solid var(--border-color)' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {cases.map((c, i) => {
            const done = Boolean(annotations[c.example_id]);
            const isSelected = i === currentIndex;
            return (
              <button
                key={c.example_id}
                onClick={() => loadCase(i)}
                style={{
                  padding: '4px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: '6px',
                  border: isSelected ? '2px solid var(--brand-green)' : '1px solid var(--border-color)',
                  backgroundColor: isSelected ? '#ecfdf5' : done ? '#f1f5f9' : '#ffffff',
                  color: isSelected ? '#065f46' : done ? '#0f172a' : '#94a3b8',
                  cursor: 'pointer',
                }}
              >
                {done ? '✓ ' : ''}{i + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Interaction Details & Rating Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '20px' }}>
        {/* Left Column: Context (Blind to LLM scores) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Customer Tweet */}
          <div className="card">
            <div className="card-header">
              <span className="card-title" style={{ fontSize: '14px' }}>Customer Message (Twitter)</span>
              <span className="badge badge-neutral">{current.difficulty} tier</span>
            </div>
            <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '14px', lineHeight: 1.5, marginTop: '8px' }}>
              "{current.customer_message}"
            </div>
          </div>

          {/* System Triage Details */}
          <div className="card">
            <div className="card-header">
              <span className="card-title" style={{ fontSize: '14px' }}>System Operational Triage</span>
              <span className={`badge ${current.escalation_decision === 'AUTO_HANDLE' ? 'badge-auto' : 'badge-escalate'}`}>
                {current.escalation_decision}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '8px', fontSize: '13px' }}>
              <div>
                <strong style={{ color: 'var(--text-muted)' }}>Predicted Intent:</strong>
                <p style={{ fontFamily: 'var(--font-mono)', marginTop: '2px', color: 'var(--brand-green)', fontWeight: 600 }}>
                  {current.predicted_intent}
                </p>
              </div>
              <div>
                <strong style={{ color: 'var(--text-muted)' }}>Routing Reason:</strong>
                <p style={{ marginTop: '2px', color: 'var(--text-secondary)' }}>
                  {current.escalation_reason || "Evaluated by 5 enterprise safety gates."}
                </p>
              </div>
            </div>
          </div>

          {/* Drafted Support Reply */}
          <div className="card" style={{ borderLeft: '4px solid var(--brand-green)' }}>
            <div className="card-header">
              <span className="card-title" style={{ fontSize: '14px', color: 'var(--brand-green)' }}>
                Drafted Reply to Evaluate
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {current.draft_reply.length} chars
              </span>
            </div>
            <div style={{ padding: '14px', backgroundColor: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0', fontSize: '14px', lineHeight: 1.6, marginTop: '8px' }}>
              "{current.draft_reply}"
            </div>
          </div>

          {/* Retrieved Historical Precedents */}
          <div className="card">
            <div className="card-header">
              <span className="card-title" style={{ fontSize: '14px' }}>
                Historical Evidence Used ({current.retrieved_evidence ? current.retrieved_evidence.length : 0} Precedents)
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
              {current.retrieved_evidence && current.retrieved_evidence.length > 0 ? (
                current.retrieved_evidence.map((ev, idx) => (
                  <div key={idx} style={{ padding: '8px 12px', backgroundColor: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '12.5px', color: '#475569' }}>
                    <span style={{ fontWeight: 600, color: '#0f172a' }}>Precedent {idx + 1}: </span>
                    {ev}
                  </div>
                ))
              ) : (
                <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>No historical precedents retrieved.</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: 6-Dimension Manual Rating Form */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Independent Quality Rubric</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Score each dimension from 1 (poor/defective) to 5 (production-ready).
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {dimensions.map(dim => {
              const currentScore = scores[dim.key] || 0;
              return (
                <div key={dim.key} style={{ padding: '10px 12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '13px', color: '#0f172a' }}>{dim.label}</strong>
                      <p style={{ fontSize: '11px', color: '#64748b', marginTop: '1px' }}>{dim.desc}</p>
                    </div>
                    <span style={{ fontSize: '14px', fontWeight: 800, color: currentScore > 0 ? 'var(--brand-green)' : '#94a3b8' }}>
                      {currentScore > 0 ? `${currentScore} / 5` : '—'}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                    {[1, 2, 3, 4, 5].map(val => (
                      <button
                        key={val}
                        type="button"
                        onClick={() => handleScoreChange(dim.key, val)}
                        style={{
                          flex: 1,
                          padding: '6px 0',
                          borderRadius: '6px',
                          border: currentScore === val ? '2px solid var(--brand-green)' : '1px solid #cbd5e1',
                          backgroundColor: currentScore === val ? 'var(--brand-green)' : '#ffffff',
                          color: currentScore === val ? '#ffffff' : '#334155',
                          fontWeight: 700,
                          fontSize: '12.5px',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {val}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Reviewer Comment */}
          <div>
            <label style={{ fontSize: '12px', fontWeight: 600, color: '#334155' }}>
              Reviewer Notes / Qualitative Comments (Optional):
            </label>
            <textarea
              rows={2}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="e.g. Accurate DM referral, but phrasing slightly stiff for Twitter"
              style={{
                width: '100%',
                padding: '8px',
                fontSize: '12px',
                borderRadius: '6px',
                border: '1px solid var(--border-color)',
                marginTop: '4px',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
              }}
            />
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
            {saveMessage && (
              <div style={{ padding: '8px 12px', backgroundColor: '#f0fdf4', color: '#166534', borderRadius: '6px', fontSize: '12px', border: '1px solid #bbf7d0' }}>
                ✓ {saveMessage}
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1 }}
                disabled={currentIndex === 0}
                onClick={() => loadCase(currentIndex - 1)}
              >
                ← Previous
              </button>

              <button
                type="button"
                className="btn btn-primary"
                style={{ flex: 2 }}
                disabled={saving || !isCurrentComplete()}
                onClick={() => handleSave(true)}
              >
                {saving ? "Saving..." : currentIndex === cases.length - 1 ? "Save Rating" : "Save & Next →"}
              </button>
            </div>

            {isAllComplete && (
              <div style={{ padding: '12px', backgroundColor: '#ecfdf5', borderRadius: '8px', border: '1px solid #a7f3d0', textAlign: 'center', marginTop: '6px' }}>
                <strong style={{ color: '#065f46', fontSize: '13px' }}>
                  All 40 Human Ratings Completed!
                </strong>
                <p style={{ fontSize: '11.5px', color: '#047857', marginTop: '4px' }}>
                  Saved to <code>evaluation/human_annotations.csv</code>. You can now execute:
                  <br />
                  <code style={{ fontWeight: 700 }}>python -m evaluation.human_agreement</code>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
