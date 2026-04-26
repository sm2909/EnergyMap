import React from 'react';
import { formatEnergy } from '../../utils/formatters';
import './EnergyValue.css';

export default function EnergyValue({ value, unit = 'mJ' }) {
  return (
    <span className="energy-value">
      <span className="energy-value-number">{formatEnergy(value)}</span>
      <span className="energy-value-unit">{unit}</span>
    </span>
  );
}
