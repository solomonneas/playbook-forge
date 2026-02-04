#!/usr/bin/env python3
"""
Manual test runner for markdown parser (no pytest required).

Run this script to validate the markdown parser functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.parsers.markdown_parser import MarkdownParser
from api.models import PlaybookGraph


def test_basic_parsing():
    """Test basic parsing functionality."""
    print("Test 1: Basic Parsing")
    print("-" * 50)

    parser = MarkdownParser()

    content = """# Deployment Pipeline

## Build Phase

1. Clone repository
2. Install dependencies
3. Run tests

```bash
npm install
npm test
```

## Deploy Phase

- If tests pass
  - Deploy to staging
  - Run smoke tests
- Else
  - Notify team
  - Stop deployment

4. Final verification"""

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
    assert "phase" in node_types, "Should have phase nodes"
    assert "step" in node_types, "Should have step nodes"
    assert "execute" in node_types, "Should have execute nodes"
    assert "decision" in node_types, "Should have decision nodes"

    print("✓ Basic parsing test passed!")
    print()


def test_headers():
    """Test header parsing."""
    print("Test 2: Header Parsing")
    print("-" * 50)

    parser = MarkdownParser()
    content = """# Main Phase
## Sub Phase 1
## Sub Phase 2"""

    result = parser.parse(content)

    phase_nodes = [n for n in result.nodes if n.type == "phase"]
    print(f"Phase nodes found: {len(phase_nodes)}")

    for node in phase_nodes:
        print(f"  {node.label} (level {node.metadata['level']})")

    assert len(phase_nodes) == 3, "Should have 3 phase nodes"
    assert phase_nodes[0].metadata["level"] == 1, "First should be H1"
    assert phase_nodes[1].metadata["level"] == 2, "Second should be H2"

    print("✓ Header parsing test passed!")
    print()


def test_sequential_steps():
    """Test numbered list parsing."""
    print("Test 3: Sequential Steps")
    print("-" * 50)

    parser = MarkdownParser()
    content = """1. First step
2. Second step
3. Third step"""

    result = parser.parse(content)

    print(f"Nodes: {len(result.nodes)}")
    print(f"Edges: {len(result.edges)}")

    assert len(result.nodes) == 3, "Should have 3 step nodes"
    assert len(result.edges) == 2, "Should have 2 connecting edges"

    # Verify chain
    assert result.edges[0].source == result.nodes[0].id
    assert result.edges[0].target == result.nodes[1].id
    assert result.edges[1].source == result.nodes[1].id
    assert result.edges[1].target == result.nodes[2].id

    print("✓ Sequential steps test passed!")
    print()


def test_decision_nodes():
    """Test decision node parsing."""
    print("Test 4: Decision Nodes")
    print("-" * 50)

    parser = MarkdownParser()
    content = """- If authentication succeeds
  - Load user profile
  - Redirect to dashboard"""

    result = parser.parse(content)

    decision_nodes = [n for n in result.nodes if n.type == "decision"]
    print(f"Decision nodes: {len(decision_nodes)}")

    assert len(decision_nodes) == 1, "Should have 1 decision node"

    decision_node = decision_nodes[0]
    print(f"Decision: {decision_node.label}")

    # Check branches
    branch_edges = [e for e in result.edges if e.source == decision_node.id]
    print(f"Branches: {len(branch_edges)}")

    for edge in branch_edges:
        target_node = next(n for n in result.nodes if n.id == edge.target)
        print(f"  {edge.label}: {target_node.label}")

    assert len(branch_edges) >= 2, "Should have branch edges"

    print("✓ Decision nodes test passed!")
    print()


def test_code_blocks():
    """Test code block parsing."""
    print("Test 5: Code Blocks")
    print("-" * 50)

    parser = MarkdownParser()
    content = """```bash
echo "Hello World"
npm install
```"""

    result = parser.parse(content)

    execute_nodes = [n for n in result.nodes if n.type == "execute"]
    print(f"Execute nodes: {len(execute_nodes)}")

    assert len(execute_nodes) == 1, "Should have 1 execute node"

    exec_node = execute_nodes[0]
    print(f"Label: {exec_node.label}")
    print(f"Language: {exec_node.metadata['language']}")
    print(f"Code length: {len(exec_node.metadata['code'])} chars")

    assert "bash" in exec_node.metadata["language"]
    assert "echo" in exec_node.metadata["code"]

    print("✓ Code blocks test passed!")
    print()


def test_react_flow_compatibility():
    """Test React Flow JSON compatibility."""
    print("Test 6: React Flow Compatibility")
    print("-" * 50)

    parser = MarkdownParser()
    content = """# Test
1. Step one
- If condition
  - Branch"""

    result = parser.parse(content)

    # Convert to dict (simulating JSON serialization)
    graph_dict = result.model_dump()

    print("Graph structure:")
    print(f"  nodes: {len(graph_dict['nodes'])} items")
    print(f"  edges: {len(graph_dict['edges'])} items")

    # Verify all nodes have required fields
    for node in graph_dict['nodes']:
        assert 'id' in node, "Node missing id"
        assert 'label' in node, "Node missing label"
        assert 'type' in node, "Node missing type"
        print(f"  ✓ Node {node['id']}: valid")

    # Verify all edges have required fields
    for edge in graph_dict['edges']:
        assert 'id' in edge, "Edge missing id"
        assert 'source' in edge, "Edge missing source"
        assert 'target' in edge, "Edge missing target"
        print(f"  ✓ Edge {edge['id']}: valid")

    print("✓ React Flow compatibility test passed!")
    print()


def test_incident_response_playbook():
    """Test with realistic incident response playbook."""
    print("Test 7: Incident Response Playbook")
    print("-" * 50)

    parser = MarkdownParser()
    content = """# Incident Response Playbook

## Initial Assessment

1. Receive alert notification
2. Verify alert legitimacy
3. Classify incident severity

- If severity is critical
  - Activate emergency response team
  - Notify management immediately

## Investigation

1. Gather system logs

```bash
grep ERROR /var/log/app.log | tail -100
```

2. Document findings

## Remediation

- When root cause is identified
  - Apply fix
  - Test solution

3. Update incident report"""

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
    assert len(result.nodes) > 10, "Should have substantial content"
    assert "phase" in type_counts, "Should have phases"
    assert "step" in type_counts, "Should have steps"
    assert "decision" in type_counts, "Should have decisions"
    assert "execute" in type_counts, "Should have execute nodes"

    # Verify graph connectivity
    node_ids = {n.id for n in result.nodes}
    for edge in result.edges:
        assert edge.source in node_ids, f"Invalid source: {edge.source}"
        assert edge.target in node_ids, f"Invalid target: {edge.target}"

    print("\n✓ Incident response playbook test passed!")
    print()


def main():
    """Run all tests."""
    print("=" * 50)
    print("Markdown Parser Test Suite")
    print("=" * 50)
    print()

    tests = [
        test_basic_parsing,
        test_headers,
        test_sequential_steps,
        test_decision_nodes,
        test_code_blocks,
        test_react_flow_compatibility,
        test_incident_response_playbook,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
