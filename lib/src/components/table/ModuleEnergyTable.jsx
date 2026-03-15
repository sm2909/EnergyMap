import React, { useMemo, useState } from 'react';
import './ModuleEnergyTable.css';

const columns = [
  { key: 'module', label: 'Module Name' },
  { key: 'mean', label: 'Mean Energy' },
  { key: 'median', label: 'Median Energy' },
  { key: 'variance', label: 'Variance' },
  { key: 'best_case', label: 'Best Case' },
  { key: 'worst_case', label: 'Worst Case' },
];

const formatNumber = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
};

export default function ModuleEnergyTable({ data }) {
  const [sort, setSort] = useState({ key: 'mean', direction: 'desc' });

  const sortedData = useMemo(() => {
    if (!data) return [];
    const sorted = [...data];

    sorted.sort((a, b) => {
      const aValue = a[sort.key];
      const bValue = b[sort.key];

      if (aValue == null) return 1;
      if (bValue == null) return -1;

      if (typeof aValue === 'string') {
        return sort.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sort.direction === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return sorted;
  }, [data, sort]);

  const toggleSort = (key) => {
    setSort((prior) => {
      if (prior.key === key) {
        return { key, direction: prior.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key, direction: 'desc' };
    });
  };

  const renderSortIndicator = (key) => {
    if (sort.key !== key) return '↕';
    return sort.direction === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="tableContainer">
      <div className="tableHeader">
        <h2>Module Energy Statistics</h2>
        <p className="tableSubheading">Sortable columns, clean numeric formatting, and hover-enabled row highlights.</p>
      </div>
      <div className="tableWrapper">
        <table className="dataTable">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} onClick={() => toggleSort(col.key)}>
                  <span className="tableHeaderCell">
                    {col.label}
                    <span className="tableHeaderSort">{renderSortIndicator(col.key)}</span>
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="emptyRow">
                  No module energy data available.
                </td>
              </tr>
            ) : (
              sortedData.map((row) => (
                <tr key={row.module}>
                  <td>{row.module}</td>
                  <td>{formatNumber(row.mean)}</td>
                  <td>{formatNumber(row.median)}</td>
                  <td>{formatNumber(row.variance)}</td>
                  <td>{formatNumber(row.best_case)}</td>
                  <td>{formatNumber(row.worst_case)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
