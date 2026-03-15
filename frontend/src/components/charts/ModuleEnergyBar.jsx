import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './ChartCard.css';
import { energyPalette, getEnergyColor } from '../../utils/energyColors';

export default function ModuleEnergyBar({ data }) {
  const maxMean = Math.max(...data.map((item) => item.mean || 0));
  const chartData = data.map((item) => ({
    module: item.module,
    mean: item.mean,
    median: item.median,
    color: getEnergyColor(item.mean, maxMean),
  }));

  return (
    <div className="chartCard">
      <header className="chartCard__header">
        <div>
          <h3>Mean Energy Consumption per Module</h3>
          <p className="chartCard__subtitle">Mean vs median energy consumption for each module.</p>
        </div>
      </header>
      <div className="chartCard__content">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 10, right: 18, left: 0, bottom: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(107, 114, 128, 0.2)" />
            <XAxis dataKey="module" tick={{ fontSize: 12 }} interval={0} angle={-42} textAnchor="end" height={65} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => `${value.toFixed(2)} J`} />
            <Legend verticalAlign="top" height={32} />
            <Bar dataKey="mean" fill={energyPalette.secondary} radius={[8, 8, 0, 0]} />
            <Bar dataKey="median" fill={energyPalette.primary} radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
