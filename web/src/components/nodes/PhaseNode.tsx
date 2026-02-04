/**
 * PhaseNode Component
 *
 * Represents a high-level phase in the playbook flowchart.
 * Phases are major sections or stages of the process.
 */

import React, { memo } from 'react';
import { Handle, Position } from 'react-flow-renderer';
import './NodeStyles.css';

interface PhaseNodeProps {
  data: {
    label: string;
    metadata?: Record<string, any>;
  };
}

const PhaseNode: React.FC<PhaseNodeProps> = ({ data }) => {
  return (
    <div className="custom-node phase-node">
      <Handle type="target" position={Position.Top} className="node-handle" />
      <div className="node-icon">📋</div>
      <div className="node-content">
        <div className="node-label">{data.label}</div>
        <div className="node-type-badge">Phase</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
};

export default memo(PhaseNode);
