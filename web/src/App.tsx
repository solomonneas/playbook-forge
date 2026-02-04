/**
 * Playbook Forge - Main Application Component
 *
 * Root component for the React application. Uses ImportView for
 * the complete markdown/mermaid import workflow with flowchart visualization.
 */

import React from 'react';
import './App.css';
import ImportView from './views/ImportView';

function App() {
  return (
    <div className="App">
      <ImportView />
    </div>
  );
}

export default App;
