import React, { useState } from 'react';
import ProjectDashboard from './pages/ProjectDashboard/ProjectDashboard';
import ProjectSelection from './pages/ProjectSelection/ProjectSelection';

export default function App() {
  const [selectedProject, setSelectedProject] = useState(null);

  if (!selectedProject) {
    return <ProjectSelection onProjectSelect={setSelectedProject} />;
  }

  return <ProjectDashboard projectName={selectedProject} onBack={() => setSelectedProject(null)} />;
}
