import React from "react";

interface PaginationProps {
  page: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newPageSize: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  page,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
}) => {
  const startItem = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, totalItems);

  return (
    <div className="pagination-bar">
      <div>
        <span>SHOWING </span>
        <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{startItem}–{endItem}</span>
        <span> OF </span>
        <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{totalItems.toLocaleString()}</span>
        <span> RECORDS</span>
      </div>

      <div className="pagination-controls">
        {onPageSizeChange && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", marginRight: "1rem" }}>
            <span>PER PAGE:</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="form-select"
              style={{ width: "auto", padding: "0.2rem 0.4rem" }}
            >
              <option value={10}>10</option>
              <option value={24}>24</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        )}

        {/* Page Nav */}
        <button
          onClick={() => onPageChange(1)}
          disabled={page <= 1}
          className="page-btn"
          title="First Page"
        >
          «
        </button>
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="page-btn"
          title="Previous Page"
        >
          ‹
        </button>

        <span className="page-indicator">
          PAGE {page} / {Math.max(1, totalPages)}
        </span>

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="page-btn"
          title="Next Page"
        >
          ›
        </button>
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={page >= totalPages}
          className="page-btn"
          title="Last Page"
        >
          »
        </button>
      </div>
    </div>
  );
};
