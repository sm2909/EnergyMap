import React, { useState } from 'react';
import CategorySection from '../flat/CategorySection';
import './FlatEnergyView.css';

export default function FlatEnergyView({ data }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('energy'); // 'energy' or 'alpha'

  if (!data) return null;

  return (
    <div className="flat-energy-view">
      <div className="view-controls">
        <input 
          type="text" 
          placeholder="Search modules..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-select"
        >
          <option value="energy">Sort by Energy</option>
          <option value="alpha">Sort Alphabetically</option>
        </select>
      </div>
      
      <div className="categories-container">
        <CategorySection 
          title="Internal Modules" 
          category="internal" 
          items={data.internal || []} 
          searchTerm={searchTerm}
          sortBy={sortBy}
        />
        
        <CategorySection 
          title="Standard Library" 
          category="stdlib" 
          items={data.stdlib || []} 
          searchTerm={searchTerm}
          sortBy={sortBy}
        />
        
        <CategorySection 
          title="External Dependencies" 
          category="external" 
          items={data.external || []} 
          searchTerm={searchTerm}
          sortBy={sortBy}
        />
      </div>
    </div>
  );
}
