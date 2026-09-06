import React from "react";

interface NavbarProps {
  currentTab: string;
  onNavigate: (tab: string, param?: string) => void;
  totalPlanets?: number;
  compareCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onNavigate,
  totalPlanets = 6354,
  compareCount = 0,
}) => {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Brand */}
        <div onClick={() => onNavigate("catalog")} className="brand">
          <div className="brand-icon">⏣</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="brand-title">EXOPLANET ATLAS</span>
              <span className="badge" style={{ fontSize: "0.6rem", padding: "0.1rem 0.3rem" }}>
                v1.0
              </span>
            </div>
            <p className="brand-subtitle">
              NASA EXOPLANET ARCHIVE // {totalPlanets.toLocaleString()} CONFIRMED
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-links">
          <button
            onClick={() => onNavigate("catalog")}
            className={`nav-btn ${currentTab === "catalog" || currentTab === "planet" ? "active" : ""}`}
          >
            <span>▤</span>
            <span>CATALOG</span>
          </button>

          <button
            onClick={() => onNavigate("systems")}
            className={`nav-btn ${currentTab === "systems" || currentTab === "system" ? "active" : ""}`}
          >
            <span>◎</span>
            <span>SYSTEMS</span>
          </button>

          <button
            onClick={() => onNavigate("compare")}
            className={`nav-btn ${currentTab === "compare" ? "active" : ""}`}
          >
            <span>⇄</span>
            <span>COMPARE</span>
            {compareCount > 0 && <span className="nav-badge">{compareCount}</span>}
          </button>

          <button
            onClick={() => onNavigate("explore")}
            className={`nav-btn ${currentTab === "explore" ? "active" : ""}`}
          >
            <span>◇</span>
            <span>EXPLORE</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
