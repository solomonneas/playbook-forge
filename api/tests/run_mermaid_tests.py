#!/usr/bin/env python3
"""
Manual test runner for Mermaid parser (no pytest required).

Run this script to validate the Mermaid parser functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.parsers.mermaid_parser import MermaidParser
from api.models import PlaybookGraph


def test_basic_parsing():
    """Test basic Mermaid parsing functionality."""
    print("Test 1: Basic Parsing")
    print("-" * 50)

    parser = MermaidParser()

    content = """flowchart TD
    Start[Start Process] --> Auth{Authenticated?}
    Auth --Yes--> Load[Load Data]
    Auth --No--> Login[Show Login]
    Login --> Auth
    Load --> End[Complete]"""

    result = parser.parse(content)

    print(f"Total nodes: {len(result.nodes)}")
    print(f"Total edges: {len(result.edges)}")
    print()

    print("Nodes:")
    for node in result.nodes:
        print(f"  [{node.type}] {node.id}: {node.label}")

    print()
    print("Edges:")
    for edge in result.edges:
        label_str = f" ({edge.label})" if edge.label else ""
        print(f"  {edge.id}: {edge.source} -> {edge.target}{label_str}")

    print()

    # Validations
    assert len(result.nodes) > 0, "Should have nodes"
    assert len(result.edges) > 0, "Should have edges"

    node_types = {node.type for node in result.nodes}
    assert "step" in node_types, "Should have step nodes"
    assert "decision" in node_types, "Should have decision nodes"

    print("✓ Basic parsing test passed!")
    print()


def test_node_shapes():
    """Test different node shape parsing."""
    print("Test 2: Node Shapes")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    A[Square Node]
    B{Diamond Node}
    C(Rounded Node)
    D((Circle Node))"""

    result = parser.parse(content)

    print(f"Nodes found: {len(result.nodes)}")

    for node in result.nodes:
        print(f"  {node.label} -> type: {node.type}")

    assert len(result.nodes) == 4, "Should have 4 nodes"

    # Check for different types
    node_types = [n.type for n in result.nodes]
    assert "step" in node_types, "Should have step nodes"
    assert "decision" in node_types, "Should have decision nodes"
    assert "phase" in node_types, "Should have phase nodes"

    print("✓ Node shapes test passed!")
    print()


def test_edge_types():
    """Test different edge type parsing."""
    print("Test 3: Edge Types")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    A[Start] --> B[Solid]
    B -.-> C[Dotted]
    C ==> D[Bold]"""

    result = parser.parse(content)

    print(f"Edges found: {len(result.edges)}")
    print(f"Nodes: {len(result.nodes)}")

    assert len(result.nodes) == 4, "Should have 4 nodes"
    assert len(result.edges) == 3, "Should have 3 edges"

    print("✓ Edge types test passed!")
    print()


def test_labeled_edges():
    """Test edges with labels."""
    print("Test 4: Labeled Edges")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    A[Check] --Yes--> B[Accept]
    A --No--> C[Reject]"""

    result = parser.parse(content)

    print(f"Nodes: {len(result.nodes)}")
    print(f"Edges: {len(result.edges)}")

    labeled_edges = [e for e in result.edges if e.label]
    print(f"Labeled edges: {len(labeled_edges)}")

    for edge in labeled_edges:
        print(f"  {edge.label}")

    assert len(labeled_edges) >= 1, "Should have labeled edges"

    print("✓ Labeled edges test passed!")
    print()


def test_subgraphs():
    """Test subgraph parsing."""
    print("Test 5: Subgraphs")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    subgraph Setup Phase
        A[Install] --> B[Configure]
    end
    B --> C[Run]"""

    result = parser.parse(content)

    print(f"Total nodes: {len(result.nodes)}")

    phase_nodes = [n for n in result.nodes if n.type == "phase"]
    print(f"Phase nodes: {len(phase_nodes)}")

    for node in phase_nodes:
        print(f"  {node.label}")

    assert len(phase_nodes) >= 1, "Should have at least one phase node"

    # Check for subgraph indicator
    subgraph_phases = [n for n in phase_nodes if n.metadata and n.metadata.get("is_subgraph")]
    assert len(subgraph_phases) == 1, "Should have subgraph phase"

    print("✓ Subgraphs test passed!")
    print()


def test_complex_flowchart():
    """Test complex flowchart with multiple features."""
    print("Test 6: Complex Flowchart")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    Start[Start Process] --> Auth{Authenticated?}
    Auth --Yes--> Load[Load Data]
    Auth --No--> Login[Show Login]
    Login --> Auth
    Load --> Process((Processing))
    Process --> Save[Save Results]
    Save -.-> Notify[Send Notification]
    Save --> End[Complete]"""

    result = parser.parse(content)

    print(f"Total nodes: {len(result.nodes)}")
    print(f"Total edges: {len(result.edges)}")

    # Count node types
    type_counts = {}
    for node in result.nodes:
        type_counts[node.type] = type_counts.get(node.type, 0) + 1

    print("\nNode type distribution:")
    for node_type, count in sorted(type_counts.items()):
        print(f"  {node_type}: {count}")

    assert len(result.nodes) >= 7, "Should have multiple nodes"
    assert len(result.edges) >= 6, "Should have multiple edges"

    # Check node types variety
    assert len(type_counts) >= 2, "Should have multiple node types"

    print("\n✓ Complex flowchart test passed!")
    print()


