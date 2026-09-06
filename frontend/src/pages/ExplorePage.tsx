import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { PlanetSummary, StatsResponse } from "../types";

interface ExplorePageProps {
  onSelectPlanet: (planetName: string) => void;
}

export const ExplorePage: React.FC<ExplorePageProps> = ({ onSelectPlanet }) => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [randomPlanet, setRandomPlanet] = useState<PlanetSummary | null>(null);
  const [habitablePicks, setHabitablePicks] = useState<PlanetSummary[]>([]);
  const [extremePicks, setExtremePicks] = useState<PlanetSummary[]>([]);
  const [nearbyPicks, setNearbyPicks] = useState<PlanetSummary[]>([]);
  const [rolling, setRolling] = useState(false);

  useEffect(() => {
    const loadExploreData = async () => {
      try {
        const statsRes = await api.getStats();
        setStats(statsRes);

        // Habitable Zone Earth Analogs
        const hzRes = await api.getPlanets({
          habitability_zone_est: "Conservative Habitable Zone",
          planet_class: "Terrestrial",
          page_size: 4,
        });
        setHabitablePicks(hzRes.items);

        // Extreme Worlds (Hot Gas Giants)
        const extRes = await api.getPlanets({
          planet_class: "Gas Giant",
          max_period_days: 5,
          page_size: 4,
        });
        setExtremePicks(extRes.items);

        // Nearest Worlds
        const nearRes = await api.getPlanets({
          sort_by: "distance",
          order: "asc",
          page_size: 4,
        });
        setNearbyPicks(nearRes.items);

        // Initial random planet
        rollRandom();
      } catch (err) {
        console.error("Failed to load explore data", err);
      }
    };
    loadExploreData();
  }, []);

  const rollRandom = async () => {
    setRolling(true);
    try {
      const randomPage = Math.floor(Math.random() * 150) + 1;
      const res = await api.getPlanets({ page: randomPage, page_size: 25 });
      if (res.items.length > 0) {
        const randomIndex = Math.floor(Math.random() * res.items.length);
        setRandomPlanet(res.items[randomIndex]);
      }
    } catch (err) {
      console.error("Failed to roll random planet", err);
    } finally {
      setRolling(false);
    }
  };

  return (
    <div className="content-wrapper font-mono">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">EXPLORATION & DISCOVERY TERMINAL</h1>
          <p className="page-subtitle">
            SERENDIPITOUS DISCOVERY // ASTRONOMICAL HIGHLIGHTS & ARCHIVAL ROULETTE
          </p>
        </div>
      </div>

      {/* Catalog Telemetry Overview */}
      {stats && (
        <div className="grid-4col" style={{ marginBottom: "2rem" }}>
          <MetricCard
            label="CONFIRMED PLANETS"
            value={stats.total_planets.toLocaleString()}
            subValue="NASA Exoplanet Archive"
            highlight
          />
          <MetricCard
            label="PLANETARY SYSTEMS"
            value={stats.total_systems.toLocaleString()}
            subValue={`${stats.multi_planet_systems} multi-planet systems`}
          />
          <MetricCard
            label="STELLAR HOSTS"
            value={stats.total_stars.toLocaleString()}
            subValue="Single & Binary Hosts"
          />
          <MetricCard
            label="TERRESTRIAL WORLDS"
            value={(stats.planet_class_distribution["Terrestrial"] || 0).toLocaleString()}
            subValue="Radius < 1.25 Earth radii"
          />
        </div>
      )}

      {/* Random Planetary Roulette */}
      <div className="diagram-box" style={{ marginBottom: "2.5rem", padding: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)", paddingBottom: "1rem", marginBottom: "1rem" }}>
          <div>
            <div style={{ fontSize: "0.85rem", fontWeight: "bold", color: "var(--text-main)" }}>
              RANDOM EXOPLANET ROULETTE
            </div>
            <p style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
              PULL AN UNEXPECTED WORLD FROM DEEP ARCHIVES
            </p>
          </div>

          <button onClick={rollRandom} disabled={rolling} className="btn-primary">
            {rolling ? "SCANNING ARCHIVES..." : "⚄ ROLL RANDOM PLANET"}
          </button>
        </div>

        {randomPlanet && (
          <div className="grid-3col" style={{ alignItems: "center" }}>
            <div className="panel" style={{ margin: 0 }}>
              <span style={{ fontSize: "0.65rem", color: "var(--text-muted)", display: "block", marginBottom: "0.25rem" }}>
                TARGET DESIGNATION
              </span>
              <h3
                onClick={() => onSelectPlanet(randomPlanet.name)}
                style={{ fontSize: "1.1rem", fontWeight: "bold", color: "var(--text-main)", cursor: "pointer", textDecoration: "underline" }}
              >
                {randomPlanet.name} ↗
              </h3>
              <p style={{ fontSize: "0.75rem", color: "var(--text-silver)", marginTop: "0.35rem" }}>
                {randomPlanet.planet_class || "Unclassified Planet"}
              </p>
              <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: "1px solid var(--border)", display: "flex", justifyContent: "space-between", fontSize: "0.7rem" }}>
                <span style={{ color: "var(--text-muted)" }}>REGIME:</span>
                <span style={{ color: "var(--text-main)", fontWeight: 600 }}>
                  {randomPlanet.habitability_zone_est || "Undetermined"}
                </span>
              </div>
            </div>

            <div style={{ gridColumn: "span 2" }} className="grid-4col">
              <MetricCard
                label="Radius"
                value={randomPlanet.radius_earth ? `${randomPlanet.radius_earth.toFixed(2)}` : null}
                unit="R_E"
              />
              <MetricCard
                label="Mass"
                value={randomPlanet.mass_earth ? `${randomPlanet.mass_earth.toFixed(2)}` : null}
                unit="M_E"
              />
              <MetricCard
                label="Orbital Period"
                value={randomPlanet.orbital_period_days ? `${randomPlanet.orbital_period_days.toFixed(2)}` : null}
                unit="days"
              />
              <MetricCard
                label="Equilibrium Temp"
                value={randomPlanet.equilibrium_temp_k ? `${Math.round(randomPlanet.equilibrium_temp_k)}` : null}
                unit="K"
              />
            </div>
          </div>
        )}
      </div>

      {/* Curated Highlights */}
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* 1. Habitable Zone Earth Analogs */}
        <div>
          <div className="panel-header">
            <span>EARTH-SIZED WORLDS IN CONSERVATIVE HABITABLE ZONES</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>LIQUID WATER REGIMES</span>
          </div>
          <div className="card-grid">
            {habitablePicks.map((planet) => (
              <div
                key={planet.id}
                onClick={() => onSelectPlanet(planet.name)}
                className="planet-card"
                style={{ cursor: "pointer" }}
              >
                <h4 style={{ fontSize: "0.85rem", fontWeight: "bold", color: "var(--text-main)", marginBottom: "0.5rem" }}>
                  {planet.name}
                </h4>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Radius:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.radius_earth?.toFixed(2)} R_E</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Period:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.orbital_period_days?.toFixed(1)} d</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Method:</span>
                    <span style={{ color: "var(--text-silver)" }}>{planet.discovery?.discovery_method}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Extreme Worlds */}
        <div>
          <div className="panel-header">
            <span>EXTREME WORLDS: ULTRA-SHORT PERIOD GAS GIANTS</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>ORBITS &lt; 5 DAYS</span>
          </div>
          <div className="card-grid">
            {extremePicks.map((planet) => (
              <div
                key={planet.id}
                onClick={() => onSelectPlanet(planet.name)}
                className="planet-card"
                style={{ cursor: "pointer" }}
              >
                <h4 style={{ fontSize: "0.85rem", fontWeight: "bold", color: "var(--text-main)", marginBottom: "0.5rem" }}>
                  {planet.name}
                </h4>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Period:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.orbital_period_days?.toFixed(2)} d</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Temp:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.equilibrium_temp_k ? `${Math.round(planet.equilibrium_temp_k)} K` : "—"}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Radius:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.radius_earth?.toFixed(1)} R_E</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Solar Neighborhood */}
        <div>
          <div className="panel-header">
            <span>SOLAR NEIGHBORHOOD EXOPLANETS</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>CLOSEST TO EARTH</span>
          </div>
          <div className="card-grid">
            {nearbyPicks.map((planet) => (
              <div
                key={planet.id}
                onClick={() => onSelectPlanet(planet.name)}
                className="planet-card"
                style={{ cursor: "pointer" }}
              >
                <h4 style={{ fontSize: "0.85rem", fontWeight: "bold", color: "var(--text-main)", marginBottom: "0.5rem" }}>
                  {planet.name}
                </h4>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Class:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.planet_class || "Planet"}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Period:</span>
                    <span style={{ color: "var(--text-main)" }}>{planet.orbital_period_days?.toFixed(1)} d</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Year:</span>
                    <span style={{ color: "var(--text-silver)" }}>{planet.discovery?.discovery_year}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
