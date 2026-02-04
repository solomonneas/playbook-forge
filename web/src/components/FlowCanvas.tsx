/**
 * FlowCanvas Component
 *
 * Main React Flow canvas component that renders nodes and edges from parser output.
 * Supports custom node types (Phase, Step, Decision, Execute) with distinct styling,
 * drag-and-drop, zoom/pan controls, and directional edges.
 */

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Connection,
  addEdge,
  NodeTypes,
  MarkerType,
} from 'react-flow-renderer';

import PhaseNode from './nodes/PhaseNode';
import StepNode from './nodes/StepNode';
import DecisionNode from './nodes/DecisionNode';
import ExecuteNode from './nodes/ExecuteNode';
import { PlaybookGraph, FlowNode, FlowEdge } from '../types';

import './FlowCanvas.css';

interface FlowCanvasProps {
  graph: PlaybookGraph;
  onNodesChange?: (nodes: FlowNode[]) => void;
  onEdgesChange?: (edges: FlowEdge[]) => void;
}

/**
 * Converts a playbook graph to React Flow format with proper positioning
 * Uses a simple vertical layout algorithm for node placement
 */
const convertToFlowFormat = (graph: PlaybookGraph): { nodes: FlowNode[]; edges: FlowEdge[] } => {
  // Create a map to track node positions by level
  const levelMap = new Map<string, number>();
  const visited = new Set<string>();

  // Build adjacency list for traversal
  const adjList = new Map<string, string[]>();
  graph.edges.forEach(edge => {
    if (!adjList.has(edge.source)) {
      adjList.set(edge.source, []);
    }
    adjList.get(edge.source)!.push(edge.target);
  });

  // BFS to assign levels
  const queue: Array<{ id: string; level: number }> = [];

  // Find start nodes (nodes with no incoming edges)
  const hasIncoming = new Set(graph.edges.map(e => e.target));
  const startNodes = graph.nodes.filter(n => !hasIncoming.has(n.id));

  if (startNodes.length > 0) {
    startNodes.forEach(node => queue.push({ id: node.id, level: 0 }));
  } else if (graph.nodes.length > 0) {
    // If no clear start, use first node
    queue.push({ id: graph.nodes[0].id, level: 0 });
  }

  while (queue.length > 0) {
    const { id, level } = queue.shift()!;

    if (visited.has(id)) continue;
    visited.add(id);
    levelMap.set(id, level);

    const children = adjList.get(id) || [];
    children.forEach(childId => {
      if (!visited.has(childId)) {
        queue.push({ id: childId, level: level + 1 });
      }
    });
  }

  // Assign levels to any unvisited nodes
  graph.nodes.forEach(node => {
    if (!levelMap.has(node.id)) {
      levelMap.set(node.id, 0);
    }
  });

  // Count nodes per level for horizontal spacing
  const nodesPerLevel = new Map<number, number>();
  levelMap.forEach(level => {
    nodesPerLevel.set(level, (nodesPerLevel.get(level) || 0) + 1);
  });

  // Track horizontal position per level
  const levelCounters = new Map<number, number>();

  // Convert nodes with calculated positions
  const flowNodes: FlowNode[] = graph.nodes.map(node => {
    const level = levelMap.get(node.id) || 0;
    const nodesInLevel = nodesPerLevel.get(level) || 1;
    const horizontalIndex = levelCounters.get(level) || 0;
    levelCounters.set(level, horizontalIndex + 1);

    // Calculate position
    const verticalSpacing = 150;
    const horizontalSpacing = 250;
    const horizontalOffset = (horizontalIndex - (nodesInLevel - 1) / 2) * horizontalSpacing;

    return {
      id: node.id,
      type: node.type,
      data: {
        label: node.label,
        type: node.type,
        metadata: node.metadata,
      },
      position: {
        x: 400 + horizontalOffset,
        y: level * verticalSpacing + 50,
      },
    };
  });

  // Convert edges with arrow markers
  const flowEdges: FlowEdge[] = graph.edges.map(edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    animated: true,
    style: {
      stroke: '#58a6ff',
      strokeWidth: 2,
    },
    labelStyle: {
      fill: '#c9d1d9',
      fontWeight: 500,
      fontSize: 12,
    },
    labelBgStyle: {
      fill: '#161b22',
      fillOpacity: 0.9,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 20,
      height: 20,
      color: '#58a6ff',
    },
  }));

  return { nodes: flowNodes, edges: flowEdges };
};

const FlowCanvas: React.FC<FlowCanvasProps> = ({ graph, onNodesChange, onEdgesChange }) => {
  // Convert graph to flow format
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => convertToFlowFormat(graph),
    [graph]
  );

  const [nodes, setNodes] = React.useState<FlowNode[]>(initialNodes);
  const [edges, setEdges] = React.useState<FlowEdge[]>(initialEdges);

  // Update nodes when graph changes
  React.useEffect(() => {
    const converted = convertToFlowFormat(graph);
    setNodes(converted.nodes);
    setEdges(converted.edges);
  }, [graph]);

  // Define custom node types
  const nodeTypes: NodeTypes = useMemo(
    () => ({
      phase: PhaseNode,
      step: StepNode,
      decision: DecisionNode,
      execute: ExecuteNode,
    }),
    []
  );

  // Handle connection creation
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    []
  );

  // Notify parent of node changes
  const handleNodesChange = useCallback(
    (changes: any) => {
      setNodes((nds) => {
        // Apply changes (from react-flow-renderer's applyNodeChanges if available)
        // For now, we'll handle basic updates
        const updatedNodes = [...nds];
        if (onNodesChange) {
          onNodesChange(updatedNodes);
        }
        return updatedNodes;
      });
    },
    [onNodesChange]
  );

  // Notify parent of edge changes
  const handleEdgesChange = useCallback(
    (changes: any) => {
      setEdges((eds) => {
        const updatedEdges = [...eds];
        if (onEdgesChange) {
          onEdgesChange(updatedEdges);
        }
        return updatedEdges;
      });
    },
    [onEdgesChange]
  );

  return (
    <div className="flow-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onConnect={onConnect}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        attributionPosition="bottom-right"
        minZoom={0.1}
        maxZoom={2}
        defaultZoom={1}
      >
        <Background
          color="#30363d"
          gap={16}
          size={1}
          variant="dots"
        />
        <Controls
          showInteractive={false}
        />
        <MiniMap
          nodeColor={(node) => {
            // Color minimap nodes based on type
            switch (node.type) {
              case 'phase': return '#8957e5';
              case 'step': return '#1f6feb';
              case 'decision': return '#f78166';
              case 'execute': return '#238636';
              default: return '#58a6ff';
            }
          }}
          maskColor="rgba(13, 17, 23, 0.85)"
          style={{
            backgroundColor: '#161b22',
            border: '1px solid #30363d',
          }}
        />
      </ReactFlow>
    </div>
  );
};

export default FlowCanvas;
