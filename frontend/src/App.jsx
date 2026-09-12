import React, { useState } from 'react';
import AgentCopilot from './components/AgentCopilot';
import EvaluationDashboard from './components/EvaluationDashboard';
import HumanReviewView from './components/HumanReviewView';
import HistoricalExplorer from './components/HistoricalExplorer';
import AnalyticsView from './components/AnalyticsView';
import AboutView from './components/AboutView';

export default function App() {
  const [activeTab, setActiveTab] = useState("agent");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const apiBaseUrl =
    (import.meta.env.VITE_API_BASE_URL !== undefined && import.meta.env.VITE_API_BASE_URL !== "")
      ? import.meta.env.VITE_API_BASE_URL
      : (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        ? "http://localhost:8000"
        : "https://resolveai-backend-nsws.onrender.com");

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  const renderActiveView = () => {
    switch (activeTab) {
      case "agent":
        return <AgentCopilot apiBaseUrl={apiBaseUrl} />;
      case "evaluation":
        return <EvaluationDashboard apiBaseUrl={apiBaseUrl} />;
      case "review":
        return <HumanReviewView apiBaseUrl={apiBaseUrl} />;
      case "historical":
        return <HistoricalExplorer apiBaseUrl={apiBaseUrl} />;
      case "analytics":
        return <AnalyticsView apiBaseUrl={apiBaseUrl} />;
      case "about":
        return <AboutView />;
      default:
        return <AgentCopilot apiBaseUrl={apiBaseUrl} />;
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case "agent":
        return { title: "Customer Support Agent Copilot", subtitle: "AI-assisted support grounded in 28,477 historical resolutions" };
      case "evaluation":
        return { title: "Evaluation Benchmark Dashboard", subtitle: "Rigorous evaluation against baselines on 200 Golden Set cases" };
      case "review":
        return { title: "Human Review — Reply Quality Assessment", subtitle: "Blind manual assessment across 6 standardized dimensions (40 interactions)" };
      case "historical":
        return { title: "Historical Support Explorer", subtitle: "Browse and search through real resolved @SpotifyCares Twitter conversations" };
      case "analytics":
        return { title: "Operational Analytics & Telemetry", subtitle: "Volume, routing patterns, and data pipeline statistics" };
      case "about":
        return { title: "System Architecture & Engineering Decisions", subtitle: "Critical analysis, intellectual honesty, and engineering methodology" };
      default:
        return { title: "ResolveAI Copilot", subtitle: "AI Customer Support Copilot" };
    }
  };

  const pageInfo = getPageTitle();

  return (
    <div className="app-container">
      {/* Mobile Drawer Overlay */}
      <div
        className={`sidebar-overlay ${mobileMenuOpen ? 'open' : ''}`}
        onClick={() => setMobileMenuOpen(false)}
        aria-hidden="true"
      />

      {/* Sidebar Navigation */}
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div
          className="sidebar-brand"
          onClick={() => handleTabChange("agent")}
          role="button"
          tabIndex={0}
          title="Return to Agent Copilot (Home)"
          style={{ cursor: "pointer" }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              handleTabChange("agent");
            }
          }}
        >
          <div className="sidebar-logo">R</div>
          <div>
            <div className="sidebar-title">ResolveAI Copilot</div>
            <div className="sidebar-subtitle">@SpotifyCares Copilot</div>
          </div>
          <button
            className="mobile-close-btn"
            onClick={(e) => {
              e.stopPropagation();
              setMobileMenuOpen(false);
            }}
            aria-label="Close navigation menu"
            title="Close navigation"
          >
            ✕
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            id="nav-agent"
            className={`nav-item ${activeTab === "agent" ? "active" : ""}`}
            onClick={() => handleTabChange("agent")}
          >
            <span>💬</span> Agent Copilot
          </button>

          <button
            id="nav-evaluation"
            className={`nav-item ${activeTab === "evaluation" ? "active" : ""}`}
            onClick={() => handleTabChange("evaluation")}
          >
            <span>📊</span> Evaluation & Baselines
          </button>

          <button
            id="nav-review"
            className={`nav-item ${activeTab === "review" ? "active" : ""}`}
            onClick={() => handleTabChange("review")}
          >
            <span>✍️</span> Human Review
          </button>

          <button
            id="nav-historical"
            className={`nav-item ${activeTab === "historical" ? "active" : ""}`}
            onClick={() => handleTabChange("historical")}
          >
            <span>🔍</span> Historical Cases
          </button>

          <button
            id="nav-analytics"
            className={`nav-item ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => handleTabChange("analytics")}
          >
            <span>📈</span> Analytics Telemetry
          </button>

          <button
            id="nav-about"
            className={`nav-item ${activeTab === "about" ? "active" : ""}`}
            onClick={() => handleTabChange("about")}
          >
            <span>ℹ️</span> System Architecture
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>Backend Online (Port 8000)</span>
          </div>
          <p style={{ marginTop: '6px', fontSize: '11px', color: '#64748b' }}>
            ResolveAI Support System
          </p>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="main-content">
        <header className="top-header">
          <div className="header-left-wrap">
            <button
              id="mobile-menu-btn"
              className="mobile-menu-toggle"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
              title="Open Navigation"
            >
              ☰
            </button>
            <div className="header-title-block">
              <h1>{pageInfo.title}</h1>
              <p>{pageInfo.subtitle}</p>
            </div>
          </div>
          <div className="header-meta">
            <span className="meta-pill">Brand: SpotifyCares</span>
            <span className="meta-pill" style={{ color: 'var(--brand-green)' }}>Status: Active</span>
          </div>
        </header>

        <div className="content-body">
          {renderActiveView()}
        </div>
      </main>
    </div>
  );
}

