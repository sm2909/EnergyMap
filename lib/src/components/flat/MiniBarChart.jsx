import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { getCategoryColor } from '../../utils/energyColors';
import { formatEnergy } from '../../utils/formatters';
import './MiniBarChart.css';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="mini-chart-tooltip">
        <p className="tooltip-module">{data.module}</p>
        <p className="tooltip-energy">{formatEnergy(data.energy)} mJ</p>
      </div>
    );
  }
  return null;
};

export default function MiniBarChart({ data, category }) {
  const color = getCategoryColor(category);
  
  // Increased base height calculation to accommodate more space per bar, no maximum limit
  const chartHeight = Math.max(120, data.length * 35);

  return (
    <div className="mini-bar-chart-container" style={{ height: chartHeight }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis 
            dataKey="module" 
            type="category" 
            axisLine={false} 
            tickLine={false}
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            width={280}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.067)' }} />
          <Bar dataKey="energy" radius={[0, 4, 4, 0]} barSize={24}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
