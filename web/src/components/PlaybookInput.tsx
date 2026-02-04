/**
 * PlaybookInput Component
 *
 * Provides a text area for users to input markdown or mermaid playbook content
 * and controls to submit for parsing.
 */

import React, { useState } from 'react';
import './PlaybookInput.css';

interface PlaybookInputProps {
  onSubmit: (content: string, format: string) => void;
  loading: boolean;
}

const PlaybookInput: React.FC<PlaybookInputProps> = ({ onSubmit, loading }) => {
  const [content, setContent] = useState('');
  const [format, setFormat] = useState('markdown');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim()) {
      onSubmit(content, format);
    }
  };

  const exampleMarkdown = `# Example Playbook

## Step 1: Initialize
Start the process

## Step 2: Check Condition
Decision point

## Step 3: Process
Execute action

## Step 4: Complete
End the process`;

  const loadExample = () => {
    setContent(exampleMarkdown);
  };

  return (
    <div className="playbook-input">
      <form onSubmit={handleSubmit}>
        <div className="form-header">
          <h2>Input Playbook</h2>
          <div className="format-selector">
            <label>
              <input
                type="radio"
                value="markdown"
                checked={format === 'markdown'}
                onChange={(e) => setFormat(e.target.value)}
              />
              Markdown
            </label>
            <label>
              <input
                type="radio"
                value="mermaid"
                checked={format === 'mermaid'}
                onChange={(e) => setFormat(e.target.value)}
              />
              Mermaid
            </label>
          </div>
        </div>

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={`Paste your ${format} playbook here...`}
          rows={15}
          disabled={loading}
        />

        <div className="button-group">
          <button type="button" onClick={loadExample} disabled={loading}>
            Load Example
          </button>
          <button type="submit" disabled={loading || !content.trim()}>
            {loading ? 'Parsing...' : 'Parse Playbook'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PlaybookInput;
