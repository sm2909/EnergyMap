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
        <p className="tooltip-energy">{formatEnergy(data.energy)} J</p>
      </div>
    );
  }
  return null;
};

export default function MiniBarChart({ data, category }) {
  const color = getCategoryColor(category);
  
  // Calculate a reasonable height based on number of items, max 500px, min 100px
  const chartHeight = Math.max(100, Math.min(500, data.length * 40));

  return (
    <div className="mini-bar-chart-container" style={{ height: chartHeight }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis 
            dataKey="module" 
            type="category" 
            axisLine={false} 
            tickLine={false}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            width={150}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.05)' }} />
          <Bar dataKey="energy" radius={[0, 4, 4, 0]} barSize={20}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
