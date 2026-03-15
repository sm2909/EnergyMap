import React from 'react';
import './Spinner.css';

export default function Spinner({ label = 'Loading data…' }) {
  return (
    <div className="spinner">
      <div className="spinner__ring" aria-hidden="true" />
      <div className="spinner__label">{label}</div>
    </div>
  );
}
