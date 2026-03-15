import React from 'react';
import './StatCard.css';

export default function StatCard({ title, value, description, icon, accentColor = 'var(--primary)' }) {
  return (
    <div className="statCard" style={{ '--accent': accentColor }}>
      <div className="statCard__icon" style={{ backgroundColor: `${accentColor}22`, color: accentColor }}>
        {icon}
      </div>
      <div className="statCard__body">
        <div className="statCard__title">{title}</div>
        <div className="statCard__value">{value}</div>
        {description ? <div className="statCard__desc">{description}</div> : null}
      </div>
    </div>
  );
}
