import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './ChartCard.css';

import { energyPalette, getEnergyColor } from '../../utils/energyColors';

export default function ModuleEnergyPie({ data }) {
  const maxMean = Math.max(...data.map((item) => item.mean || 0));
  const chartData = data.map((item) => ({
    name: item.module,
    value: item.mean,
    color: getEnergyColor(item.mean, maxMean),
  }));

  return (
    <div className="chartCard">
      <header className="chartCard__header">
        <div>
          <h3>Energy Distribution Across Modules</h3>
          <p className="chartCard__subtitle">Share of mean consumption across modules.</p>
        </div>
      </header>
      <div className="chartCard__content">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              stroke="transparent"
            >
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value.toFixed(2)} J`} />
            <Legend layout="horizontal" verticalAlign="bottom" height={40} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
