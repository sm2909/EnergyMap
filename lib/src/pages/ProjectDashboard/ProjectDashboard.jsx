import React, { useEffect, useState } from 'react';
import { fetchEnergyNested, fetchEnergyFlat } from '../../services/api';
import ViewToggle from '../../components/views/ViewToggle';
import NestedEnergyView from '../../components/views/NestedEnergyView';
import FlatEnergyView from '../../components/views/FlatEnergyView';
import Spinner from '../../components/ui/Spinner';
import ErrorBanner from '../../components/ui/ErrorBanner';
import './ProjectDashboard.css';

export default function ProjectDashboard({ projectName, onBack }) {
  const [view, setView] = useState('nested');
  const [nestedData, setNestedData] = useState(null);
  const [flatData, setFlatData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load both views in parallel
      const [nestedResponse, flatResponse] = await Promise.all([
        fetchEnergyNested(projectName),
        fetchEnergyFlat(projectName)
      ]);
      
      setNestedData(nestedResponse);
      setFlatData(flatResponse);
    } catch (err) {
      setError(err.message || 'Unable to load project energy data.');
      setNestedData(null);
      setFlatData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectName]);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Energy Consumption Analysis: {projectName}</h1>
          <p className="dashboard__subtitle">Software Energy Consumption Analysis Dashboard</p>
        </div>
        <button onClick={onBack} className="dashboard__back-btn">Change Project</button>
      </header>

      {loading ? (
        <Spinner />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadData} />
      ) : (
        <>
          <ViewToggle 
            activeView={view} 
            onChange={setView} 
            options={['nested', 'flat']}
          />
          
          <section className="dashboard__main-view" aria-label="Energy visualization views">
            {view === 'nested' && <NestedEnergyView data={nestedData} />}
            {view === 'flat' && <FlatEnergyView data={flatData} />}
          </section>
        </>
      )}
    </div>
  );
}
