# FlowCanvas Component

React Flow canvas component for visualizing playbook flowcharts with custom node types.

## Overview

The FlowCanvas component renders interactive flowcharts from parsed playbook data. It provides:

- Custom node types with distinct visual styling
- Drag-and-drop node positioning
- Zoom and pan controls
- Animated directional edges with arrows
- Minimap for navigation
- Automatic layout algorithm

## Custom Node Types

### PhaseNode
- **Icon:** 📋
- **Color:** Purple gradient
- **Usage:** High-level phases or major sections
- **Badge:** "Phase"

### StepNode
- **Icon:** ▶️
- **Color:** Blue gradient
- **Usage:** Individual actions or tasks
- **Badge:** "Step"

### DecisionNode
- **Icon:** ❓
- **Color:** Orange gradient
- **Usage:** Conditional branches or decision points
- **Badge:** "Decision"
- **Handles:** Top (input), Bottom + Right (outputs)

### ExecuteNode
- **Icon:** ⚙️
- **Color:** Green gradient
- **Usage:** Execution or operation commands
- **Badge:** "Execute"

## Usage

```tsx
import FlowCanvas from './components/FlowCanvas';
import { PlaybookGraph } from './types';

const graph: PlaybookGraph = {
  nodes: [
    { id: '1', label: 'Initialize', type: 'phase' },
    { id: '2', label: 'Check Status', type: 'decision' },
    { id: '3', label: 'Execute Task', type: 'execute' },
  ],
  edges: [
    { id: 'e1-2', source: '1', target: '2' },
    { id: 'e2-3', source: '2', target: '3', label: 'yes' },
  ],
};

<FlowCanvas graph={graph} />
```

## Props

### FlowCanvas

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `graph` | `PlaybookGraph` | Yes | The flowchart data to render |
| `onNodesChange` | `(nodes: FlowNode[]) => void` | No | Callback for node updates |
| `onEdgesChange` | `(edges: FlowEdge[]) => void` | No | Callback for edge updates |

## Layout Algorithm

The component uses a BFS-based layout algorithm:

1. Identifies start nodes (no incoming edges)
2. Assigns vertical levels via breadth-first traversal
3. Distributes nodes horizontally within each level
4. Calculates positions with configurable spacing
5. Centers nodes in their horizontal slots

**Spacing:**
- Vertical: 150px between levels
- Horizontal: 250px between nodes in same level

## Styling

Custom node styles are defined in `nodes/NodeStyles.css`:

- GitHub dark theme color scheme
- Hover effects with shadow and transform
- Gradient backgrounds per node type
- Consistent handle styling
- Selection highlights

Canvas styles in `FlowCanvas.css`:

- Dark background (#0d1117)
- Styled controls and minimap
- Animated edges with dash animation
- Responsive design (hides minimap on mobile)

## Dependencies

- `react-flow-renderer` (^10.3.17)
- Custom node components in `./nodes/`
- Type definitions in `../types/`

## Integration

To replace the existing FlowchartViewer:

```tsx
// In App.tsx, replace:
import FlowchartViewer from './components/FlowchartViewer';

// With:
import FlowCanvas from './components/FlowCanvas';

// Update render:
<FlowCanvas graph={graph} />
```

## Features

### Interactive Controls
- **Zoom:** Mouse wheel or controls panel
- **Pan:** Click and drag canvas
- **Fit View:** Auto-centers flowchart
- **Minimap:** Overview with node colors

### Edge Features
- Smooth step edge type
- Animated flow with dashes
- Arrow markers showing direction
- Optional labels (e.g., "yes", "no")
- Hover effects

### Node Features
- Draggable positioning
- Selection highlighting
- Type-specific icons and colors
- Metadata support
- Connection handles (top/bottom)

## File Structure

```
web/src/
├── components/
│   ├── FlowCanvas.tsx          # Main canvas component
│   ├── FlowCanvas.css          # Canvas styling
│   ├── FlowCanvas.README.md    # This file
│   └── nodes/
│       ├── PhaseNode.tsx
│       ├── StepNode.tsx
│       ├── DecisionNode.tsx
│       ├── ExecuteNode.tsx
│       ├── NodeStyles.css      # Shared node styles
│       └── index.ts            # Node exports
└── types/
    └── index.ts                # Type definitions
```

## Extending

To add a new node type:

1. Create `NewNode.tsx` in `nodes/`
2. Add styles in `NodeStyles.css`
3. Export from `nodes/index.ts`
4. Add to `nodeTypes` in FlowCanvas
5. Update TypeScript types

## Performance

- Uses React.memo for node components
- Memoized nodeTypes object
- Efficient BFS layout algorithm
- Minimal re-renders on prop changes
