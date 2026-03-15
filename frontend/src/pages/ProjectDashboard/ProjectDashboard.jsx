import React, { useEffect, useMemo, useState } from 'react';
import { fetchProjectEnergy } from '../../services/api';
import StatCard from '../../components/cards/StatCard';
import ModuleEnergyPie from '../../components/charts/ModuleEnergyPie';
import ModuleEnergyTreemap from '../../components/charts/ModuleEnergyTreemap';
import ModuleEnergyBar from '../../components/charts/ModuleEnergyBar';
import ModuleEnergyTable from '../../components/table/ModuleEnergyTable';
import Spinner from '../../components/ui/Spinner';
import ErrorBanner from '../../components/ui/ErrorBanner';
import './ProjectDashboard.css';

const numberFormatter = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
};

export default function ProjectDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchProjectEnergy();
      if (!Array.isArray(response)) {
        throw new Error('Invalid API response structure');
      }
      setData(response);
    } catch (err) {
      setError(err.message || 'Unable to load project energy data.');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const summary = useMemo(() => {
    if (!data || data.length === 0) return null;

    const totalModules = data.length;
    const meanList = data.map((item) => item.mean ?? 0);
    const averageEnergy = meanList.reduce((acc, val) => acc + val, 0) / totalModules;

    const sortedByMean = [...data].sort((a, b) => (b.mean || 0) - (a.mean || 0));
    const highest = sortedByMean[0];
    const lowest = sortedByMean[sortedByMean.length - 1];

    return {
      totalModules,
      averageEnergy,
      highestModule: highest,
      lowestModule: lowest,
    };
  }, [data]);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Energy Consumption Analysis</h1>
          <p className="dashboard__subtitle">Software Energy Consumption Analysis Dashboard</p>
        </div>
      </header>

      {loading ? (
        <Spinner />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadData} />
      ) : (
        <>
          <section className="dashboard__overview" aria-label="Project overview">
            <StatCard
              title="Total Modules Analyzed"
              value={summary?.totalModules ?? '-'}
              description="Number of modules included in the analysis"
              icon={<span>🧩</span>}
              accentColor="var(--primary)"
            />
            <StatCard
              title="Average Energy Consumption"
              value={`${numberFormatter(summary?.averageEnergy)} J`}
              description="Mean energy across all modules"
              icon={<span>⚡</span>}
              accentColor="var(--secondary-accent)"
            />
            <StatCard
              title="Lowest Energy Module"
              value={summary?.lowestModule?.module ?? '-'}
              description={`Mean: ${numberFormatter(summary?.lowestModule?.mean)} J`}
              icon={<span>🟢</span>}
              accentColor="#2ECC71"
            />
            <StatCard
              title="Highest Energy Module"
              value={summary?.highestModule?.module ?? '-'}
              description={`Mean: ${numberFormatter(summary?.highestModule?.mean)} J`}
              icon={<span>🔴</span>}
              accentColor="#E74C3C"
            />
          </section>

          <section className="dashboard__charts" aria-label="Energy visualization charts">
            <ModuleEnergyPie data={data} />
            <ModuleEnergyTreemap data={data} />
            <ModuleEnergyBar data={data} />
          </section>

          <section className="dashboard__table" aria-label="Module statistics table">
            <ModuleEnergyTable data={data} />
          </section>
        </>
      )}
    </div>
  );
}
