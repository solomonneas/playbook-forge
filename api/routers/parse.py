"""
Parse Router

Handles the POST /api/parse endpoint for converting markdown/mermaid text to flowchart JSON.
"""

import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from api.models import ParseRequest, ParseResponse, ParseMetadata, PlaybookNode, PlaybookEdge
from api.parsers.markdown_parser import MarkdownParser
from api.parsers.mermaid_parser import MermaidParser

router = APIRouter()


def detect_format(content: str) -> str:
    """
    Auto-detect whether content is markdown or mermaid format.

    Args:
        content: Text content to analyze

    Returns:
        'mermaid' if content starts with flowchart/graph keywords, else 'markdown'
    """
    content_stripped = content.strip()

    # Check for mermaid flowchart indicators
    mermaid_patterns = [
        r'^flowchart\s+(TD|LR|TB|RL|BT)',
        r'^graph\s+(TD|LR|TB|RL|BT)',
    ]

    for pattern in mermaid_patterns:
        if re.match(pattern, content_stripped, re.IGNORECASE):
            return 'mermaid'

    # Default to markdown
    return 'markdown'


def extract_title(content: str, format_type: str) -> Optional[str]:
    """
    Extract title from content based on format.

    Args:
        content: Text content
        format_type: 'markdown' or 'mermaid'

    Returns:
        Extracted title or None
    """
    if format_type == 'markdown':
        # Look for first H1 header
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    elif format_type == 'mermaid':
        # Look for flowchart/graph title
        match = re.search(r'^(?:flowchart|graph)\s+\w+\s*:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_description(content: str, format_type: str) -> Optional[str]:
    """
    Extract description from content based on format.

    Args:
        content: Text content
        format_type: 'markdown' or 'mermaid'

    Returns:
        Extracted description or None
    """
    if format_type == 'markdown':
        # Look for first paragraph after title
        lines = content.split('\n')
        found_title = False
        for line in lines:
            stripped = line.strip()
            if not found_title and stripped.startswith('#'):
                found_title = True
                continue
            if found_title and stripped and not stripped.startswith('#'):
                return stripped
    elif format_type == 'mermaid':
        # Look for comment at the top
        match = re.search(r'^%%\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

    return None


@router.post("/parse", response_model=ParseResponse)
async def parse_content(request: ParseRequest):
    """
    Parse markdown or mermaid text and return flowchart JSON.

    This endpoint accepts markdown or mermaid flowchart syntax and converts it
    to a structured graph format with nodes and edges. Format detection is automatic
    if not specified.

    Args:
        request: ParseRequest with content and optional format

    Returns:
        ParseResponse with nodes, edges, and metadata

    Raises:
        HTTPException: 400 if content is empty or parsing fails
        HTTPException: 422 if format is invalid
    """
    # Validate content
    content = request.content.strip()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Content cannot be empty"
        )

    # Detect or validate format
    if request.format is None:
        format_type = detect_format(content)
    else:
        format_type = request.format.lower()
        if format_type not in ['markdown', 'mermaid']:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid format '{request.format}'. Must be 'markdown' or 'mermaid'."
            )

    # Parse content based on format
    try:
        if format_type == 'markdown':
            parser = MarkdownParser()
            graph = parser.parse(content)
        elif format_type == 'mermaid':
            parser = MermaidParser()
            graph = parser.parse(content)
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported format: {format_type}"
            )

        # Extract metadata
        title = extract_title(content, format_type)
        description = extract_description(content, format_type)

        # Build response
        metadata = ParseMetadata(
            title=title,
            description=description,
            format=format_type,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges)
        )

        return ParseResponse(
            nodes=graph.nodes,
            edges=graph.edges,
            metadata=metadata
        )

    except Exception as e:
        # Handle parsing errors gracefully
        error_message = str(e)

        # Check for common parsing issues
        if "invalid syntax" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Malformed {format_type} syntax: {error_message}"
            )
        elif "unexpected" in error_message.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected content in {format_type}: {error_message}"
            )
        else:
            # Generic parsing error
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse {format_type} content: {error_message}"
            )


@router.get("/formats")
async def list_supported_formats():
    """
    List supported input formats.

    Returns:
        Dictionary with supported formats and their descriptions
    """
    return {
        "formats": [
            {
                "name": "markdown",
                "description": "Structured markdown with headers, lists, and code blocks",
                "detection": "Default format when no flowchart/graph keyword is found"
            },
            {
                "name": "mermaid",
                "description": "Mermaid flowchart syntax (flowchart TD/LR or graph TD/LR)",
                "detection": "Auto-detected when content starts with 'flowchart' or 'graph'"
            }
        ]
    }
