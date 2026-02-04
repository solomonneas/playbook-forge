/**
 * Type definitions for Playbook Forge
 *
 * Defines the data structures used throughout the application,
 * matching the API response format.
 */

import { Node, Edge } from 'react-flow-renderer';

/**
 * Node type enumeration
 * Defines the different types of nodes in a playbook flowchart
 */
export type NodeType = 'phase' | 'step' | 'decision' | 'execute' | 'start' | 'end' | 'default';

/**
 * Playbook node from API
 */
export interface PlaybookNode {
  id: string;
  label: string;
  type: NodeType;
  metadata?: Record<string, any>;
}

/**
 * Playbook edge from API
 */
export interface PlaybookEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

/**
 * Complete playbook graph structure from API
 */
export interface PlaybookGraph {
  nodes: PlaybookNode[];
  edges: PlaybookEdge[];
}

/**
 * Extended data for custom React Flow nodes
 */
export interface CustomNodeData {
  label: string;
  type: NodeType;
  metadata?: Record<string, any>;
}

/**
 * Custom React Flow node with typed data
 */
export type FlowNode = Node<CustomNodeData>;

/**
 * Custom React Flow edge with typed data
 */
export type FlowEdge = Edge;
