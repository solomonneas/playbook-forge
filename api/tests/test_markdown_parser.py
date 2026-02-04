"""
Unit Tests for Markdown Parser

Tests the markdown-to-flowchart parsing functionality with various playbook formats.
"""

import pytest
from api.parsers.markdown_parser import MarkdownParser
from api.models import PlaybookGraph, PlaybookNode, PlaybookEdge


class TestMarkdownParser:
    """Test suite for MarkdownParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownParser()

    def test_empty_content(self):
        """Test parsing empty content."""
        result = self.parser.parse("")
        assert isinstance(result, PlaybookGraph)
        assert len(result.nodes) == 0
        assert len(result.edges) == 0

    def test_single_h1_header(self):
        """Test parsing a single H1 header as phase node."""
        content = "# Deployment Phase"
        result = self.parser.parse(content)

        assert len(result.nodes) == 1
        assert result.nodes[0].type == "phase"
        assert result.nodes[0].label == "Deployment Phase"
        assert result.nodes[0].metadata["level"] == 1
        assert result.nodes[0].metadata["header_type"] == "h1"

    def test_h1_and_h2_headers(self):
        """Test parsing H1 and H2 headers with connection."""
        content = """# Main Phase
## Sub Phase"""
        result = self.parser.parse(content)

        assert len(result.nodes) == 2
        assert result.nodes[0].type == "phase"
        assert result.nodes[0].label == "Main Phase"
        assert result.nodes[1].type == "phase"
        assert result.nodes[1].label == "Sub Phase"

        # Should have one edge connecting them
        assert len(result.edges) == 1
        assert result.edges[0].source == result.nodes[0].id
        assert result.edges[0].target == result.nodes[1].id

    def test_numbered_list_sequential_steps(self):
        """Test parsing numbered list as sequential steps."""
        content = """1. Install dependencies
2. Configure environment
3. Run tests"""
        result = self.parser.parse(content)

        assert len(result.nodes) == 3
        for node in result.nodes:
            assert node.type == "step"
            assert node.metadata["step_type"] == "sequential"

        assert result.nodes[0].label == "Install dependencies"
        assert result.nodes[1].label == "Configure environment"
        assert result.nodes[2].label == "Run tests"

        # Should have edges connecting sequential steps
        assert len(result.edges) == 2
        assert result.edges[0].source == result.nodes[0].id
        assert result.edges[0].target == result.nodes[1].id

    def test_bullet_point_without_decision(self):
        """Test parsing regular bullet points as steps."""
        content = """- Check system requirements
- Verify credentials"""
        result = self.parser.parse(content)

        assert len(result.nodes) == 2
        for node in result.nodes:
            assert node.type == "step"
            assert node.metadata["step_type"] == "bullet"

    def test_decision_node_with_if(self):
        """Test parsing bullet point with 'if' as decision node."""
        content = """- If authentication succeeds
  - Continue to dashboard
  - Load user data"""
        result = self.parser.parse(content)

        # Should have: decision node, 2 branch nodes, merge node
        assert len(result.nodes) == 4

        decision_node = result.nodes[0]
        assert decision_node.type == "decision"
        assert "Authentication succeeds?" in decision_node.label

        # Check branches
        branch_nodes = [n for n in result.nodes if n.metadata and n.metadata.get("branch")]
        assert len(branch_nodes) == 2

        # Check merge node
        merge_nodes = [n for n in result.nodes if n.type == "merge"]
        assert len(merge_nodes) == 1

    def test_decision_node_with_when(self):
        """Test parsing bullet point with 'when' as decision node."""
        content = """- When deployment is complete
  - Notify team
  - Update documentation"""
        result = self.parser.parse(content)

        decision_node = result.nodes[0]
        assert decision_node.type == "decision"
        assert "Deployment is complete?" in decision_node.label

    def test_code_block_as_execute_node(self):
        """Test parsing code block as execute node."""
        content = """```bash
npm install
npm run build
```"""
        result = self.parser.parse(content)

        assert len(result.nodes) == 1
        execute_node = result.nodes[0]
        assert execute_node.type == "execute"
        assert "bash" in execute_node.label.lower()
        assert execute_node.metadata["language"] == "bash"
        assert "npm install" in execute_node.metadata["code"]
        assert "npm run build" in execute_node.metadata["code"]

    def test_code_block_without_language(self):
        """Test parsing code block without language specification."""
        content = """```
echo "Hello"
```"""
        result = self.parser.parse(content)

        assert len(result.nodes) == 1
        assert result.nodes[0].type == "execute"
        assert result.nodes[0].metadata["language"] == ""

    def test_complete_playbook(self):
        """Test parsing a complete playbook with multiple element types."""
        content = """# CI/CD Pipeline

## Build Phase

1. Clone repository
2. Install dependencies

```bash
npm install
```

3. Run linter

## Test Phase

- If tests pass
  - Deploy to staging
  - Run smoke tests
- Otherwise
  - Notify developers
  - Halt deployment

## Deployment

- When staging is validated
  - Deploy to production
  - Monitor metrics"""

        result = self.parser.parse(content)

        # Verify we have various node types
        node_types = {node.type for node in result.nodes}
        assert "phase" in node_types
        assert "step" in node_types
        assert "execute" in node_types
        assert "decision" in node_types
        assert "merge" in node_types

        # Verify nodes are connected
        assert len(result.edges) > 0

        # Verify all nodes have valid IDs
        node_ids = {node.id for node in result.nodes}
        assert len(node_ids) == len(result.nodes)  # All IDs unique

        # Verify all edges reference existing nodes
        for edge in result.edges:
            assert edge.source in node_ids
            assert edge.target in node_ids

    def test_mixed_markdown_formatting(self):
        """Test parsing with mixed formatting and empty lines."""
        content = """
# Phase 1

Some text that isn't parsed.

1. First step

2. Second step

- Regular bullet

- If condition met
  - Branch action

```python
print("code")
```

# Phase 2
"""
        result = self.parser.parse(content)

        # Should parse headers, numbered items, bullets, and code
        assert len(result.nodes) > 0

        phase_nodes = [n for n in result.nodes if n.type == "phase"]
        assert len(phase_nodes) == 2

    def test_complex_decision_with_else(self):
        """Test parsing decision with else branch."""
        content = """- If database connection succeeds
  - Initialize schema
- Else
  - Log error
  - Exit"""

        result = self.parser.parse(content)

        decision_nodes = [n for n in result.nodes if n.type == "decision"]
        assert len(decision_nodes) == 1

        # Should have branches
        branch_nodes = [n for n in result.nodes if n.metadata and n.metadata.get("branch")]
        assert len(branch_nodes) >= 2

    def test_node_edge_consistency(self):
        """Test that all edges point to valid nodes."""
        content = """# Start
1. Step one
2. Step two
- If check
  - Action A
  - Action B
```bash
echo done
```"""

        result = self.parser.parse(content)

        node_ids = {node.id for node in result.nodes}

        for edge in result.edges:
            assert edge.source in node_ids, f"Edge source {edge.source} not in nodes"
            assert edge.target in node_ids, f"Edge target {edge.target} not in nodes"
            assert edge.id is not None
            assert edge.id != ""

    def test_sequential_parsing(self):
        """Test that sequential steps are properly connected."""
        content = """1. First
2. Second
3. Third"""

        result = self.parser.parse(content)

        assert len(result.nodes) == 3
        assert len(result.edges) == 2

        # Verify chain: node0 -> node1 -> node2
        assert result.edges[0].source == result.nodes[0].id
        assert result.edges[0].target == result.nodes[1].id
        assert result.edges[1].source == result.nodes[1].id
        assert result.edges[1].target == result.nodes[2].id

    def test_decision_branch_labels(self):
        """Test that decision branches have proper labels."""
        content = """- If user is authenticated
  - Load profile
  - Show dashboard"""

        result = self.parser.parse(content)

        # Find edges from decision node
        decision_node = next(n for n in result.nodes if n.type == "decision")
        decision_edges = [e for e in result.edges if e.source == decision_node.id]

        # Should have yes/no labels
        labels = {e.label for e in decision_edges if e.label}
        assert "yes" in labels or "no" in labels

    def test_multiple_code_blocks(self):
        """Test parsing multiple code blocks."""
        content = """```bash
npm install
```

Some text.

```python
print("test")
```"""

        result = self.parser.parse(content)

        execute_nodes = [n for n in result.nodes if n.type == "execute"]
        assert len(execute_nodes) == 2

        # Verify they're connected
        assert len(result.edges) == 1

    def test_sample_incident_response_playbook(self):
        """Test with a realistic incident response playbook."""
        content = """# Incident Response Playbook

## Initial Assessment

1. Receive alert notification
2. Verify alert legitimacy
3. Classify incident severity

- If severity is critical
  - Activate emergency response team
  - Notify management immediately
- Else
  - Assign to on-call engineer
  - Monitor progress

## Investigation

1. Gather system logs
2. Identify affected systems

```bash
grep ERROR /var/log/app.log | tail -100
```

3. Document findings

## Remediation

- When root cause is identified
  - Apply fix
  - Test solution
- Otherwise
  - Escalate to senior engineer

## Post-Incident

1. Update incident report
2. Schedule post-mortem
3. Update runbooks"""

        result = self.parser.parse(content)

        # Verify comprehensive parsing
        assert len(result.nodes) > 10
        assert len(result.edges) > 5

        # Check for all expected node types
        types_present = {n.type for n in result.nodes}
        assert "phase" in types_present
        assert "step" in types_present
        assert "decision" in types_present
        assert "execute" in types_present

        # Verify React Flow compatibility (all required fields present)
        for node in result.nodes:
            assert hasattr(node, 'id')
            assert hasattr(node, 'label')
            assert hasattr(node, 'type')
            assert node.id is not None
            assert node.label is not None

        for edge in result.edges:
            assert hasattr(edge, 'id')
            assert hasattr(edge, 'source')
            assert hasattr(edge, 'target')
            assert edge.id is not None
            assert edge.source is not None
            assert edge.target is not None


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
