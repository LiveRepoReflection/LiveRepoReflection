import unittest
from streaming_graph import process_operations

class TestStreamingGraphAnalytics(unittest.TestCase):

    def test_simple_chain(self):
        # Test a simple chain of adds with one query.
        operations = [
            "add 0 1",
            "add 1 2",
            "query"
        ]
        expected = [3]
        result = process_operations(operations)
        self.assertEqual(result, expected)

    def test_multiple_components(self):
        # Test with two separate components and one query.
        operations = [
            "add 0 1",
            "add 2 3",
            "query"
        ]
        # Components: {0,1} and {2,3} => largest size = 2.
        expected = [2]
        result = process_operations(operations)
        self.assertEqual(result, expected)

    def test_complex_sequence(self):
        # A sequence of operations merging and splitting components.
        operations = [
            "add 1 2",    # Component A: {1,2}
            "add 2 3",    # Component A: {1,2,3}
            "add 4 5",    # Component B: {4,5}
            "query",      # Largest component = 3 (Component A)
            "remove 2 3", # Now Component A splits: {1,2} and {3}
            "query",      # Largest component = 2 (from {1,2} or {4,5})
            "add 3 4",    # Merge: {3,4,5} as Component B remains, Component A remains {1,2}
            "query",      # Largest remains = 3 (components of sizes 2 and 3)
            "add 0 6",    # New Component C: {0,6}
            "add 6 7",    # Component C becomes: {0,6,7}
            "query",      # Largest is max(3,3,?) = 3
            "add 1 6",    # Merge Component A {1,2} with Component C {0,6,7} -> {0,1,2,6,7}
            "query"       # Largest now becomes size 5 from merged component.
        ]
        expected = [3, 2, 3, 3, 5]
        result = process_operations(operations)
        self.assertEqual(result, expected)

    def test_duplicate_and_invalid_removals(self):
        # Test duplicate add operations and removals that should have no effect.
        operations = [
            "add 10 20",
            "add 10 20",  # Duplicate add should not change structure.
            "query",      # Component {10,20} -> size 2
            "remove 10 20",
            "query",      # Now 10 and 20 are isolated: largest size = 1.
            "remove 10 20", # Removing non-existent edge; should be ignored.
            "query"       # No change: largest size = 1.
        ]
        expected = [2, 1, 1]
        result = process_operations(operations)
        self.assertEqual(result, expected)

    def test_no_operations(self):
        # When there are no 'query' operations the result should be an empty list.
        operations = [
            "add 0 1",
            "add 1 2",
            "remove 0 1"
        ]
        expected = []
        result = process_operations(operations)
        self.assertEqual(result, expected)

    def test_multiple_queries(self):
        # Test a series of queries throughout the operations.
        operations = [
            "query",
            "add 5 6",
            "query",
            "add 6 7",
            "query",
            "remove 5 6",
            "query",
            "remove 6 7",
            "query"
        ]
        # Explanation:
        # First query: empty graph -> largest component is 0.
        # After "add 5 6": component {5,6} -> size 2.
        # After "add 6 7": component {5,6,7} -> size 3.
        # After "remove 5 6": remaining component becomes {6,7} -> size 2, and node 5 isolated.
        # After "remove 6 7": nodes 5,6,7 all isolated, max component size = 1.
        expected = [0, 2, 3, 2, 1]
        result = process_operations(operations)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()