import unittest
from trust_route import find_shortest_trust_path


class MockNetwork:
    """Mock network for testing find_shortest_trust_path function."""

    def __init__(self, network_structure):
        self.network_structure = network_structure
        self.query_count = 0

    def get_trusted_users(self, user_id):
        self.query_count += 1
        return self.network_structure.get(user_id, [])


class TrustRouteTest(unittest.TestCase):

    def test_direct_path(self):
        """Test when there is a direct trust relationship."""
        network = MockNetwork({
            "A": ["B"],
            "B": []
        })
        result = find_shortest_trust_path("A", "B", network.get_trusted_users)
        self.assertEqual(result, ["A", "B"])
        self.assertLessEqual(network.query_count, 2)

    def test_two_hop_path(self):
        """Test when the path requires two hops."""
        network = MockNetwork({
            "A": ["B"],
            "B": ["C"],
            "C": []
        })
        result = find_shortest_trust_path("A", "C", network.get_trusted_users)
        self.assertEqual(result, ["A", "B", "C"])
        self.assertLessEqual(network.query_count, 3)

    def test_multiple_paths_should_return_shortest(self):
        """Test that the shortest path is returned when multiple paths exist."""
        network = MockNetwork({
            "A": ["B", "X"],
            "B": ["C"],
            "C": ["D"],
            "X": ["Y"],
            "Y": ["Z"],
            "Z": ["D"]
        })
        result = find_shortest_trust_path("A", "D", network.get_trusted_users)
        self.assertEqual(result, ["A", "B", "C", "D"])
        # Not checking query count here as optimizations may vary

    def test_no_path_exists(self):
        """Test when no path exists between the two users."""
        network = MockNetwork({
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": [],
            "E": []
        })
        result = find_shortest_trust_path("A", "Z", network.get_trusted_users)
        self.assertEqual(result, [])

    def test_start_and_target_are_same(self):
        """Test when the start and target users are the same."""
        network = MockNetwork({
            "A": ["B"]
        })
        result = find_shortest_trust_path("A", "A", network.get_trusted_users)
        self.assertEqual(result, ["A"])
        self.assertEqual(network.query_count, 0)  # No need to query when start = target

    def test_cyclic_network(self):
        """Test handling of cycles in the trust network."""
        network = MockNetwork({
            "A": ["B"],
            "B": ["C"],
            "C": ["A", "D"],
            "D": []
        })
        result = find_shortest_trust_path("A", "D", network.get_trusted_users)
        self.assertEqual(result, ["A", "B", "C", "D"])
        # Not checking query count as it depends on implementation

    def test_complex_network(self):
        """Test with a more complex network structure."""
        network = MockNetwork({
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["F"],
            "D": ["G"],
            "E": [],
            "F": [],
            "G": []
        })
        result = find_shortest_trust_path("A", "G", network.get_trusted_users)
        self.assertEqual(result, ["A", "B", "D", "G"])

    def test_large_branching_network(self):
        """Test performance with a large branching network."""
        # Create a network where A connects to 100 users, and only one path leads to Z
        network_structure = {"A": [f"B{i}" for i in range(100)]}
        # Only B99 leads to Z
        for i in range(99):
            network_structure[f"B{i}"] = []
        network_structure["B99"] = ["Z"]
        network_structure["Z"] = []
        
        network = MockNetwork(network_structure)
        result = find_shortest_trust_path("A", "Z", network.get_trusted_users)
        self.assertEqual(result, ["A", "B99", "Z"])
        # Ensure we're not making unnecessary queries
        self.assertLessEqual(network.query_count, 101)  # Worst case is querying A and all B's

    def test_optimization_with_redundant_paths(self):
        """Test that the implementation is optimized and doesn't explore unnecessary paths."""
        # Create a network where many redundant paths exist
        network = MockNetwork({
            "A": ["B", "C", "D"],
            "B": ["E"],
            "C": ["E"],
            "D": ["E"],
            "E": ["F"],
            "F": []
        })
        result = find_shortest_trust_path("A", "F", network.get_trusted_users)
        self.assertEqual(result, ["A", "B", "E", "F"])  # Any path through B, C, or D is valid
        # Since we're using BFS, we should not query more than necessary
        self.assertLessEqual(network.query_count, 6)  # A, B, C, D, E, F at most

    def test_empty_trusted_list(self):
        """Test when a user doesn't trust anyone."""
        network = MockNetwork({
            "A": [],
            "B": ["C"],
            "C": []
        })
        result = find_shortest_trust_path("A", "C", network.get_trusted_users)
        self.assertEqual(result, [])  # No path possible
        self.assertEqual(network.query_count, 1)  # Only need to query A

    def test_disconnected_components(self):
        """Test with disconnected components in the network."""
        network = MockNetwork({
            "A": ["B"],
            "B": ["C"],
            "C": [],
            "X": ["Y"],
            "Y": ["Z"],
            "Z": []
        })
        result = find_shortest_trust_path("A", "Z", network.get_trusted_users)
        self.assertEqual(result, [])  # No path possible
        # Cannot check query count here, as it depends on the search strategy


if __name__ == '__main__':
    unittest.main()