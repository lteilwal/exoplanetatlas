import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { OrbitDiagram } from "../components/OrbitDiagram";
import { ScaleDiagram } from "../components/ScaleDiagram";
import { PlanetAISummaryResponse, PlanetDetail, PlanetQAResponse, PlanetSummary } from "../types";

interface PlanetDetailPageProps {
  planetName: string;
  onBack: () => void;
  onNavigateSystem: (systemName: string) => void;
  onToggleCompare: (planet: PlanetSummary) => void;
  isCompared: boolean;
}

export const PlanetDetailPage: React.FC<PlanetDetailPageProps> = ({
  planetName,
  onBack,
  onNavigateSystem,
  onToggleCompare,
  isCompared,
}) => {
  const [planet, setPlanet] = useState<PlanetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI Summary State
  const [aiSummary, setAiSummary] = useState<PlanetAISummaryResponse | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  // AI Q&A State
  const [qaInput, setQaInput] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [qaHistory, setQaHistory] = useState<PlanetQAResponse[]>([]);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      setAiSummary(null);
      setQaHistory([]);
      try {
        const data = await api.getPlanet(planetName);
        setPlanet(data);

        // Fetch AI Summary asynchronously
        setAiLoading(true);
        api.getPlanetAiSummary(planetName)
          .then((res) => setAiSummary(res))
          .catch((err) => console.error("Failed to load AI summary", err))
          .finally(() => setAiLoading(false));

      } catch (err: any) {
        setError(err.message || "Failed to load planet details");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [planetName]);

  const handleAskQuestion = async (e?: React.FormEvent, overrideQuestion?: string) => {
    if (e) e.preventDefault();
    const query = overrideQuestion || qaInput;
    if (!query.trim()) return;

    setQaLoading(true);
    try {
      const res = await api.askPlanetAiQuestion(planetName, query);
      setQaHistory((prev) => [res, ...prev]);
      if (!overrideQuestion) setQaInput("");
    } catch (err: any) {
      console.error("QA error", err);
    } finally {
      setQaLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="content-wrapper font-mono" style={{ textAlign: "center", padding: "6rem 0", color: "var(--text-muted)" }}>
        LOADING PLANETARY DOSSIER FOR {planetName}...
      </div>
    );
  }

  if (error || !planet) {
    return (
      <div className="content-wrapper font-mono">
        <button onClick={onBack} className="btn-icon" style={{ marginBottom: "1.5rem" }}>
          ← BACK TO CATALOG
        </button>
        <div style={{ padding: "2rem", border: "1px solid var(--border)", backgroundColor: "var(--bg-card)", textAlign: "center" }}>
          <div style={{ color: "var(--text-main)", marginBottom: "0.5rem" }}>ERROR FETCHING PLANET DOSSIER</div>
          <div style={{ color: "var(--text-muted)" }}>{error || "Planet not found"}</div>
        </div>
      </div>
    );
  }

  const isHabitable =
    planet.habitability_zone_est === "Conservative Habitable Zone" ||
    planet.habitability_zone_est === "Optimistic Habitable Zone";

  return (
    <div className="content-wrapper font-mono">
      {/* Top Header & Actions */}
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button onClick={onBack} className="btn-icon" title="Back">
            ← BACK
          </button>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h1 className="page-title">{planet.name}</h1>
              {isHabitable && (
                <span className="badge badge-highlight">
                  HABITABLE ZONE
                </span>
              )}
            </div>
            <p className="page-subtitle">
              HOST SYSTEM:{" "}
              <span
                onClick={() => planet.system?.name && onNavigateSystem(planet.system.name)}
                style={{ color: "var(--text-main)", textDecoration: "underline", cursor: "pointer", fontWeight: 600 }}
              >
                {planet.system?.name || "Unknown"}
              </span>
            </p>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <button
            onClick={() => onToggleCompare(planet)}
            className={`btn-icon ${isCompared ? "active" : ""}`}
            style={{ padding: "0.4rem 0.8rem", fontWeight: 600 }}
          >
            {isCompared ? "✓ IN COMPARISON" : "+ ADD TO COMPARE"}
          </button>

          {planet.system?.name && (
            <button
              onClick={() => onNavigateSystem(planet.system!.name)}
              className="btn-icon"
              style={{ padding: "0.4rem 0.8rem" }}
            >
              ◎ VIEW SYSTEM
            </button>
          )}
        </div>
      </div>

      {/* AI Grounded Factual Summary Panel */}
      <div className="panel" style={{ marginBottom: "1.5rem" }}>
        <div className="panel-header">
          <span>AI SCIENTIFIC DOSSIER (GEMINI + MCP DATABASE TOOLS)</span>
          <span style={{ fontSize: "0.65rem", color: "var(--text-dim)" }}>
            SOURCE: NASA EXOPLANET ARCHIVE VIA MCP
          </span>
        </div>
        {aiLoading ? (
          <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
            Synthesizing factual narrative from relational records...
          </div>
        ) : aiSummary ? (
          <div>
            <p style={{ color: "var(--text-main)", fontSize: "0.8rem", lineHeight: 1.6, marginBottom: "0.75rem" }}>
              {aiSummary.summary}
            </p>
            {aiSummary.key_facts.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", paddingTop: "0.5rem", borderTop: "1px solid var(--border)" }}>
                {aiSummary.key_facts.map((fact, idx) => (
                  <span key={idx} className="badge" style={{ color: "var(--text-silver)" }}>
                    • {fact}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
            Summary generated from direct parameter tables below.
          </div>
        )}
      </div>

      {/* Grid: Left Visuals, Right Telemetry */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
          <OrbitDiagram
            semiMajorAxisAu={planet.semi_major_axis_au}
            eccentricity={planet.eccentricity}
            stellarMassSolar={planet.star?.mass_solar}
            planetName={planet.name}
            habitabilityZone={planet.habitability_zone_est}
          />
          <ScaleDiagram
            radiusEarth={planet.radius_earth}
            planetName={planet.name}
            planetClass={planet.planet_class}
          />
        </div>

        {/* Telemetry Panels */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* 1. Physical Dimensions */}
          <div className="panel">
            <div className="panel-header">
              <span>PHYSICAL DIMENSIONS & BULK CHARACTERISTICS</span>
            </div>
            <div className="grid-4col">
              <MetricCard
                label="Radius (Earth)"
                value={planet.radius_earth ? planet.radius_earth.toFixed(2) : null}
                unit="R_E"
                subValue={planet.radius_jupiter ? `${planet.radius_jupiter.toFixed(3)} R_J` : undefined}
                highlight
              />
              <MetricCard
                label="Mass (Earth)"
                value={planet.mass_earth ? planet.mass_earth.toFixed(2) : null}
                unit="M_E"
                subValue={planet.mass_jupiter ? `${planet.mass_jupiter.toFixed(3)} M_J` : undefined}
                highlight
              />
              <MetricCard
                label="Mean Density"
                value={planet.density_g_cm3 ? planet.density_g_cm3.toFixed(2) : null}
                unit="g/cm³"
                subValue="Bulk Structure"
              />
              <MetricCard
                label="Morphology"
                value={planet.planet_class || "Unclassified"}
              />
            </div>
          </div>

          {/* 2. Orbital Mechanics */}
          <div className="panel">
            <div className="panel-header">
              <span>ORBITAL DYNAMICS & EPHEMERIS</span>
            </div>
            <div className="grid-4col">
              <MetricCard
                label="Orbital Period"
                value={planet.orbital_period_days ? planet.orbital_period_days.toFixed(3) : null}
                unit="days"
              />
              <MetricCard
                label="Semi-Major Axis"
                value={planet.semi_major_axis_au ? planet.semi_major_axis_au.toFixed(4) : null}
                unit="AU"
              />
              <MetricCard
                label="Eccentricity (e)"
                value={planet.eccentricity !== null && planet.eccentricity !== undefined ? planet.eccentricity.toFixed(3) : null}
              />
              <MetricCard
                label="Inclination"
                value={planet.inclination_deg ? planet.inclination_deg.toFixed(2) : null}
                unit="deg"
              />
            </div>
          </div>

          {/* 3. Thermodynamics */}
          <div className="panel">
            <div className="panel-header">
              <span>THERMODYNAMICS & STELLAR FLUX</span>
            </div>
            <div className="grid-3col">
              <MetricCard
                label="Equilibrium Temp"
                value={planet.equilibrium_temp_k ? Math.round(planet.equilibrium_temp_k) : null}
                unit="K"
                subValue={planet.equilibrium_temp_k ? `${Math.round(planet.equilibrium_temp_k - 273.15)} °C` : undefined}
                highlight
              />
              <MetricCard
                label="Insolation Flux"
                value={planet.insolation_earth ? planet.insolation_earth.toFixed(2) : null}
                unit="S_E"
                subValue="Earth Equivalent"
              />
              <MetricCard
                label="Habitability Regime"
                value={planet.habitability_zone_est || "Undetermined"}
              />
            </div>
          </div>

          {/* 4. Host Star */}
          {planet.star && (
            <div className="panel">
              <div className="panel-header">
                <span>HOST STAR // {planet.star.name}</span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>
                  SPECTRAL: {planet.star.spectral_type || "N/A"}
                </span>
              </div>
              <div className="grid-4col">
                <div>
                  <span className="telemetry-item-label">EFFECTIVE TEMP</span>
                  <span className="telemetry-item-val tabular-nums">
                    {planet.star.effective_temp_k ? `${Math.round(planet.star.effective_temp_k)} K` : "—"}
                  </span>
                </div>
                <div>
                  <span className="telemetry-item-label">STELLAR MASS</span>
                  <span className="telemetry-item-val tabular-nums">
                    {planet.star.mass_solar ? `${planet.star.mass_solar.toFixed(2)} M_Sun` : "—"}
                  </span>
                </div>
                <div>
                  <span className="telemetry-item-label">STELLAR RADIUS</span>
                  <span className="telemetry-item-val tabular-nums">
                    {planet.star.radius_solar ? `${planet.star.radius_solar.toFixed(2)} R_Sun` : "—"}
                  </span>
                </div>
                <div>
                  <span className="telemetry-item-label">METALLICITY [Fe/H]</span>
                  <span className="telemetry-item-val tabular-nums">
                    {planet.star.metallicity_dex !== null && planet.star.metallicity_dex !== undefined
                      ? `${planet.star.metallicity_dex.toFixed(2)} dex`
                      : "—"}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* 5. Discovery Circumstances */}
          {planet.discovery && (
            <div className="panel">
              <div className="panel-header">
                <span>DISCOVERY CIRCUMSTANCES & ARCHIVE BIBLIOGRAPHY</span>
              </div>
              <div className="grid-3col" style={{ marginBottom: "0.75rem" }}>
                <div>
                  <span className="telemetry-item-label">DETECTION METHOD</span>
                  <span className="telemetry-item-val">{planet.discovery.discovery_method}</span>
                </div>
                <div>
                  <span className="telemetry-item-label">DISCOVERY YEAR</span>
                  <span className="telemetry-item-val">{planet.discovery.discovery_year || "—"}</span>
                </div>
                <div>
                  <span className="telemetry-item-label">OBSERVATORY / FACILITY</span>
                  <span className="telemetry-item-val">{planet.discovery.discovery_facility || "—"}</span>
                </div>
              </div>
              {planet.discovery.reference_name && (
                <div
                  style={{
                    borderTop: "1px solid var(--border)",
                    paddingTop: "0.5rem",
                    fontSize: "0.7rem",
                    display: "flex",
                    justifyContent: "space-between",
                    color: "var(--text-muted)",
                  }}
                >
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    REFERENCE: {planet.discovery.reference_name}
                  </span>
                  <a
                    href={`https://ui.adsabs.harvard.edu/search/q=${encodeURIComponent(planet.discovery.reference_name)}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "var(--text-main)", marginLeft: "0.5rem" }}
                  >
                    ADS ↗
                  </a>
                </div>
              )}
            </div>
          )}

          {/* 6. Grounded AI Q&A Panel */}
          <div className="panel">
            <div className="panel-header">
              <span>FACTUAL ARCHIVAL Q&A</span>
              <span style={{ fontSize: "0.65rem", color: "var(--text-dim)" }}>
                STRICTLY DATA-GROUNDED
              </span>
            </div>

            {/* Quick Sample Questions */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.75rem" }}>
              <span style={{ fontSize: "0.65rem", color: "var(--text-dim)", alignSelf: "center" }}>SAMPLE:</span>
              {[
                "What is the mass?",
                "Is it in the habitable zone?",
                "How was it discovered?",
                "What star does it orbit?",
              ].map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAskQuestion(undefined, q)}
                  className="preset-btn"
                  style={{ fontSize: "0.65rem", padding: "0.2rem 0.4rem" }}
                  disabled={qaLoading}
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Question Input Form */}
            <form onSubmit={handleAskQuestion} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
              <input
                type="text"
                value={qaInput}
                onChange={(e) => setQaInput(e.target.value)}
                placeholder="Ask a factual question about this planet (e.g. mass, radius, distance, temperature)..."
                className="search-input"
                disabled={qaLoading}
              />
              <button type="submit" className="btn-primary" disabled={qaLoading}>
                {qaLoading ? "QUERYING..." : "ASK"}
              </button>
            </form>

            {/* Q&A History Stream */}
            {qaHistory.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
                {qaHistory.map((item, idx) => (
                  <div key={idx} style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border)", padding: "0.75rem" }}>
                    <div style={{ color: "var(--text-main)", fontWeight: 600, fontSize: "0.75rem", marginBottom: "0.35rem" }}>
                      Q: {item.question}
                    </div>
                    <div style={{ color: "var(--text-silver)", fontSize: "0.75rem", lineHeight: 1.5 }}>
                      A: {item.answer}
                    </div>
                    {item.tools_used && item.tools_used.length > 0 && (
                      <div style={{ marginTop: "0.4rem", display: "flex", gap: "0.4rem", alignItems: "center" }}>
                        <span style={{ fontSize: "0.6rem", color: "var(--text-dim)" }}>MCP TOOLS:</span>
                        {item.tools_used.map((t, tidx) => (
                          <span key={tidx} className="badge" style={{ fontSize: "0.55rem", padding: "0.1rem 0.3rem" }}>
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
