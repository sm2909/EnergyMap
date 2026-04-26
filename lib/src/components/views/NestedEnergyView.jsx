import React from 'react';
import NestedTreemap from '../hierarchy/NestedTreemap';
import './NestedEnergyView.css';

export default function NestedEnergyView({ data }) {
  return (
    <div className="nested-energy-view">
      <div className="tree-container">
        <NestedTreemap data={data?.modules || []} />
      </div>
    </div>
  );
}
