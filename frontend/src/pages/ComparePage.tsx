import React from "react";
import { PlanetSummary } from "../types";

interface ComparePageProps {
  comparedPlanets: PlanetSummary[];
  onRemovePlanet: (name: string) => void;
  onClearAll: () => void;
  onSelectPlanet: (name: string) => void;
  onNavigateExplore: () => void;
}

export const ComparePage: React.FC<ComparePageProps> = ({
  comparedPlanets,
  onRemovePlanet,
  onClearAll,
  onSelectPlanet,
  onNavigateExplore,
}) => {
  if (comparedPlanets.length === 0) {
    return (
      <div className="content-wrapper font-mono" style={{ textAlign: "center", padding: "5rem 0" }}>
        <div style={{ fontSize: "2rem", marginBottom: "1rem", color: "var(--text-muted)" }}>⇄</div>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "bold", color: "var(--text-main)", marginBottom: "0.5rem" }}>
          COMPARISON MATRIX EMPTY
        </h2>
        <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", maxWidth: "400px", margin: "0 auto 1.5rem auto" }}>
          Add 2 to 4 exoplanets from the Catalog or Explore view to inspect side-by-side astrophysical parameters and relative scales.
        </p>
        <button onClick={onNavigateExplore} className="btn-primary">
          EXPLORE CATALOG FOR TARGETS
        </button>
      </div>
    );
  }

  const renderComparisonRow = (
    label: string,
    getValue: (p: PlanetSummary) => string | number | null | undefined,
    unit?: string
  ) => {
    return (
      <tr>
        <td className="param-col">{label}</td>
        {comparedPlanets.map((planet) => {
          const val = getValue(planet);
          const display = val !== null && val !== undefined && val !== "" ? String(val) : "—";
          return (
            <td key={planet.id} className="tabular-nums">
              {display} {unit && display !== "—" && <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>{unit}</span>}
            </td>
          );
        })}
      </tr>
    );
  };

  return (
    <div className="content-wrapper font-mono">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">PLANETARY COMPARISON MATRIX</h1>
          <p className="page-subtitle">
            SIDE-BY-SIDE ASTROPHYSICAL EVALUATION ({comparedPlanets.length}/4 TARGETS)
          </p>
        </div>

        <button onClick={onClearAll} className="btn-icon" style={{ padding: "0.4rem 0.8rem" }}>
          ✕ CLEAR MATRIX
        </button>
      </div>

      {/* Comparison Table */}
      <div className="table-container">
        <table className="compare-table">
          <thead>
            <tr>
              <th style={{ width: "200px" }}>PARAMETER</th>
              {comparedPlanets.map((planet) => (
                <th key={planet.id}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span
                      onClick={() => onSelectPlanet(planet.name)}
                      style={{ cursor: "pointer", textDecoration: "underline" }}
                    >
                      {planet.name} ↗
                    </span>
                    <button
                      onClick={() => onRemovePlanet(planet.name)}
                      className="btn-icon"
                      style={{ padding: "0.1rem 0.3rem", fontSize: "0.6rem" }}
                      title="Remove from matrix"
                    >
                      ✕
                    </button>
                  </div>
                  <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", fontWeight: "normal", display: "block", marginTop: "0.2rem" }}>
                    {planet.planet_class || "Unclassified"}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Visual Size Scale Row */}
            <tr style={{ backgroundColor: "var(--bg-surface)" }}>
              <td className="param-col">RELATIVE RADIUS</td>
              {comparedPlanets.map((planet) => {
                const rEarth = planet.radius_earth || 1.0;
                const sizePx = Math.min(48, Math.max(8, rEarth * 6));
                return (
                  <td key={planet.id}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                      <div
                        style={{
                          width: `${sizePx}px`,
                          height: `${sizePx}px`,
                          borderRadius: "50%",
                          backgroundColor: "#ffffff",
                          border: "1px solid #ffffff",
                        }}
                      />
                      <span className="tabular-nums" style={{ fontSize: "0.75rem", fontWeight: 600 }}>
                        {planet.radius_earth ? `${planet.radius_earth.toFixed(2)} R_E` : "—"}
                      </span>
                    </div>
                  </td>
                );
              })}
            </tr>

            {/* Dimensional Properties */}
            {renderComparisonRow("RADIUS (EARTH)", (p) => p.radius_earth ? p.radius_earth.toFixed(2) : null, "R_E")}
            {renderComparisonRow("RADIUS (JUPITER)", (p) => p.radius_jupiter ? p.radius_jupiter.toFixed(3) : null, "R_J")}
            {renderComparisonRow("MASS (EARTH)", (p) => p.mass_earth ? p.mass_earth.toFixed(2) : null, "M_E")}
            {renderComparisonRow("MASS (JUPITER)", (p) => p.mass_jupiter ? p.mass_jupiter.toFixed(3) : null, "M_J")}
            {renderComparisonRow("BULK DENSITY", (p) => p.density_g_cm3 ? p.density_g_cm3.toFixed(2) : null, "g/cm³")}

            {/* Dynamics */}
            {renderComparisonRow("ORBITAL PERIOD", (p) => p.orbital_period_days ? p.orbital_period_days.toFixed(3) : null, "days")}
            {renderComparisonRow("SEMI-MAJOR AXIS", (p) => p.semi_major_axis_au ? p.semi_major_axis_au.toFixed(4) : null, "AU")}
            {renderComparisonRow("ECCENTRICITY", (p) => p.eccentricity !== null && p.eccentricity !== undefined ? p.eccentricity.toFixed(3) : null)}
            {renderComparisonRow("INCLINATION", (p) => p.inclination_deg ? p.inclination_deg.toFixed(2) : null, "deg")}

            {/* Thermodynamics */}
            {renderComparisonRow("EQUILIBRIUM TEMP", (p) => p.equilibrium_temp_k ? Math.round(p.equilibrium_temp_k) : null, "K")}
            {renderComparisonRow("INSOLATION FLUX", (p) => p.insolation_earth ? p.insolation_earth.toFixed(2) : null, "S_E")}
            {renderComparisonRow("HABITABILITY REGIME", (p) => p.habitability_zone_est || "Undetermined")}

            {/* Discovery */}
            {renderComparisonRow("DISCOVERY METHOD", (p) => p.discovery?.discovery_method)}
            {renderComparisonRow("DISCOVERY YEAR", (p) => p.discovery?.discovery_year)}
            {renderComparisonRow("FACILITY / MISSION", (p) => p.discovery?.discovery_facility)}
          </tbody>
        </table>
      </div>
    </div>
  );
};
