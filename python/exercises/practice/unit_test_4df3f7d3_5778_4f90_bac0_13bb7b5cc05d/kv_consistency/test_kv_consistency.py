import unittest
from kv_consistency import resolve_conflicts

class TestKeyValueConsistency(unittest.TestCase):
    def test_dominance_simple(self):
        versions = [
            ("value1", {"node1": 1, "node2": 1}),
            ("value2", {"node1": 2, "node2": 1}),
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value2", {"node1": 2, "node2": 1})
        )

    def test_dominance_with_multiple_versions(self):
        versions = [
            ("value1", {"node1": 1, "node2": 1}),
            ("value2", {"node1": 2, "node2": 1}),
            ("value3", {"node1": 1, "node2": 0})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value2", {"node1": 2, "node2": 1})
        )

    def test_concurrent_versions(self):
        versions = [
            ("value1", {"node1": 2, "node2": 1}),
            ("value2", {"node1": 1, "node2": 2})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 2, "node2": 2})
        )

    def test_concurrent_lexicographically_ordering(self):
        versions = [
            ("zebra", {"node1": 2, "node2": 1}),
            ("apple", {"node1": 1, "node2": 2})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("apple", {"node1": 2, "node2": 2})
        )

    def test_multiple_concurrent_versions(self):
        versions = [
            ("value1", {"node1": 2, "node2": 1, "node3": 1}),
            ("value2", {"node1": 1, "node2": 2, "node3": 1}),
            ("value3", {"node1": 1, "node2": 1, "node3": 2})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 2, "node2": 2, "node3": 2})
        )

    def test_single_version(self):
        versions = [("value1", {"node1": 1, "node2": 1})]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 1, "node2": 1})
        )

    def test_vector_clocks_missing_nodes(self):
        versions = [
            ("value1", {"node1": 2}),
            ("value2", {"node2": 2})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 2, "node2": 2})
        )

    def test_dominance_with_extra_nodes(self):
        versions = [
            ("value1", {"node1": 1, "node2": 1}),
            ("value2", {"node1": 2, "node2": 2, "node3": 1})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value2", {"node1": 2, "node2": 2, "node3": 1})
        )

    def test_complex_scenario(self):
        versions = [
            ("value1", {"node1": 3, "node2": 2, "node3": 1}),
            ("value2", {"node1": 2, "node2": 3, "node3": 1}),
            ("value3", {"node1": 1, "node2": 1, "node3": 3}),
            ("value4", {"node1": 3, "node2": 3, "node3": 0})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 3, "node2": 3, "node3": 3})
        )

    def test_empty_vector_clock(self):
        versions = [
            ("value1", {}),
            ("value2", {"node1": 1})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value2", {"node1": 1})
        )

    def test_zero_counters(self):
        versions = [
            ("value1", {"node1": 0, "node2": 0}),
            ("value2", {"node1": 0, "node2": 0})
        ]
        self.assertEqual(
            resolve_conflicts(versions),
            ("value1", {"node1": 0, "node2": 0})
        )

    def test_large_number_of_versions(self):
        # Create a large number of versions
        versions = []
        for i in range(1000):
            versions.append((f"value{i}", {"node1": i % 10, "node2": (i+5) % 10}))
        
        # Add a dominant version
        versions.append(("dominant", {"node1": 10, "node2": 10}))
        
        self.assertEqual(
            resolve_conflicts(versions),
            ("dominant", {"node1": 10, "node2": 10})
        )

    def test_large_number_of_nodes(self):
        # Create versions with many nodes
        version1 = ("value1", {f"node{i}": i for i in range(1, 101)})
        version2 = ("value2", {f"node{i}": i+1 for i in range(1, 101)})
        
        self.assertEqual(
            resolve_conflicts([version1, version2]),
            ("value2", {f"node{i}": i+1 for i in range(1, 101)})
        )

if __name__ == "__main__":
    unittest.main()