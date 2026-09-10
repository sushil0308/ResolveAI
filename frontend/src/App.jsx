import React, { useState } from 'react';
import AgentCopilot from './components/AgentCopilot';
import EvaluationDashboard from './components/EvaluationDashboard';
import HistoricalExplorer from './components/HistoricalExplorer';
import AnalyticsView from './components/AnalyticsView';
import AboutView from './components/AboutView';

export default function App() {
  const [activeTab, setActiveTab] = useState("agent");
  const apiBaseUrl = "http://localhost:8000";

  const renderActiveView = () => {
    switch (activeTab) {
      case "agent":
        return <AgentCopilot apiBaseUrl={apiBaseUrl} />;
      case "evaluation":
        return <EvaluationDashboard apiBaseUrl={apiBaseUrl} />;
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
      case "historical":
        return { title: "Historical Support Explorer", subtitle: "Browse and search through real resolved @SpotifyCares Twitter conversations" };
      case "analytics":
        return { title: "Operational Analytics & Telemetry", subtitle: "Volume, routing patterns, and data pipeline statistics" };
      case "about":
        return { title: "System Architecture & Engineering Decisions", subtitle: "Critical analysis, intellectual honesty, and engineering roadmap" };
      default:
        return { title: "ResolveAI Copilot", subtitle: "AI Customer Support Copilot" };
    }
  };

  const pageInfo = getPageTitle();

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">R</div>
          <div>
            <div className="sidebar-title">ResolveAI Copilot</div>
            <div className="sidebar-subtitle">@SpotifyCares Copilot</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            id="nav-agent"
            className={`nav-item ${activeTab === "agent" ? "active" : ""}`}
            onClick={() => setActiveTab("agent")}
          >
            <span>💬</span> Agent Copilot
          </button>

          <button
            id="nav-evaluation"
            className={`nav-item ${activeTab === "evaluation" ? "active" : ""}`}
            onClick={() => setActiveTab("evaluation")}
          >
            <span>📊</span> Evaluation & Baselines
          </button>

          <button
            id="nav-historical"
            className={`nav-item ${activeTab === "historical" ? "active" : ""}`}
            onClick={() => setActiveTab("historical")}
          >
            <span>🔍</span> Historical Cases
          </button>

          <button
            id="nav-analytics"
            className={`nav-item ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => setActiveTab("analytics")}
          >
            <span>📈</span> Analytics Telemetry
          </button>

          <button
            id="nav-about"
            className={`nav-item ${activeTab === "about" ? "active" : ""}`}
            onClick={() => setActiveTab("about")}
          >
            <span>ℹ️</span> About & Roadmap
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
          <div className="header-title-block">
            <h1>{pageInfo.title}</h1>
            <p>{pageInfo.subtitle}</p>
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
