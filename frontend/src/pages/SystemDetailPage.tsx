import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { SystemArchitectureDiagram } from "../components/SystemArchitectureDiagram";
import { PlanetSummary, SystemDetail } from "../types";

interface SystemDetailPageProps {
  systemName: string;
  onBack: () => void;
  onSelectPlanet: (planetName: string) => void;
  onToggleCompare: (planet: PlanetSummary) => void;
  comparedPlanets: PlanetSummary[];
}

export const SystemDetailPage: React.FC<SystemDetailPageProps> = ({
  systemName,
  onBack,
  onSelectPlanet,
  onToggleCompare,
  comparedPlanets,
}) => {
  const [system, setSystem] = useState<SystemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getSystem(systemName);
        setSystem(data);
      } catch (err: any) {
        setError(err.message || "Failed to load system details");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [systemName]);

  if (loading) {
    return (
      <div className="content-wrapper font-mono" style={{ textAlign: "center", padding: "6rem 0", color: "var(--text-muted)" }}>
        LOADING SYSTEM TELEMETRY FOR {systemName}...
      </div>
    );
  }

  if (error || !system) {
    return (
      <div className="content-wrapper font-mono">
        <button onClick={onBack} className="btn-icon" style={{ marginBottom: "1.5rem" }}>
          ← BACK
        </button>
        <div style={{ padding: "2rem", border: "1px solid var(--border)", backgroundColor: "var(--bg-card)", textAlign: "center" }}>
          <div style={{ color: "var(--text-main)", marginBottom: "0.5rem" }}>ERROR FETCHING SYSTEM</div>
          <div style={{ color: "var(--text-muted)" }}>{error || "System not found"}</div>
        </div>
      </div>
    );
  }

  const comparedNames = comparedPlanets.map((p) => p.name);

  return (
    <div className="content-wrapper font-mono">
      {/* Header */}
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button onClick={onBack} className="btn-icon">
            ← BACK
          </button>
          <div>
            <h1 className="page-title">SYSTEM // {system.name}</h1>
            <p className="page-subtitle">
              STELLAR MULTIPLICITY: {system.star_count || 1} | CONFIRMED PLANETS: {system.planet_count || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Architecture Diagram */}
      <div style={{ marginBottom: "1.5rem" }}>
        <SystemArchitectureDiagram
          systemName={system.name}
          planets={system.planets || []}
          onSelectPlanet={onSelectPlanet}
        />
      </div>

      {/* Coordinates & Photometry */}
      <div className="grid-2col" style={{ marginBottom: "1.5rem" }}>
        {/* Astrometry */}
        <div className="panel" style={{ margin: 0 }}>
          <div className="panel-header">
            <span>ASTROMETRY & SKY POSITION (ICRS J2000)</span>
          </div>
          <div className="grid-3col">
            <MetricCard
              label="Distance"
              value={system.distance_pc ? system.distance_pc.toFixed(2) : null}
              unit="pc"
              subValue={system.distance_pc ? `${(system.distance_pc * 3.262).toFixed(1)} ly` : undefined}
              highlight
            />
            <MetricCard
              label="Right Ascension"
              value={system.ra ? `${system.ra.toFixed(4)}°` : null}
            />
            <MetricCard
              label="Declination"
              value={system.dec ? `${system.dec.toFixed(4)}°` : null}
            />
            <MetricCard
              label="Parallax"
              value={system.parallax_mas ? system.parallax_mas.toFixed(3) : null}
              unit="mas"
            />
            <MetricCard
              label="Proper Motion"
              value={system.proper_motion_mas_yr ? system.proper_motion_mas_yr.toFixed(2) : null}
              unit="mas/yr"
            />
            <MetricCard
              label="Circumbinary"
              value={system.is_circumbinary ? "YES" : "NO"}
            />
          </div>
        </div>

        {/* Photometry */}
        <div className="panel" style={{ margin: 0 }}>
          <div className="panel-header">
            <span>APPARENT PHOTOMETRY (MAGNITUDES)</span>
          </div>
          <div className="grid-4col">
            <MetricCard label="Johnson V" value={system.v_mag ? system.v_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="Gaia G" value={system.gaia_mag ? system.gaia_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="TESS" value={system.tess_mag ? system.tess_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="Kepler" value={system.kepler_mag ? system.kepler_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="2MASS J" value={system.j_mag ? system.j_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="2MASS H" value={system.h_mag ? system.h_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="2MASS Ks" value={system.k_mag ? system.k_mag.toFixed(2) : null} unit="mag" />
            <MetricCard label="Johnson B" value={system.b_mag ? system.b_mag.toFixed(2) : null} unit="mag" />
          </div>
        </div>
      </div>

      {/* Orbiting Planets Grid */}
      <div className="panel">
        <div className="panel-header">
          <span>CONSTITUENT PLANETS ({system.planets?.length || 0})</span>
        </div>

        <div className="card-grid">
          {system.planets?.map((planet) => {
            const isCompared = comparedNames.includes(planet.name);
            return (
              <div
                key={planet.id}
                onClick={() => onSelectPlanet(planet.name)}
                className="planet-card"
                style={{ cursor: "pointer" }}
              >
                <div className="card-header">
                  <span className="card-title">{planet.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleCompare(planet);
                    }}
                    className={`btn-icon ${isCompared ? "active" : ""}`}
                    style={{ fontSize: "0.65rem", padding: "0.2rem 0.4rem" }}
                  >
                    {isCompared ? "✓ COMPARING" : "+ COMPARE"}
                  </button>
                </div>
                <div className="telemetry-grid-2x2">
                  <div>
                    <span className="telemetry-item-label">RADIUS</span>
                    <span className="telemetry-item-val tabular-nums">
                      {planet.radius_earth ? `${planet.radius_earth.toFixed(2)} R_E` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">PERIOD</span>
                    <span className="telemetry-item-val tabular-nums">
                      {planet.orbital_period_days ? `${planet.orbital_period_days.toFixed(2)} d` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">CLASS</span>
                    <span className="telemetry-item-val">{planet.planet_class || "—"}</span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">TEMP</span>
                    <span className="telemetry-item-val tabular-nums">
                      {planet.equilibrium_temp_k ? `${Math.round(planet.equilibrium_temp_k)} K` : "—"}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Host Stars */}
      {system.stars && system.stars.length > 0 && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <div className="panel-header">
            <span>STELLAR HOSTS ({system.stars.length})</span>
          </div>
          <div className="grid-2col">
            {system.stars.map((star) => (
              <div key={star.id} className="metric-tile">
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <span style={{ fontWeight: 600, color: "var(--text-main)" }}>{star.name}</span>
                  <span className="badge">{star.spectral_type || "N/A"}</span>
                </div>
                <div className="grid-4col">
                  <div>
                    <span className="telemetry-item-label">TEMPERATURE</span>
                    <span className="telemetry-item-val tabular-nums">
                      {star.effective_temp_k ? `${Math.round(star.effective_temp_k)} K` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">MASS</span>
                    <span className="telemetry-item-val tabular-nums">
                      {star.mass_solar ? `${star.mass_solar.toFixed(2)} M_Sun` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">RADIUS</span>
                    <span className="telemetry-item-val tabular-nums">
                      {star.radius_solar ? `${star.radius_solar.toFixed(2)} R_Sun` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">METALLICITY</span>
                    <span className="telemetry-item-val tabular-nums">
                      {star.metallicity_dex !== null && star.metallicity_dex !== undefined
                        ? `${star.metallicity_dex.toFixed(2)} dex`
                        : "—"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
