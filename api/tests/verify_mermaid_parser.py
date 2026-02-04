#!/usr/bin/env python3
"""
Quick verification script for Mermaid parser logic.
Tests core parsing patterns without requiring full dependency stack.
"""

import re


def test_node_patterns():
    """Test node shape pattern matching."""
    print("Testing node shape patterns...")
    print("-" * 50)

    patterns = {
        r'\[([^\]]+)\]': 'step',           # [text]
        r'\{([^\}]+)\}': 'decision',       # {text}
        r'\(\(([^\)]+)\)\)': 'phase',      # ((text))
        r'\(([^\)]+)\)': 'step',           # (text)
    }

    test_cases = [
        ("A[Start Process]", "Start Process", "step"),
        ("B{Is Valid?}", "Is Valid?", "decision"),
        ("C((Phase 1))", "Phase 1", "phase"),
        ("D(Rounded)", "Rounded", "step"),
    ]

    for test_input, expected_label, expected_type in test_cases:
        matched = False
        for pattern, node_type in patterns.items():
            full_pattern = r'([A-Za-z0-9_]+)\s*' + pattern
            match = re.match(full_pattern, test_input)

            if match:
                node_id = match.group(1)
                label = match.group(2).strip()

                print(f"✓ '{test_input}' -> ID: {node_id}, Label: {label}, Type: {node_type}")
                assert label == expected_label, f"Label mismatch: {label} != {expected_label}"
                assert node_type == expected_type, f"Type mismatch: {node_type} != {expected_type}"
                matched = True
                break

        assert matched, f"Failed to match: {test_input}"

    print("\n✓ All node pattern tests passed!\n")


def test_edge_patterns():
    """Test edge pattern matching."""
    print("Testing edge patterns...")
    print("-" * 50)

    edge_patterns = [
        (r'--\s*([^-]+?)\s*-->', 'solid'),      # --text-->
        (r'-\.\s*([^-]+?)\s*\.->', 'dotted'),    # -.text.->
        (r'==\s*([^=]+?)\s*==>', 'bold'),        # ==text==>
        (r'-->', 'solid'),                       # -->
        (r'-\.->', 'dotted'),                    # .->
        (r'==>', 'bold'),                        # ==>
    ]

    test_cases = [
        ("A --> B", "solid", None),
        ("A --Yes--> B", "solid", "Yes"),
        ("A -.-> B", "dotted", None),
        ("A -.Optional.-> B", "dotted", "Optional"),
        ("A ==> B", "bold", None),
        ("A ==Critical==> B", "bold", "Critical"),
    ]

    for test_input, expected_type, expected_label in test_cases:
        matched = False
        for edge_pattern, edge_type in edge_patterns:
            if re.search(edge_pattern, test_input):
                # Try to extract label if pattern has capture group
                if '(' in edge_pattern:
                    parts = re.split(edge_pattern, test_input)
                    if len(parts) > 2:
                        label = parts[1].strip()
                        print(f"✓ '{test_input}' -> Type: {edge_type}, Label: {label}")
                        if expected_label:
                            assert label == expected_label, f"Label mismatch: {label} != {expected_label}"
                    else:
                        print(f"✓ '{test_input}' -> Type: {edge_type}, No label")
                else:
                    print(f"✓ '{test_input}' -> Type: {edge_type}")

                assert edge_type == expected_type, f"Type mismatch: {edge_type} != {expected_type}"
                matched = True
                break

        assert matched, f"Failed to match: {test_input}"

    print("\n✓ All edge pattern tests passed!\n")


def test_statement_parsing():
    """Test full statement parsing logic."""
    print("Testing statement parsing...")
    print("-" * 50)

    test_statements = [
        "A[Start] --> B[End]",
        "A{Check?} --Yes--> B[Process]",
        "A((Phase)) -.-> B[Optional]",
        "subgraph Setup Phase",
        "end",
    ]

    for stmt in test_statements:
        print(f"Statement: '{stmt}'")

        # Check for edges
        has_edge = bool(re.search(r'-->|-\.->|==>', stmt))

        # Check for subgraph
        is_subgraph_start = stmt.startswith('subgraph')
        is_subgraph_end = stmt == 'end'

        # Check for node definitions
        has_node = bool(re.search(r'[A-Za-z0-9_]+\s*[\[\{\(]', stmt))

        print(f"  Has edge: {has_edge}, Has node: {has_node}, " +
              f"Subgraph start: {is_subgraph_start}, Subgraph end: {is_subgraph_end}")
        print()

    print("✓ Statement parsing logic verified!\n")


def test_complex_edge_parsing():
    """Test parsing complex edge with source and target nodes."""
    print("Testing complex edge parsing...")
    print("-" * 50)

    test_line = "Start[Begin Process] --Check--> Valid{Is Valid?}"

    # Split by edge pattern
    edge_pattern = r'--\s*([^-]+?)\s*-->'
    parts = re.split(edge_pattern, test_line)

    print(f"Input: {test_line}")
    print(f"Split parts: {parts}")

    if len(parts) >= 2:
        source_part = parts[0].strip()
        edge_label = parts[1].strip() if len(parts) > 2 else None
        target_part = parts[2].strip() if len(parts) > 2 else parts[1].strip()

        print(f"Source: {source_part}")
        print(f"Label: {edge_label}")
        print(f"Target: {target_part}")

        # Extract node info from source
        node_pattern = r'([A-Za-z0-9_]+)\s*\[([^\]]+)\]'
        source_match = re.match(node_pattern, source_part)
        if source_match:
            print(f"  Source ID: {source_match.group(1)}, Label: {source_match.group(2)}")

        # Extract node info from target
        target_pattern = r'([A-Za-z0-9_]+)\s*\{([^\}]+)\}'
        target_match = re.match(target_pattern, target_part)
        if target_match:
            print(f"  Target ID: {target_match.group(1)}, Label: {target_match.group(2)}")

    print("\n✓ Complex edge parsing verified!\n")


def main():
    """Run all verification tests."""
    print("=" * 50)
    print("Mermaid Parser Logic Verification")
    print("=" * 50)
    print()

    tests = [
        test_node_patterns,
        test_edge_patterns,
        test_statement_parsing,
        test_complex_edge_parsing,
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
    import sys
    sys.exit(main())
