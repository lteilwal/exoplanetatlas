import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { Pagination } from "../components/Pagination";
import { SystemSummary } from "../types";

interface SystemsListPageProps {
  onSelectSystem: (name: string) => void;
}

export const SystemsListPage: React.FC<SystemsListPageProps> = ({ onSelectSystem }) => {
  const [systems, setSystems] = useState<SystemSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(24);
  const [search, setSearch] = useState("");
  const [minPlanets, setMinPlanets] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState("name");
  const [order] = useState<"asc" | "desc">("asc");

  const loadSystems = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getSystems({
        page,
        page_size: pageSize,
        search: search || undefined,
        min_planets: minPlanets,
        sort_by: sortBy,
        order,
      });
      setSystems(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err: any) {
      setError(err.message || "Failed to load systems");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSystems();
  }, [page, pageSize, minPlanets, sortBy, order]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadSystems();
  };

  return (
    <div className="content-wrapper font-mono">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">PLANETARY SYSTEMS DIRECTORY</h1>
          <p className="page-subtitle">
            MULTIPLICITY ARCHITECTURES & HOST STELLAR CONFIGURATIONS
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-container">
        <div className="filter-main">
          <form onSubmit={handleSearchSubmit} className="search-form">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="SEARCH SYSTEM NAME (E.G. 'TRAPPIST-1', 'KEPLER-11')..."
              className="search-input"
            />
            <button type="submit" className="btn-primary">
              SEARCH
            </button>
          </form>

          {/* Quick filter pills */}
          <div className="preset-group">
            <span style={{ color: "var(--text-dim)", marginRight: "0.25rem" }}>MIN PLANETS:</span>
            {[undefined, 2, 3, 5].map((val) => (
              <button
                key={val ?? "all"}
                onClick={() => {
                  setMinPlanets(val);
                  setPage(1);
                }}
                className={`preset-btn ${minPlanets === val ? "active" : ""}`}
              >
                {val ? `≥ ${val}` : "ALL"}
              </button>
            ))}

            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setPage(1);
              }}
              className="form-select"
              style={{ width: "auto", padding: "0.3rem 0.5rem" }}
            >
              <option value="name">Name</option>
              <option value="planets">Planet Count</option>
              <option value="distance">Distance</option>
              <option value="stars">Star Count</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid of Systems */}
      {loading ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "5rem 0",
            border: "1px solid var(--border)",
            backgroundColor: "var(--bg-card)",
            color: "var(--text-muted)",
          }}
        >
          <div style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>⚙</div>
          <span>RETRIEVING SYSTEM ARCHITECTURES...</span>
        </div>
      ) : error ? (
        <div style={{ padding: "2rem", border: "1px solid var(--border)", backgroundColor: "var(--bg-card)", textAlign: "center" }}>
          <div style={{ color: "var(--text-main)", marginBottom: "0.5rem" }}>ERROR FETCHING SYSTEMS</div>
          <div style={{ color: "var(--text-muted)" }}>{error}</div>
        </div>
      ) : (
        <div className="card-grid">
          {systems.map((sys) => (
            <div
              key={sys.id}
              onClick={() => onSelectSystem(sys.name)}
              className="planet-card"
              style={{ cursor: "pointer" }}
            >
              <div>
                <div className="card-header">
                  <h3 className="card-title">
                    {sys.name} ↗
                  </h3>
                  <span className="badge">
                    {sys.planet_count || 1} PLANETS
                  </span>
                </div>
                <div className="telemetry-grid-2x2">
                  <div>
                    <span className="telemetry-item-label">DISTANCE</span>
                    <span className="telemetry-item-val tabular-nums">
                      {sys.distance_pc ? `${sys.distance_pc.toFixed(1)} pc` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">STARS</span>
                    <span className="telemetry-item-val tabular-nums">{sys.star_count || 1}</span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">V-MAG</span>
                    <span className="telemetry-item-val tabular-nums">
                      {sys.v_mag ? `${sys.v_mag.toFixed(2)}` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="telemetry-item-label">CIRCUMBINARY</span>
                    <span className="telemetry-item-val">{sys.is_circumbinary ? "YES" : "NO"}</span>
                  </div>
                </div>
              </div>

              <div className="card-footer">
                <span>COORDINATES:</span>
                <span style={{ color: "var(--text-silver)" }}>
                  {sys.ra ? `${sys.ra.toFixed(2)}°, ${sys.dec?.toFixed(2)}°` : "—"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && systems.length > 0 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          totalItems={total}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={(size) => {
            setPageSize(size);
            setPage(1);
          }}
        />
      )}
    </div>
  );
};