def test_incident_response_flowchart():
    """Test with realistic incident response flowchart."""
    print("Test 7: Incident Response Flowchart")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    Alert[Receive Alert] --> Verify{Legitimate?}
    Verify --No--> Close[Close Alert]
    Verify --Yes--> Classify{Severity}

    subgraph Critical Path
        Classify --Critical--> Escalate[Activate Response Team]
        Escalate --> Investigate[Deep Investigation]
    end

    Classify --Low--> Assign[Assign to Engineer]
    Assign --> Monitor[Monitor Progress]

    Investigate --> Remediate[Apply Fix]
    Monitor --> Remediate
    Remediate --> Verify2{Fixed?}
    Verify2 --Yes--> Document[Document Incident]
    Verify2 --No--> Investigate
    Document --> Close"""

    result = parser.parse(content)

    print(f"Total nodes: {len(result.nodes)}")
    print(f"Total edges: {len(result.edges)}")

    # Count node types
    type_counts = {}
    for node in result.nodes:
        type_counts[node.type] = type_counts.get(node.type, 0) + 1

    print("\nNode type distribution:")
    for node_type, count in sorted(type_counts.items()):
        print(f"  {node_type}: {count}")

    # Validations
    assert len(result.nodes) >= 10, "Should have substantial content"
    assert "step" in type_counts, "Should have step nodes"
    assert "decision" in type_counts, "Should have decision nodes"
    assert "phase" in type_counts, "Should have phase nodes (subgraph)"

    # Verify graph connectivity
    node_ids = {n.id for n in result.nodes}
    for edge in result.edges:
        assert edge.source in node_ids, f"Invalid source: {edge.source}"
        assert edge.target in node_ids, f"Invalid target: {edge.target}"

    print("\n✓ Incident response flowchart test passed!")
    print()


def test_graph_structure_compatibility():
    """Test that output matches markdown parser structure."""
    print("Test 8: Structure Compatibility")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart TD
    A[Start] --> B{Check}
    B --Yes--> C[Process]
    B --No--> D[Skip]"""

    result = parser.parse(content)

    # Verify structure
    assert isinstance(result, PlaybookGraph), "Should return PlaybookGraph"
    assert hasattr(result, 'nodes'), "Should have nodes attribute"
    assert hasattr(result, 'edges'), "Should have edges attribute"
    assert isinstance(result.nodes, list), "Nodes should be a list"
    assert isinstance(result.edges, list), "Edges should be a list"

    # Verify all nodes have required fields
    for node in result.nodes:
        assert hasattr(node, 'id'), "Node missing id"
        assert hasattr(node, 'label'), "Node missing label"
        assert hasattr(node, 'type'), "Node missing type"
        assert hasattr(node, 'metadata'), "Node missing metadata"
        assert node.id is not None, "Node id cannot be None"
        assert node.label is not None, "Node label cannot be None"
        print(f"  ✓ Node {node.id}: valid")

    # Verify all edges have required fields
    for edge in result.edges:
        assert hasattr(edge, 'id'), "Edge missing id"
        assert hasattr(edge, 'source'), "Edge missing source"
        assert hasattr(edge, 'target'), "Edge missing target"
        assert hasattr(edge, 'label'), "Edge missing label attribute"
        assert edge.id is not None, "Edge id cannot be None"
        assert edge.source is not None, "Edge source cannot be None"
        assert edge.target is not None, "Edge target cannot be None"
        print(f"  ✓ Edge {edge.id}: valid")

    print("\n✓ Structure compatibility test passed!")
    print()


def test_deployment_pipeline():
    """Test deployment pipeline flowchart."""
    print("Test 9: Deployment Pipeline")
    print("-" * 50)

    parser = MermaidParser()
    content = """flowchart LR
    Code[Write Code] --> Commit[Commit Changes]
    Commit --> Build{Build Success?}
    Build --No--> Fix[Fix Build]
    Fix --> Build
    Build --Yes--> Test{Tests Pass?}
    Test --No--> Debug[Debug Tests]
    Debug --> Test
    Test --Yes--> Deploy((Deploy to Staging))
    Deploy --> Smoke{Smoke Tests OK?}
    Smoke --Yes--> Prod[Deploy to Production]
    Smoke --No--> Rollback[Rollback]"""

    result = parser.parse(content)

    print(f"Total nodes: {len(result.nodes)}")
    print(f"Total edges: {len(result.edges)}")

    assert len(result.nodes) >= 10, "Should have all pipeline nodes"
    assert len(result.edges) >= 10, "Should have all pipeline edges"

    # Check for node type variety
    node_types = {node.type for node in result.nodes}
    assert len(node_types) >= 2, "Should have multiple node types"

    print("✓ Deployment pipeline test passed!")
    print()


def main():
    """Run all tests."""
    print("=" * 50)
    print("Mermaid Parser Test Suite")
    print("=" * 50)
    print()

    tests = [
        test_basic_parsing,
        test_node_shapes,
        test_edge_types,
        test_labeled_edges,
        test_subgraphs,
        test_complex_flowchart,
        test_incident_response_flowchart,
        test_graph_structure_compatibility,
        test_deployment_pipeline,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            print()
            failed += 1

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
