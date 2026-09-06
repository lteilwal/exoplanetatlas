import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number | null | undefined;
  unit?: string;
  subValue?: string;
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subValue,
  highlight = false,
}) => {
  const displayValue = value !== null && value !== undefined && value !== "" ? value : "—";

  return (
    <div className={`metric-tile ${highlight ? "highlight" : ""}`}>
      <div className="metric-tile-label">{label}</div>
      <div className="metric-tile-body">
        <span className="metric-tile-val tabular-nums">{displayValue}</span>
        {unit && displayValue !== "—" && (
          <span className="metric-tile-unit">{unit}</span>
        )}
      </div>
      {subValue && <div className="metric-tile-sub">{subValue}</div>}
    </div>
  );
};
