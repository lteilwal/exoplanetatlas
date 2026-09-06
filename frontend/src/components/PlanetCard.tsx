import React from "react";
import { PlanetSummary } from "../types";

interface PlanetCardProps {
  planet: PlanetSummary;
  onSelect: (name: string) => void;
  onToggleCompare: (planet: PlanetSummary) => void;
  isCompared: boolean;
}

export const PlanetCard: React.FC<PlanetCardProps> = ({
  planet,
  onSelect,
  onToggleCompare,
  isCompared,
}) => {
  const isHabitable =
    planet.habitability_zone_est === "Conservative Habitable Zone" ||
    planet.habitability_zone_est === "Optimistic Habitable Zone";

  return (
    <div className="planet-card">
      <div>
        {/* Header */}
        <div className="card-header">
          <div>
            <h3 onClick={() => onSelect(planet.name)} className="card-title">
              {planet.name} ↗
            </h3>
            <p className="card-subtitle">
              {planet.planet_class || "Unclassified Planet"}
            </p>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleCompare(planet);
            }}
            className={`btn-icon ${isCompared ? "active" : ""}`}
            style={{ fontSize: "0.65rem", padding: "0.2rem 0.4rem" }}
            title={isCompared ? "Remove from comparison" : "Add to comparison"}
          >
            {isCompared ? "✓ COMPARING" : "+ COMPARE"}
          </button>
        </div>

        {/* Badges */}
        <div className="badge-row">
          {isHabitable && (
            <span className="badge badge-highlight">HABITABLE ZONE</span>
          )}
          {planet.discovery?.discovery_method && (
            <span className="badge">{planet.discovery.discovery_method}</span>
          )}
          {planet.discovery?.discovery_year && (
            <span className="badge" style={{ color: "var(--text-muted)" }}>
              {planet.discovery.discovery_year}
            </span>
          )}
        </div>

        {/* Telemetry Grid */}
        <div className="telemetry-grid-2x2">
          <div>
            <span className="telemetry-item-label">RADIUS</span>
            <span className="telemetry-item-val tabular-nums">
              {planet.radius_earth ? `${planet.radius_earth.toFixed(2)} R_E` : "—"}
            </span>
          </div>
          <div>
            <span className="telemetry-item-label">MASS</span>
            <span className="telemetry-item-val tabular-nums">
              {planet.mass_earth ? `${planet.mass_earth.toFixed(2)} M_E` : "—"}
            </span>
          </div>
          <div>
            <span className="telemetry-item-label">PERIOD</span>
            <span className="telemetry-item-val tabular-nums">
              {planet.orbital_period_days ? `${planet.orbital_period_days.toFixed(2)} d` : "—"}
            </span>
          </div>
          <div>
            <span className="telemetry-item-label">TEMP (T_EQ)</span>
            <span className="telemetry-item-val tabular-nums">
              {planet.equilibrium_temp_k ? `${Math.round(planet.equilibrium_temp_k)} K` : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="card-footer">
        <span>FACILITY:</span>
        <span style={{ color: "var(--text-silver)", maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {planet.discovery?.discovery_facility || "Unknown"}
        </span>
      </div>
    </div>
  );
};
