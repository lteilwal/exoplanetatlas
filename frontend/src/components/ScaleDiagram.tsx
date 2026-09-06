import React from "react";

interface ScaleDiagramProps {
  radiusEarth: number | null;
  planetName: string;
  planetClass?: string | null;
}

export const ScaleDiagram: React.FC<ScaleDiagramProps> = ({
  radiusEarth,
  planetName,
  planetClass,
}) => {
  const rPlanet = radiusEarth || 1.0;
  const rEarth = 1.0;
  const rJupiter = 11.2;

  // Visual scaling relative to Jupiter (max radius in plot)
  const maxR = Math.max(rPlanet, rJupiter, 4.0);
  const pxScale = 50 / maxR;

  const pxPlanet = Math.max(3, rPlanet * pxScale);
  const pxEarth = Math.max(3, rEarth * pxScale);
  const pxJupiter = Math.max(6, rJupiter * pxScale);

  return (
    <div className="diagram-box">
      <div className="diagram-header">
        <span>PLANETARY RADIUS SCALE</span>
        <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>
          {radiusEarth ? `${radiusEarth.toFixed(2)} R_Earth` : "N/A"}
        </span>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "space-around",
          padding: "1.5rem 1rem",
          borderBottom: "1px solid var(--border)",
          minHeight: "140px",
        }}
      >
        {/* Earth Reference */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div
            style={{
              width: `${pxEarth * 2}px`,
              height: `${pxEarth * 2}px`,
              borderRadius: "50%",
              border: "1px solid var(--text-muted)",
              backgroundColor: "rgba(255,255,255,0.2)",
              marginBottom: "0.5rem",
            }}
          />
          <span style={{ fontSize: "0.65rem", color: "var(--text-silver)" }}>EARTH</span>
          <span style={{ fontSize: "0.6rem", color: "var(--text-dim)" }}>1.00 R_E</span>
        </div>

        {/* Target Exoplanet */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div
            style={{
              width: `${pxPlanet * 2}px`,
              height: `${pxPlanet * 2}px`,
              borderRadius: "50%",
              border: "2px solid #ffffff",
              backgroundColor: "#ffffff",
              marginBottom: "0.5rem",
            }}
          />
          <span
            style={{
              fontSize: "0.65rem",
              color: "var(--text-main)",
              fontWeight: "bold",
              maxWidth: "100px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              textAlign: "center",
            }}
          >
            {planetName}
          </span>
          <span style={{ fontSize: "0.6rem", color: "var(--text-silver)", fontWeight: 600 }}>
            {radiusEarth ? `${radiusEarth.toFixed(2)} R_E` : "Estimated"}
          </span>
        </div>

        {/* Jupiter Reference */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div
            style={{
              width: `${pxJupiter * 2}px`,
              height: `${pxJupiter * 2}px`,
              borderRadius: "50%",
              border: "1px solid var(--text-muted)",
              backgroundColor: "var(--bg-elevated)",
              marginBottom: "0.5rem",
            }}
          />
          <span style={{ fontSize: "0.65rem", color: "var(--text-silver)" }}>JUPITER</span>
          <span style={{ fontSize: "0.6rem", color: "var(--text-dim)" }}>11.20 R_E</span>
        </div>
      </div>

      <div
        style={{
          marginTop: "0.75rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.65rem",
          color: "var(--text-muted)",
        }}
      >
        <span>MORPHOLOGY:</span>
        <span style={{ color: "var(--text-main)", fontWeight: 600 }}>
          {planetClass || "Unclassified"}
        </span>
      </div>
    </div>
  );
};
