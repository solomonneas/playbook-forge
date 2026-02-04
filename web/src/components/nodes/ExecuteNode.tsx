/**
 * ExecuteNode Component
 *
 * Represents an execution or action node in the playbook.
 * Execute nodes indicate specific operations or commands to be performed.
 */

import React, { memo } from 'react';
import { Handle, Position } from 'react-flow-renderer';
import './NodeStyles.css';

interface ExecuteNodeProps {
  data: {
    label: string;
    metadata?: Record<string, any>;
  };
}

const ExecuteNode: React.FC<ExecuteNodeProps> = ({ data }) => {
  return (
    <div className="custom-node execute-node">
      <Handle type="target" position={Position.Top} className="node-handle" />
      <div className="node-icon">⚙️</div>
      <div className="node-content">
        <div className="node-label">{data.label}</div>
        <div className="node-type-badge">Execute</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
};

export default memo(ExecuteNode);
