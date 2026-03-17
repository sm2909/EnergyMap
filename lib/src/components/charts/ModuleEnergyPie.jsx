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

export default function ModuleEnergyPie({ data }) {
  const chartData = data.map((item) => ({
    name: item.module,
    value: item.mean,
  }));

  // Create an array of visually distinct colors for each slice in the pie chart
  const pieColors = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', 
    '#A28DFF', '#FF6666', '#8884d8', '#82ca9d',
    '#a4de6c', '#d0ed57', '#ffc658', '#4A90E2',
    '#E91E63', '#50E3C2', '#F5A623', '#D0021B',
    '#7ED321', '#9013FE', '#BD10E0', '#4A4A4A'
  ];

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
              {chartData.map((entry, index) => (
                <Cell key={entry.name} fill={pieColors[index % pieColors.length]} />
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
