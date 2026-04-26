import React, { useState } from 'react';
import ModuleNode from './ModuleNode';
import './HierarchyTreeChart.css';

export default function HierarchyTreeChart({ data, searchTerm }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No hierarchical data available.</div>;
  }

  // Filter top-level modules based on search term
  const filteredData = data.filter(mod => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    // Check if module itself matches
    if (mod.module.toLowerCase().includes(term)) return true;
    // Check if any dependency matches
    if (mod.dependencies && mod.dependencies.some(dep => dep.module.toLowerCase().includes(term))) {
      return true;
    }
    return false;
  });

  return (
    <div className="hierarchy-tree">
      {filteredData.map(module => (
        <ModuleNode 
          key={module.module} 
          data={module} 
          searchTerm={searchTerm} 
        />
      ))}
    </div>
  );
}
