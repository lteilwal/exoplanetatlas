import React from "react";
import { PlanetSummary } from "../types";

interface SystemArchitectureDiagramProps {
  systemName: string;
  planets: PlanetSummary[];
  onSelectPlanet?: (planetName: string) => void;
  selectedPlanetName?: string;
}

export const SystemArchitectureDiagram: React.FC<SystemArchitectureDiagramProps> = ({
  systemName,
  planets,
  onSelectPlanet,
  selectedPlanetName,
}) => {
  // Sort planets by semi-major axis or orbital period
  const sortedPlanets = [...planets].sort((a, b) => {
    const aVal = a.semi_major_axis_au ?? a.orbital_period_days ?? 0;
    const bVal = b.semi_major_axis_au ?? b.orbital_period_days ?? 0;
    return aVal - bVal;
  });

  return (
    <div className="diagram-box">
      <div className="diagram-header">
        <span>SYSTEM ARCHITECTURE // {systemName} ({planets.length} PLANETS)</span>
        <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>
          ORBITAL SEQUENCE
        </span>
      </div>

      <div style={{ position: "relative", padding: "1.5rem 0", overflowX: "auto" }}>
        {/* Baseline orbital axis */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: 0,
            right: 0,
            height: "1px",
            backgroundColor: "var(--border-hover)",
            transform: "translateY(-50%)",
            zIndex: 0,
          }}
        />

        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", minWidth: "max-content", padding: "0 1rem", position: "relative", zIndex: 1 }}>
          {/* Host Star */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "50%",
                backgroundColor: "#ffffff",
                border: "1px solid #ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#000000",
                fontSize: "0.6rem",
                fontWeight: "bold",
              }}
            >
              ★
            </div>
            <span style={{ fontSize: "0.6rem", color: "var(--text-silver)", marginTop: "0.5rem" }}>STAR</span>
          </div>

          {/* Planets arrayed */}
          {sortedPlanets.map((planet, idx) => {
            const isSelected = selectedPlanetName === planet.name;
            const rEarth = planet.radius_earth || 1.0;
            const sizePx = Math.min(24, Math.max(8, rEarth * 4));

            return (
              <div
                key={planet.id || idx}
                onClick={() => onSelectPlanet && onSelectPlanet(planet.name)}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  cursor: "pointer",
                  padding: "0.5rem",
                  border: isSelected ? "1px solid #ffffff" : "1px solid transparent",
                  backgroundColor: isSelected ? "var(--bg-elevated)" : "transparent",
                  transition: "all 0.15s ease",
                }}
              >
                {/* Distance marker */}
                <span style={{ fontSize: "0.6rem", color: "var(--text-dim)", marginBottom: "0.25rem" }} className="tabular-nums">
                  {planet.semi_major_axis_au
                    ? `${planet.semi_major_axis_au.toFixed(2)} AU`
                    : planet.orbital_period_days
                    ? `${planet.orbital_period_days.toFixed(1)} d`
                    : "—"}
                </span>

                {/* Planet Body */}
                <div
                  style={{
                    width: `${sizePx}px`,
                    height: `${sizePx}px`,
                    borderRadius: "50%",
                    border: isSelected ? "1px solid #ffffff" : "1px solid var(--text-muted)",
                    backgroundColor: isSelected ? "#ffffff" : "var(--bg-elevated)",
                    transition: "transform 0.15s ease",
                  }}
                />

                {/* Name */}
                <span
                  style={{
                    fontSize: "0.65rem",
                    marginTop: "0.5rem",
                    fontWeight: isSelected ? "bold" : 500,
                    color: isSelected ? "var(--text-main)" : "var(--text-silver)",
                    maxWidth: "80px",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    textAlign: "center",
                  }}
                >
                  {planet.planet_letter || planet.name.replace(systemName, "").trim() || planet.name}
                </span>

                {/* Regime */}
                <span style={{ fontSize: "0.55rem", color: "var(--text-dim)", textTransform: "uppercase", marginTop: "0.15rem" }}>
                  {planet.planet_class || "Planet"}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
