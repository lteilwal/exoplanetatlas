import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { CatalogFilterBar } from "../components/CatalogFilterBar";
import { Pagination } from "../components/Pagination";
import { PlanetCard } from "../components/PlanetCard";
import { PlanetTable } from "../components/PlanetTable";
import { CatalogFilterParams, PlanetSummary } from "../types";

interface CatalogPageProps {
  onSelectPlanet: (name: string) => void;
  comparedPlanets: PlanetSummary[];
  onToggleCompare: (planet: PlanetSummary) => void;
}

export const CatalogPage: React.FC<CatalogPageProps> = ({
  onSelectPlanet,
  comparedPlanets,
  onToggleCompare,
}) => {
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [planets, setPlanets] = useState<PlanetSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const [filters, setFilters] = useState<CatalogFilterParams>({
    page: 1,
    page_size: 24,
    sort_by: "name",
    order: "asc",
  });

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getPlanets(filters);
      setPlanets(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err: any) {
      setError(err.message || "Failed to load exoplanets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  const handleFilterChange = (newFilters: CatalogFilterParams) => {
    setFilters(newFilters);
  };

  const handleReset = () => {
    setFilters({
      page: 1,
      page_size: 24,
      sort_by: "name",
      order: "asc",
    });
  };

  const handleSortChange = (sortBy: string) => {
    if (filters.sort_by === sortBy) {
      setFilters({
        ...filters,
        order: filters.order === "asc" ? "desc" : "asc",
      });
    } else {
      setFilters({
        ...filters,
        sort_by: sortBy,
        order: "asc",
      });
    }
  };

  const comparedNames = comparedPlanets.map((p) => p.name);

  return (
    <div className="content-wrapper">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">EXOPLANET CATALOG</h1>
          <p className="page-subtitle">
            SEARCHABLE ARCHIVE OF CONFIRMED EXTRA-SOLAR PLANETS
          </p>
        </div>

        {/* View Toggle */}
        <div style={{ display: "flex", gap: "0.25rem", fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
          <button
            onClick={() => setViewMode("grid")}
            className={`btn-icon ${viewMode === "grid" ? "active" : ""}`}
            style={{ padding: "0.35rem 0.6rem" }}
          >
            <span>▦ GRID</span>
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`btn-icon ${viewMode === "table" ? "active" : ""}`}
            style={{ padding: "0.35rem 0.6rem" }}
          >
            <span>▤ TABLE</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <CatalogFilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleReset}
      />

      {/* Content Area */}
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
            fontFamily: "var(--font-mono)",
            color: "var(--text-muted)",
          }}
        >
          <div style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>⚙</div>
          <span>QUERYING RELATIONAL DATABASE...</span>
        </div>
      ) : error ? (
        <div
          style={{
            padding: "2rem",
            border: "1px solid var(--border)",
            backgroundColor: "var(--bg-card)",
            textAlign: "center",
            fontFamily: "var(--font-mono)",
          }}
        >
          <div style={{ color: "var(--text-main)", marginBottom: "0.5rem" }}>ERROR FETCHING CATALOG DATA</div>
          <div style={{ color: "var(--text-muted)", marginBottom: "1rem" }}>{error}</div>
          <button onClick={loadData} className="btn-primary">
            RETRY
          </button>
        </div>
      ) : planets.length === 0 ? (
        <div
          style={{
            padding: "3rem",
            border: "1px solid var(--border)",
            backgroundColor: "var(--bg-card)",
            textAlign: "center",
            fontFamily: "var(--font-mono)",
          }}
        >
          <div style={{ color: "var(--text-main)", marginBottom: "0.5rem" }}>NO EXOPLANETS MATCH YOUR CRITERIA</div>
          <div style={{ color: "var(--text-muted)", marginBottom: "1rem" }}>
            Try adjusting search terms or widening filter parameters.
          </div>
          <button onClick={handleReset} className="btn-primary">
            CLEAR FILTERS
          </button>
        </div>
      ) : viewMode === "grid" ? (
        <div className="card-grid">
          {planets.map((planet) => (
            <PlanetCard
              key={planet.id}
              planet={planet}
              onSelect={onSelectPlanet}
              onToggleCompare={onToggleCompare}
              isCompared={comparedNames.includes(planet.name)}
            />
          ))}
        </div>
      ) : (
        <PlanetTable
          planets={planets}
          onSelect={onSelectPlanet}
          onToggleCompare={onToggleCompare}
          comparedPlanetNames={comparedNames}
          sortBy={filters.sort_by || "name"}
          onSortChange={handleSortChange}
        />
      )}

      {/* Pagination Controls */}
      {!loading && planets.length > 0 && (
        <Pagination
          page={filters.page || 1}
          totalPages={totalPages}
          totalItems={total}
          pageSize={filters.page_size || 24}
          onPageChange={(page) => setFilters({ ...filters, page })}
          onPageSizeChange={(page_size) => setFilters({ ...filters, page_size, page: 1 })}
        />
      )}
    </div>
  );
};
