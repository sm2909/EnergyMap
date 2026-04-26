import React, { useMemo } from 'react';
import CategoryBadge from '../shared/CategoryBadge';
import EnergyValue from '../shared/EnergyValue';
import MiniBarChart from './MiniBarChart';
import { getCategoryColor } from '../../utils/energyColors';
import './CategorySection.css';

export default function CategorySection({ title, category, items, searchTerm, sortBy }) {
  const filteredAndSortedItems = useMemo(() => {
    let result = [...items];
    
    // Filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(item => item.module.toLowerCase().includes(term));
    }
    
    // Sort
    result.sort((a, b) => {
      if (sortBy === 'energy') {
        return (b.energy || 0) - (a.energy || 0);
      } else {
        return a.module.localeCompare(b.module);
      }
    });
    
    return result;
  }, [items, searchTerm, sortBy]);

  if (filteredAndSortedItems.length === 0 && searchTerm) {
    return null; // Don't show empty sections when searching
  }

  const totalEnergy = items.reduce((sum, item) => sum + (item.energy || 0), 0);
  const color = getCategoryColor(category);

  return (
    <div className="category-section">
      <div className="category-header" style={{ borderBottomColor: color }}>
        <div className="category-title-area">
          <h2 className="category-title">{title}</h2>
          <CategoryBadge category={category} />
        </div>
        
        <div className="category-stats">
          <div className="stat-item">
            <span className="stat-label">Count:</span>
            <span className="stat-value">{filteredAndSortedItems.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Energy:</span>
            <EnergyValue value={totalEnergy} />
          </div>
        </div>
      </div>
      
      {filteredAndSortedItems.length > 0 ? (
        <div className="category-content">
          <MiniBarChart data={filteredAndSortedItems} category={category} />
        </div>
      ) : (
        <div className="empty-category">No modules found.</div>
      )}
    </div>
  );
}
