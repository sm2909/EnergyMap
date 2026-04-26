import React from 'react';
import CategoryBadge from '../shared/CategoryBadge';
import EnergyValue from '../shared/EnergyValue';
import { getCategoryColor } from '../../utils/energyColors';
import './DependencyList.css';

export default function DependencyList({ dependencies, selfEnergy, searchTerm }) {
  // Sort dependencies by energy, descending
  const sortedDeps = [...dependencies].sort((a, b) => (b.energy || 0) - (a.energy || 0));

  return (
    <div className="dependency-list">
      {selfEnergy > 0 && (
        <div className="dependency-item self">
          <div className="dependency-info">
            <div className="dependency-bullet" style={{ backgroundColor: getCategoryColor('self') }}></div>
            <span className="dependency-name">(self)</span>
            <CategoryBadge category="self" />
          </div>
          <EnergyValue value={selfEnergy} />
        </div>
      )}
      
      {sortedDeps.map((dep, index) => {
        const isMatch = searchTerm && dep.module.toLowerCase().includes(searchTerm.toLowerCase());
        
        return (
          <div key={`${dep.module}-${index}`} className={`dependency-item ${isMatch ? 'highlight' : ''}`}>
            <div className="dependency-info">
              <div 
                className="dependency-bullet" 
                style={{ backgroundColor: getCategoryColor(dep.category) }}
              ></div>
              <span className="dependency-name">{dep.module}</span>
              <CategoryBadge category={dep.category} />
            </div>
            <EnergyValue value={dep.energy} />
          </div>
        );
      })}
    </div>
  );
}
