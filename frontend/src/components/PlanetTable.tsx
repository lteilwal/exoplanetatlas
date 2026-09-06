import React from "react";
import { PlanetSummary } from "../types";

interface PlanetTableProps {
  planets: PlanetSummary[];
  onSelect: (name: string) => void;
  onToggleCompare: (planet: PlanetSummary) => void;
  comparedPlanetNames: string[];
  sortBy: string;
  onSortChange: (sortBy: string) => void;
}

export const PlanetTable: React.FC<PlanetTableProps> = ({
  planets,
  onSelect,
  onToggleCompare,
  comparedPlanetNames,
  sortBy,
  onSortChange,
}) => {
  const renderSortHeader = (label: string, field: string) => {
    const isActive = sortBy === field;
    return (
      <th onClick={() => onSortChange(field)} className="sortable">
        <span>{label}</span> {isActive ? "↕" : ""}
      </th>
    );
  };

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: "40px", textAlign: "center" }}>CMP</th>
            {renderSortHeader("PLANET NAME", "name")}
            <th>CLASSIFICATION</th>
            {renderSortHeader("RADIUS (R_E)", "radius")}
            {renderSortHeader("MASS (M_E)", "mass")}
            {renderSortHeader("PERIOD (DAYS)", "period")}
            {renderSortHeader("TEMP (K)", "temp")}
            {renderSortHeader("METHOD", "method")}
            {renderSortHeader("YEAR", "year")}
          </tr>
        </thead>
        <tbody>
          {planets.map((planet) => {
            const isCompared = comparedPlanetNames.includes(planet.name);
            return (
              <tr key={planet.id} onClick={() => onSelect(planet.name)}>
                {/* Compare Checkbox */}
                <td
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleCompare(planet);
                  }}
                  style={{ textAlign: "center" }}
                >
                  <button
                    className={`btn-icon ${isCompared ? "active" : ""}`}
                    style={{ width: "20px", height: "20px", padding: 0, fontSize: "0.65rem" }}
                  >
                    {isCompared ? "✓" : "+"}
                  </button>
                </td>

                {/* Planet Name */}
                <td className="planet-name-cell font-mono" style={{ fontWeight: 600 }}>
                  {planet.name}
                </td>

                {/* Classification */}
                <td style={{ color: "var(--text-silver)" }}>
                  {planet.planet_class || "—"}
                </td>

                {/* Radius */}
                <td className="tabular-nums" style={{ color: "var(--text-main)" }}>
                  {planet.radius_earth ? planet.radius_earth.toFixed(2) : "—"}
                </td>

                {/* Mass */}
                <td className="tabular-nums" style={{ color: "var(--text-main)" }}>
                  {planet.mass_earth ? planet.mass_earth.toFixed(2) : "—"}
                </td>

                {/* Period */}
                <td className="tabular-nums" style={{ color: "var(--text-main)" }}>
                  {planet.orbital_period_days ? planet.orbital_period_days.toFixed(2) : "—"}
                </td>

                {/* Temp */}
                <td className="tabular-nums" style={{ color: "var(--text-main)" }}>
                  {planet.equilibrium_temp_k ? Math.round(planet.equilibrium_temp_k) : "—"}
                </td>

                {/* Method */}
                <td style={{ color: "var(--text-silver)" }}>
                  {planet.discovery?.discovery_method || "—"}
                </td>

                {/* Year */}
                <td className="tabular-nums" style={{ color: "var(--text-muted)" }}>
                  {planet.discovery?.discovery_year || "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
