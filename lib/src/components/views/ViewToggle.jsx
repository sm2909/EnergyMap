import React from 'react';
import './ViewToggle.css';

export default function ViewToggle({ activeView, onChange, options }) {
  return (
    <div className="view-toggle">
      {options.map(option => (
        <button
          key={option}
          className={`view-toggle-btn ${activeView === option ? 'active' : ''}`}
          onClick={() => onChange(option)}
        >
          {option.charAt(0).toUpperCase() + option.slice(1)} View
        </button>
      ))}
    </div>
  );
}
