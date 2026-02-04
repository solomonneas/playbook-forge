/**
 * Playbook Forge - Main Application Component
 *
 * Root component for the React application. Provides the main layout
 * and coordinates between playbook input and flowchart visualization.
 */

import React, { useState } from 'react';
import './App.css';
import PlaybookInput from './components/PlaybookInput';
import FlowchartViewer from './components/FlowchartViewer';

interface PlaybookGraph {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
  }>;
}

function App() {
  const [graph, setGraph] = useState<PlaybookGraph | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePlaybookSubmit = async (content: string, format: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/playbooks/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content, format }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setGraph(data.graph);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse playbook');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Playbook Forge</h1>
        <p>Convert markdown/mermaid playbooks to visual IR flowcharts</p>
      </header>

      <main className="App-main">
        <div className="container">
          <PlaybookInput onSubmit={handlePlaybookSubmit} loading={loading} />

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {graph && (
            <div className="flowchart-section">
              <h2>Flowchart Visualization</h2>
              <FlowchartViewer graph={graph} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
