import React, { useState, useEffect } from 'react';

const INTENT_OPTIONS = [
  { value: "", label: "All Intents" },
  { value: "playback_streaming_issue", label: "Playback & Streaming" },
  { value: "offline_downloads", label: "Offline & Downloads" },
  { value: "subscription_billing", label: "Subscription & Billing" },
  { value: "account_security_access", label: "Account Security & Access" },
  { value: "app_crash_performance", label: "App Crash & Performance" },
  { value: "playlist_library_management", label: "Playlists & Local Files" },
  { value: "family_duo_plan", label: "Family & Duo Plan" },
  { value: "device_connectivity", label: "Device Connectivity" },
  { value: "catalog_licensing", label: "Catalog & Regional Licensing" },
  { value: "feedback_feature_request", label: "Feedback & Suggestions" },
];

export default function HistoricalExplorer({ apiBaseUrl = "https://resolveai-backend-nsws.onrender.com" }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIntent, setSelectedIntent] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const performSearch = async (q = searchQuery, intent = selectedIntent) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.set("q", q.trim());
      if (intent) params.set("intent", intent);
      params.set("limit", "15");

      const res = await fetch(`${apiBaseUrl}/api/historical/search?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResults(data.results || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
  }, [selectedIntent]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header & Filter Controls */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Historical Support Case Explorer</h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Search across 28,477 indexed historical Twitter customer support conversations for @SpotifyCares
            </p>
          </div>
          <span className="badge badge-neutral">{totalCount.toLocaleString()} Total Matches</span>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
          <input
            type="text"
            placeholder="Search keywords (e.g. 'offline greyed out', 'charged twice', 'bluetooth car')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: '6px',
              border: '1px solid var(--card-border)',
              fontSize: '13px',
              outline: 'none',
            }}
          />

          <select
            value={selectedIntent}
            onChange={(e) => setSelectedIntent(e.target.value)}
            style={{
              padding: '10px 14px',
              borderRadius: '6px',
              border: '1px solid var(--card-border)',
              fontSize: '13px',
              backgroundColor: '#ffffff',
              outline: 'none',
            }}
          >
            {INTENT_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <button
            className="btn btn-primary"
            onClick={() => performSearch()}
            disabled={loading}
          >
            {loading ? <span className="spinner"></span> : "Search"}
          </button>
        </div>
      </div>

      {/* Case List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <span className="spinner" style={{ borderColor: 'rgba(0,0,0,0.1)', borderTopColor: 'var(--brand-green)', width: '20px', height: '20px' }}></span>
            <p style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Searching historical index...</p>
          </div>
        ) : results.length > 0 ? (
          results.map((item, idx) => (
            <div key={idx} className="card" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Conversation #{item.conversation_id}
                  </span>
                  <span className="badge badge-neutral" style={{ fontSize: '11px', padding: '2px 8px' }}>
                    {item.intent || "general_inquiry"}
                  </span>
                </div>
                {item.similarity < 1.0 && (
                  <span style={{ fontSize: '11px', fontWeight: 600, color: '#047857', backgroundColor: '#ecfdf5', padding: '2px 6px', borderRadius: '4px' }}>
                    Match: {(item.similarity * 100).toFixed(1)}%
                  </span>
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '13px' }}>
                <div style={{ backgroundColor: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #f1f5f9' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Customer Inquiry:
                  </span>
                  <p style={{ marginTop: '4px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {item.customer_message}
                  </p>
                </div>

                <div style={{ backgroundColor: '#f0fdf4', padding: '12px', borderRadius: '6px', border: '1px solid #dcfce7' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#15803d', textTransform: 'uppercase' }}>
                    Spotify Agent Historical Resolution:
                  </span>
                  <p style={{ marginTop: '4px', color: '#166534', lineHeight: 1.5, fontStyle: 'italic' }}>
                    "{item.brand_response}"
                  </p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            No historical cases found matching your criteria. Try broader keywords.
          </div>
        )}
      </div>
    </div>
  );
}
