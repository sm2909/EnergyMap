import React, { useState } from 'react';
import './ProjectSelection.css';

export default function ProjectSelection({ onProjectSelect }) {
  const [inputValue, setInputValue] = useState('');
  const [message, setMessage] = useState('');

  const validProjects = ['flask', 'black', 'requests'];

  const handleSubmit = (e) => {
    e.preventDefault();
    const project = inputValue.trim().toLowerCase();
    if (!project) return;

    if (validProjects.includes(project)) {
      onProjectSelect(project);
    } else {
      setMessage('That project stats will be implemented soon.');
    }
  };

  return (
    <div className="project-selection-container">
      <div className="project-selection-card">
        <h1>Select a Project</h1>
        <p>Enter the name of the project to view its energy statistics.</p>
        <p className="hint">Available projects: flask, black, requests</p>
        
        <form onSubmit={handleSubmit} className="project-selection-form">
          <input
            type="text"
            placeholder="e.g., flask"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setMessage(''); // Clear message on new input
            }}
            className="project-input"
          />
          <button type="submit" className="submit-btn">View Stats</button>
        </form>

        {message && <div className="message">{message}</div>}
      </div>
    </div>
  );
}