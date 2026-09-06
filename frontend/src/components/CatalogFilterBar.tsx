import React, { useState } from "react";
import { CatalogFilterParams } from "../types";

interface CatalogFilterBarProps {
  filters: CatalogFilterParams;
  onFilterChange: (newFilters: CatalogFilterParams) => void;
  onReset: () => void;
}

export const CatalogFilterBar: React.FC<CatalogFilterBarProps> = ({
  filters,
  onFilterChange,
  onReset,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [searchInput, setSearchInput] = useState(filters.search || "");

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilterChange({ ...filters, search: searchInput, page: 1 });
  };

  const handlePreset = (preset: Partial<CatalogFilterParams>) => {
    onFilterChange({ ...filters, ...preset, page: 1 });
  };

  return (
    <div className="filter-container">
      {/* Top Search & Presets */}
      <div className="filter-main">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="SEARCH BY PLANET, SYSTEM, STAR, OR FACILITY (E.G. 'TRAPPIST', 'KEPLER-186')..."
            className="search-input"
          />
          <button type="submit" className="btn-primary">
            SEARCH
          </button>
        </form>

        {/* Quick Presets */}
        <div className="preset-group">
          <span style={{ color: "var(--text-dim)", marginRight: "0.25rem" }}>PRESETS:</span>
          <button
            onClick={() =>
              handlePreset({ habitability_zone_est: "Conservative Habitable Zone", planet_class: undefined })
            }
            className={`preset-btn ${filters.habitability_zone_est === "Conservative Habitable Zone" ? "active" : ""}`}
          >
            HABITABLE ZONE
          </button>
          <button
            onClick={() =>
              handlePreset({ planet_class: "Terrestrial", habitability_zone_est: undefined })
            }
            className={`preset-btn ${filters.planet_class === "Terrestrial" ? "active" : ""}`}
          >
            TERRESTRIAL
          </button>
          <button
            onClick={() =>
              handlePreset({ planet_class: "Super-Earth", habitability_zone_est: undefined })
            }
            className={`preset-btn ${filters.planet_class === "Super-Earth" ? "active" : ""}`}
          >
            SUPER-EARTH
          </button>
          <button
            onClick={() => handlePreset({ discovery_method: "Direct Imaging" })}
            className={`preset-btn ${filters.discovery_method === "Direct Imaging" ? "active" : ""}`}
          >
            DIRECT IMAGING
          </button>

          <button
            onClick={() => setExpanded(!expanded)}
            className={`btn-icon ${expanded ? "active" : ""}`}
            title="Toggle advanced filters"
          >
            <span>⚙ {expanded ? "HIDE" : "FILTERS"}</span>
          </button>

          <button
            onClick={() => {
              setSearchInput("");
              onReset();
            }}
            className="btn-icon"
            title="Reset Filters"
          >
            <span>↺</span>
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {expanded && (
        <div className="filter-drawer">
          {/* Classification */}
          <div className="form-group">
            <label>PLANET CLASSIFICATION</label>
            <select
              value={filters.planet_class || ""}
              onChange={(e) => onFilterChange({ ...filters, planet_class: e.target.value || undefined, page: 1 })}
              className="form-select"
            >
              <option value="">ALL CLASSIFICATIONS</option>
              <option value="Terrestrial">Terrestrial (&lt;1.25 R_E)</option>
              <option value="Super-Earth">Super-Earth (1.25–2.0 R_E)</option>
              <option value="Sub-Neptune">Sub-Neptune (2.0–4.0 R_E)</option>
              <option value="Neptune-like">Neptune-like (4.0–6.0 R_E)</option>
              <option value="Gas Giant">Gas Giant (&gt;6.0 R_E)</option>
            </select>
          </div>

          {/* Habitability Zone */}
          <div className="form-group">
            <label>HABITABILITY REGIME</label>
            <select
              value={filters.habitability_zone_est || ""}
              onChange={(e) => onFilterChange({ ...filters, habitability_zone_est: e.target.value || undefined, page: 1 })}
              className="form-select"
            >
              <option value="">ALL REGIMES</option>
              <option value="Conservative Habitable Zone">Conservative Habitable Zone</option>
              <option value="Optimistic Habitable Zone">Optimistic Habitable Zone</option>
              <option value="Hot Zone">Hot Zone (Too Hot)</option>
              <option value="Cold Zone">Cold Zone (Too Cold)</option>
            </select>
          </div>

          {/* Discovery Method */}
          <div className="form-group">
            <label>DISCOVERY METHOD</label>
            <select
              value={filters.discovery_method || ""}
              onChange={(e) => onFilterChange({ ...filters, discovery_method: e.target.value || undefined, page: 1 })}
              className="form-select"
            >
              <option value="">ALL METHODS</option>
              <option value="Transit">Transit</option>
              <option value="Radial Velocity">Radial Velocity</option>
              <option value="Microlensing">Microlensing</option>
              <option value="Direct Imaging">Direct Imaging</option>
              <option value="Transit Timing Variations">Transit Timing Variations (TTV)</option>
              <option value="Astrometry">Astrometry</option>
            </select>
          </div>

          {/* Sort By */}
          <div className="form-group">
            <label>SORT METRIC</label>
            <div style={{ display: "flex", gap: "0.25rem" }}>
              <select
                value={filters.sort_by || "name"}
                onChange={(e) => onFilterChange({ ...filters, sort_by: e.target.value, page: 1 })}
                className="form-select"
                style={{ flex: 1 }}
              >
                <option value="name">Name</option>
                <option value="distance">Distance from Earth</option>
                <option value="radius">Planet Radius</option>
                <option value="mass">Planet Mass</option>
                <option value="period">Orbital Period</option>
                <option value="temp">Equilibrium Temp</option>
                <option value="year">Discovery Year</option>
              </select>
              <select
                value={filters.order || "asc"}
                onChange={(e) => onFilterChange({ ...filters, order: e.target.value as "asc" | "desc", page: 1 })}
                className="form-select"
                style={{ width: "70px" }}
              >
                <option value="asc">ASC</option>
                <option value="desc">DESC</option>
              </select>
            </div>
          </div>

          {/* Max Distance */}
          <div className="form-group">
            <label>MAX DISTANCE (PC)</label>
            <input
              type="number"
              placeholder="e.g. 50"
              value={filters.max_distance_pc || ""}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  max_distance_pc: e.target.value ? Number(e.target.value) : undefined,
                  page: 1,
                })
              }
              className="form-input"
            />
          </div>

          {/* Max Orbital Period */}
          <div className="form-group">
            <label>MAX ORBITAL PERIOD (DAYS)</label>
            <input
              type="number"
              placeholder="e.g. 365"
              value={filters.max_period_days || ""}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  max_period_days: e.target.value ? Number(e.target.value) : undefined,
                  page: 1,
                })
              }
              className="form-input"
            />
          </div>

          {/* Radius Range */}
          <div className="form-group">
            <label>RADIUS RANGE (R_EARTH)</label>
            <div className="range-inputs">
              <input
                type="number"
                placeholder="MIN"
                value={filters.min_radius_earth || ""}
                onChange={(e) =>
                  onFilterChange({
                    ...filters,
                    min_radius_earth: e.target.value ? Number(e.target.value) : undefined,
                    page: 1,
                  })
                }
                className="form-input"
              />
              <span style={{ color: "var(--text-dim)" }}>-</span>
              <input
                type="number"
                placeholder="MAX"
                value={filters.max_radius_earth || ""}
                onChange={(e) =>
                  onFilterChange({
                    ...filters,
                    max_radius_earth: e.target.value ? Number(e.target.value) : undefined,
                    page: 1,
                  })
                }
                className="form-input"
              />
            </div>
          </div>

          {/* Discovery Year */}
          <div className="form-group">
            <label>DISCOVERY YEAR</label>
            <input
              type="number"
              placeholder="e.g. 2024"
              value={filters.discovery_year || ""}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  discovery_year: e.target.value ? Number(e.target.value) : undefined,
                  page: 1,
                })
              }
              className="form-input"
            />
          </div>
        </div>
      )}
    </div>
  );
};
