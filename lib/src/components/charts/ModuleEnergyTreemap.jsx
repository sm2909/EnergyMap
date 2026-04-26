import React from 'react';
import { Treemap, Tooltip, ResponsiveContainer } from 'recharts';
import './ChartCard.css';
import { getEnergyColor } from '../../utils/energyColors';

const numberFormatter = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  const valInJoules = value / 1000;
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(valInJoules);
};

function renderCustomContent(props) {
  const { x, y, width, height, name, value, actualEnergy, root, depth } = props;
  
  if (depth === 0) {
    return <rect x={x} y={y} width={width} height={height} fill="transparent" stroke="none" />;
  }

  const max = root?.value ?? value;
  const color = getEnergyColor(value, max);

  const displayEnergy = actualEnergy !== undefined ? actualEnergy : (value || 0);
  const formattedValue = numberFormatter(displayEnergy) + " mJ";
  
  const nameFontSize = Math.max(7, Math.min(15, (width - 12) / (0.55 * (name || '').length)));
  const valFontSize = Math.max(7, Math.min(12, (width - 12) / (0.55 * formattedValue.length)));
  
  const canFitText = width > 25 && height > 22;

  return (
    <g>
      <rect x={x} y={y} width={width} height={height} fill={color} rx={12} ry={12} />
      {canFitText && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 4} textAnchor="middle" fill="#000000" fontSize={nameFontSize} fontWeight={700} stroke="#fff" strokeWidth={0.1}>
            {name}
          </text>
          <text x={x + width / 2} y={y + height / 2 + 12} textAnchor="middle" fill="#000000" fontSize={valFontSize} fontWeight={700} stroke="#fff" strokeWidth={0.1}>
            {formattedValue}
          </text>
        </>
      )}
    </g>
  );
}

export default function ModuleEnergyTreemap({ data }) {
  const validData = data.filter(item => (item.mean || 0) > 0);
  const maxMean = validData.length > 0 ? Math.max(...validData.map((item) => item.mean)) : 0;
  const minVisualSize = maxMean * 0.015;

  const chartData = validData.map((item) => ({
    name: item.module,
    actualEnergy: item.mean || 0,
    size: Math.max(item.mean || 0, minVisualSize),
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
        <ResponsiveContainer width="100%" height={350}>
          <Treemap
            data={chartData}
            dataKey="size"
            stroke="#fff"
            fill="#8884d8"
            content={renderCustomContent}
            aspectRatio={4 / 3}
            isAnimationActive={false}
          />
        </ResponsiveContainer>
      </div>
    </div>
  );
}
