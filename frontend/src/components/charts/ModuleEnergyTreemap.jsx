import React from 'react';
import { Treemap, Tooltip, ResponsiveContainer } from 'recharts';
import './ChartCard.css';
import { getEnergyColor } from '../../utils/energyColors';

function renderCustomContent({ x, y, width, height, name, value, index, root }) {
  if (width < 60 || height < 40) return null;
  const max = root?.value ?? value;
  const color = getEnergyColor(value, max);
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill={color} rx={12} ry={12} />
      <text x={x + 12} y={y + 20} fill="#fff" fontSize={12} fontWeight={700}>
        {name}
      </text>
      <text x={x + 12} y={y + 38} fill="#f3f4f6" fontSize={11}>
        {value.toFixed(1)}
      </text>
    </g>
  );
}

export default function ModuleEnergyTreemap({ data }) {
  const maxMean = Math.max(...data.map((item) => item.mean || 0));
  const chartData = data.map((item) => ({
    name: item.module,
    size: item.mean,
  }));

  return (
    <div className="chartCard">
      <header className="chartCard__header">
        <div>
          <h3>Module Energy Comparison</h3>
          <p className="chartCard__subtitle">Relative mean energy usage between modules.</p>
        </div>
      </header>
      <div className="chartCard__content">
        <ResponsiveContainer width="100%" height={280}>
          <Treemap
            data={chartData}
            dataKey="size"
            stroke="#fff"
            fill="#8884d8"
            content={renderCustomContent}
            aspectRatio={4 / 3}
          />
        </ResponsiveContainer>
      </div>
    </div>
  );
}
