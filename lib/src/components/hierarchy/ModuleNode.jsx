import React, { useState, useMemo } from 'react';
import CategoryBadge from '../shared/CategoryBadge';
import EnergyValue from '../shared/EnergyValue';
import DependencyList from './DependencyList';
import { getCategoryColor } from '../../utils/energyColors';
import './ModuleNode.css';

export default function ModuleNode({ data, searchTerm }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const hasDependencies = data.dependencies && data.dependencies.length > 0;
  
  // Calculate self energy (total energy minus dependencies energy)
  const depsEnergy = hasDependencies 
    ? data.dependencies.reduce((sum, dep) => sum + (dep.energy || 0), 0)
    : 0;
  const selfEnergy = Math.max(0, (data.energy || 0) - depsEnergy);
  
  const toggleExpand = () => setIsExpanded(!isExpanded);
  
  const color = getCategoryColor(data.category);
  
  const isMatch = searchTerm && data.module.toLowerCase().includes(searchTerm.toLowerCase());
  
  return (
    <div className={`module-node-container ${isMatch ? 'highlight' : ''}`}>
      <div 
        className={`module-node-header ${hasDependencies ? 'clickable' : ''}`}
        onClick={hasDependencies ? toggleExpand : undefined}
        style={{ borderLeftColor: color }}
      >
        <div className="module-node-title">
          {hasDependencies && (
            <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
              ▶
            </span>
          )}
          {!hasDependencies && <span className="expand-spacer"></span>}
          <span className="module-name">{data.module}</span>
          <CategoryBadge category={data.category} />
        </div>
        
        <div className="module-node-stats">
          <EnergyValue value={data.energy} />
        </div>
      </div>
      
      {isExpanded && hasDependencies && (
        <div className="module-node-children">
          <DependencyList 
            dependencies={data.dependencies} 
            selfEnergy={selfEnergy} 
            searchTerm={searchTerm} 
          />
        </div>
      )}
    </div>
  );
}
