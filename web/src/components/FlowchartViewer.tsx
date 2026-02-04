/**
 * FlowchartViewer Component
 *
 * Renders an interactive flowchart visualization using react-flow-renderer.
 * Displays the parsed playbook as a visual graph with nodes and edges.
 */

import React, { useEffect, useState } from 'react';
import ReactFlow, { Node, Edge, Background, Controls, MiniMap } from 'react-flow-renderer';
import './FlowchartViewer.css';

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

interface FlowchartViewerProps {
  graph: PlaybookGraph;
}

const FlowchartViewer: React.FC<FlowchartViewerProps> = ({ graph }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    // Convert playbook graph to react-flow format with auto-layout
    const flowNodes: Node[] = graph.nodes.map((node, index) => ({
      id: node.id,
      data: { label: node.label },
      position: { x: 250, y: index * 150 }, // Simple vertical layout
      type: node.type === 'decision' ? 'default' : 'default',
      style: {
        background: getNodeColor(node.type),
        color: '#fff',
        border: '1px solid #1f6feb',
        borderRadius: '8px',
        padding: '10px',
        width: 180,
      },
    }));

    const flowEdges: Edge[] = graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: true,
      style: { stroke: '#58a6ff' },
      labelStyle: { fill: '#c9d1d9', fontWeight: 500 },
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [graph]);

  const getNodeColor = (type: string): string => {
    switch (type) {
      case 'start':
        return '#238636';
      case 'end':
        return '#da3633';
      case 'decision':
        return '#f78166';
      default:
        return '#1f6feb';
    }
  };

  return (
    <div className="flowchart-viewer">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#30363d" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => node.style?.background as string || '#1f6feb'}
          maskColor="rgba(13, 17, 23, 0.8)"
        />
      </ReactFlow>
    </div>
  );
};

export default FlowchartViewer;
