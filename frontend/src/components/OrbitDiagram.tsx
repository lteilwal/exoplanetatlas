import React, { useRef, useState, useEffect } from "react";

interface OrbitDiagramProps {
  semiMajorAxisAu: number | null;
  eccentricity: number | null;
  stellarMassSolar?: number | null;
  planetName: string;
  habitabilityZone?: string | null;
}

export const OrbitDiagram: React.FC<OrbitDiagramProps> = ({
  semiMajorAxisAu,
  eccentricity = 0,
  stellarMassSolar = 1.0,
  planetName,
  habitabilityZone,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const sma = semiMajorAxisAu || 1.0;
  const ecc = eccentricity || 0;
  const mStar = stellarMassSolar || 1.0;

  // Approximate habitable zone boundaries in AU scaled to stellar mass/luminosity
  // L ~ M^3.5 for main sequence
  const lumEst = Math.pow(Math.max(0.05, Math.min(20, mStar)), 3.5);
  const hzInner = Math.sqrt(lumEst / 1.1); // ~0.95 AU for Sun
  const hzOuter = Math.sqrt(lumEst / 0.53); // ~1.37 AU for Sun

  // Base normalization
  const maxRadius = Math.max(sma * 1.4, hzOuter * 1.2, 0.4);
  const width = isExpanded ? 500 : 320;
  const height = isExpanded ? 500 : 320;
  const cx = width / 2;
  const cy = height / 2;
  const baseScale = (Math.min(width, height) / 2 - 35) / maxRadius;
  const scale = baseScale * zoom;

  const planetRadiusPx = sma * scale;
  const hzInnerPx = hzInner * scale;
  const hzOuterPx = hzOuter * scale;

  // Orbit ellipse geometry
  const aPx = planetRadiusPx;
  const bPx = planetRadiusPx * Math.sqrt(Math.max(0.01, 1 - ecc * ecc));
  const focusOffsetPx = aPx * ecc;

  // Wheel zoom handler
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      setZoom((prev) => Math.min(8.0, Math.max(0.2, +(prev * zoomFactor).toFixed(2))));
    };

    el.addEventListener("wheel", handleWheel, { passive: false });
    return () => el.removeEventListener("wheel", handleWheel);
  }, []);

  // Mouse Drag / Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleReset = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(8.0, +(prev * 1.25).toFixed(2)));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(0.2, +(prev * 0.8).toFixed(2)));
  };

  return (
    <div className="diagram-box font-mono" style={{ display: "flex", flexDirection: "column" }}>
      {/* Header with Telemetry & Controls */}
      <div className="diagram-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>ORBITAL GEOMETRY (SCROLL / DRAG SCALABLE)</span>
        <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>
          SMA: {semiMajorAxisAu ? `${semiMajorAxisAu.toFixed(3)} AU` : "N/A"} | ECC: {ecc.toFixed(3)}
        </span>
      </div>

      {/* Control Bar: Zoom +/- / Reset / Expand */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          backgroundColor: "var(--bg-surface)",
          padding: "0.35rem 0.5rem",
          borderBottom: "1px solid var(--border)",
          fontSize: "0.65rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ color: "var(--text-dim)" }}>ZOOM:</span>
          <span style={{ color: "var(--text-main)", fontWeight: 600, minWidth: "35px" }}>
            {zoom.toFixed(2)}x
          </span>
          <input
            type="range"
            min="0.2"
            max="8.0"
            step="0.05"
            value={zoom}
            onChange={(e) => setZoom(parseFloat(e.target.value))}
            style={{
              width: "70px",
              height: "4px",
              cursor: "pointer",
              accentColor: "#ffffff",
              backgroundColor: "var(--border)",
            }}
            title="Scale Orbit"
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <button
            onClick={handleZoomOut}
            className="preset-btn"
            style={{ padding: "0.15rem 0.4rem", fontSize: "0.65rem" }}
            title="Zoom Out"
          >
            -
          </button>
          <button
            onClick={handleZoomIn}
            className="preset-btn"
            style={{ padding: "0.15rem 0.4rem", fontSize: "0.65rem" }}
            title="Zoom In"
          >
            +
          </button>
          <button
            onClick={handleReset}
            className="preset-btn"
            style={{ padding: "0.15rem 0.4rem", fontSize: "0.65rem" }}
            title="Reset Pan & Zoom"
          >
            RESET
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="preset-btn"
            style={{ padding: "0.15rem 0.4rem", fontSize: "0.65rem" }}
            title={isExpanded ? "Standard View" : "Expand Size"}
          >
            {isExpanded ? "COMPACT" : "EXPAND"}
          </button>
        </div>
      </div>

      {/* Interactive Canvas */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "0.5rem 0",
          cursor: isDragging ? "grabbing" : "grab",
          userSelect: "none",
          overflow: "hidden",
          position: "relative",
          backgroundColor: "var(--bg-void)",
          minHeight: isExpanded ? "450px" : "280px",
          transition: "min-height 0.2s ease-in-out",
        }}
      >
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: "100%", height: isExpanded ? "450px" : "280px", overflow: "visible" }}
        >
          {/* Static Axes */}
          <line x1={0} y1={cy} x2={width} y2={cy} stroke="#141414" strokeWidth="1" strokeDasharray="2 2" />
          <line x1={cx} y1={0} x2={cx} y2={height} stroke="#141414" strokeWidth="1" strokeDasharray="2 2" />

          {/* Scaled and Panned Group */}
          <g transform={`translate(${cx + pan.x}, ${cy + pan.y})`}>
            {/* Habitable Zone Annulus */}
            {hzInnerPx > 2 && (
              <circle
                cx={0}
                cy={0}
                r={hzOuterPx}
                fill="#ffffff"
                fillOpacity="0.03"
                stroke="#ffffff"
                strokeOpacity="0.15"
                strokeWidth="1"
                strokeDasharray="3 3"
              />
            )}
            {hzInnerPx > 2 && (
              <circle
                cx={0}
                cy={0}
                r={hzInnerPx}
                fill="var(--bg-card)"
                stroke="#ffffff"
                strokeOpacity="0.15"
                strokeWidth="1"
                strokeDasharray="3 3"
              />
            )}

            {/* Earth 1 AU Reference Orbit */}
            {maxRadius > 1.2 && (
              <circle
                cx={0}
                cy={0}
                r={1.0 * scale}
                fill="none"
                stroke="#333333"
                strokeWidth="0.75"
                strokeDasharray="1 3"
              />
            )}

            {/* Planet Orbit Ellipse */}
            <ellipse
              cx={-focusOffsetPx}
              cy={0}
              rx={aPx}
              ry={bPx}
              fill="none"
              stroke="#ffffff"
              strokeWidth="1"
            />

            {/* Host Star at Focus */}
            <circle cx={0} cy={0} r={Math.max(3, Math.min(8, 5 * Math.sqrt(zoom)))} fill="#ffffff" />
            <text
              x={0}
              y={14 + 2 * zoom}
              textAnchor="middle"
              fill="#8a8a8a"
              fontSize="8"
              fontFamily="monospace"
            >
              HOST STAR
            </text>

            {/* Planet Position at Periastron */}
            <circle
              cx={aPx - focusOffsetPx}
              cy={0}
              r={Math.max(3, Math.min(7, 4 * Math.sqrt(zoom)))}
              fill="#ffffff"
              stroke="#000000"
              strokeWidth="1"
            />
            <text
              x={aPx - focusOffsetPx}
              y={-10}
              textAnchor="middle"
              fill="#ffffff"
              fontSize="8"
              fontFamily="monospace"
              fontWeight="bold"
            >
              {planetName}
            </text>
          </g>
        </svg>

        {/* Floating Hint */}
        <div
          style={{
            position: "absolute",
            bottom: "6px",
            right: "8px",
            fontSize: "0.55rem",
            color: "var(--text-dim)",
            pointerEvents: "none",
          }}
        >
          SCROLL WHEEL TO ZOOM • DRAG TO PAN
        </div>
      </div>

      {/* Legend & Telemetry */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "0.5rem",
          fontSize: "0.65rem",
          color: "var(--text-muted)",
          borderTop: "1px solid var(--border)",
          paddingTop: "0.5rem",
          marginTop: "auto",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <div style={{ width: "8px", height: "8px", backgroundColor: "#ffffff" }} />
          <span>Planet Orbit ({sma.toFixed(2)} AU)</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <div style={{ width: "8px", height: "8px", backgroundColor: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.3)" }} />
          <span>Habitable Zone</span>
        </div>
      </div>

      {habitabilityZone && (
        <div
          style={{
            marginTop: "0.5rem",
            fontSize: "0.65rem",
            border: "1px solid var(--border)",
            backgroundColor: "var(--bg-surface)",
            padding: "0.35rem 0.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ color: "var(--text-muted)" }}>CLASSIFIED REGIME:</span>
          <span style={{ color: "var(--text-main)", fontWeight: 600, textTransform: "uppercase" }}>
            {habitabilityZone}
          </span>
        </div>
      )}
    </div>
  );
};
