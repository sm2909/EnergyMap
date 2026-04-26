import React from 'react';
import { getCategoryColor } from '../../utils/energyColors';
import './CategoryBadge.css';

export default function CategoryBadge({ category }) {
  if (!category) return null;
  
  const color = getCategoryColor(category);
  const label = category.charAt(0).toUpperCase() + category.slice(1);
  
  return (
    <span 
      className="category-badge" 
      style={{ backgroundColor: `${color}15`, color: color, borderColor: `${color}30` }}
    >
      {label}
    </span>
  );
}
