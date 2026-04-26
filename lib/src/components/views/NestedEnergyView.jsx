import React, { useState } from 'react';
import HierarchyTreeChart from '../hierarchy/HierarchyTreeChart';
import './NestedEnergyView.css';

export default function NestedEnergyView({ data }) {
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <div className="nested-energy-view">
      <div className="view-controls">
        <input 
          type="text" 
          placeholder="Search modules..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="tree-container">
        <HierarchyTreeChart data={data?.modules || []} searchTerm={searchTerm} />
      </div>
    </div>
  );
}
