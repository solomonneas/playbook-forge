# Playbook Forge

Convert markdown/mermaid playbooks to visual IR (Intermediate Representation) flowcharts.

## Overview

Playbook Forge is a web application that transforms textual playbooks (written in markdown or mermaid syntax) into interactive, visual flowchart diagrams. It provides an intuitive interface for security operations, incident response, and process documentation teams to create and visualize procedural workflows.

## Architecture

- **Backend**: FastAPI (Python) - Handles playbook parsing and conversion to IR graph format
- **Frontend**: React (TypeScript) - Provides interactive UI and flowchart visualization
- **Visualization**: react-flow-renderer - Renders interactive node-edge graphs

## Project Structure

```
playbook-forge/
├── api/                    # FastAPI backend
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── models.py          # Pydantic data models
│   └── routers/           # API route handlers
│       ├── __init__.py
│       └── playbooks.py   # Playbook parsing endpoints
├── web/                   # React frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── PlaybookInput.tsx
│   │   │   ├── PlaybookInput.css
│   │   │   ├── FlowchartViewer.tsx
│   │   │   └── FlowchartViewer.css
│   │   ├── App.tsx        # Main application component
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   └── tsconfig.json
├── requirements.txt       # Python dependencies
├── Makefile              # Development commands
└── README.md             # This file
```

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
make dev-api
# Or manually:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the web directory:
```bash
cd web
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
make dev-web
# Or manually:
npm start
```

The web application will be available at `http://localhost:3000`

### Quick Start with Makefile

```bash
# Install all dependencies
make install

# Run both backend and frontend in development mode
make dev

# Build production artifacts
make build

# Clean build artifacts
make clean
```

## API Endpoints

### `POST /api/playbooks/parse`

Parse a playbook document and return the IR graph structure.

**Request Body:**
```json
{
  "content": "# Step 1\n## Step 2",
  "format": "markdown"
}
```

**Response:**
```json
{
  "graph": {
    "nodes": [
      {"id": "start", "label": "Start", "type": "start"},
      {"id": "step1", "label": "Example Step", "type": "default"}
    ],
    "edges": [
      {"id": "e1", "source": "start", "target": "step1"}
    ]
  },
  "metadata": {
    "format": "markdown",
    "node_count": 2,
    "edge_count": 1
  },
  "errors": []
}
```

### `GET /api/health`

Health check endpoint for monitoring.

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation using Python type annotations
- **python-markdown** - Markdown parsing and processing

### Frontend
- **React** - Component-based UI library
- **TypeScript** - Type-safe JavaScript
- **react-flow-renderer** - Interactive node-based graph visualization
- **Tailwind CSS** - Utility-first CSS framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Enhancements

- [ ] Advanced mermaid syntax support
- [ ] Export to PNG/SVG
- [ ] Playbook validation and linting
- [ ] Real-time collaboration
- [ ] Template library
- [ ] Version control integration

## License

MIT License - See LICENSE file for details
