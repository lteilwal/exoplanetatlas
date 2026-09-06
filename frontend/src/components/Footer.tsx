import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ color: "var(--text-main)" }}>EXOPLANET ATLAS</span>
          <span style={{ color: "var(--border-hover)" }}>|</span>
          <span>STAGE 3 SCIENTIFIC TERMINAL & DATA PLATFORM</span>
        </div>

        <div className="footer-links">
          <a href="/docs" target="_blank" rel="noreferrer">
            REST API SPEC ↗
          </a>
          <a href="https://exoplanetarchive.ipac.caltech.edu/" target="_blank" rel="noreferrer">
            NASA TAP ARCHIVE ↗
          </a>
        </div>
      </div>
    </footer>
  );
};
