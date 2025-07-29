import unittest
from network_influence import calculate_influence_score

class DummyNetwork:
    def __init__(self, graph):
        self.graph = graph
        self.call_counts = {}

    def get_connections(self, user_id):
        self.call_counts[user_id] = self.call_counts.get(user_id, 0) + 1
        # Return the list as defined in the graph, or an empty list if not present.
        return self.graph.get(user_id, [])

class NetworkInfluenceTest(unittest.TestCase):
    def test_single_user_no_connections(self):
        # Single user with no connections should have an influence score of 0.
        graph = {1: []}
        dummy_network = DummyNetwork(graph)
        result = calculate_influence_score(1, 1, dummy_network.get_connections)
        self.assertEqual(result, 0)

    def test_two_users_direct_connection(self):
        # Two users with a direct connection.
        graph = {1: [2], 2: [1]}
        dummy_network = DummyNetwork(graph)
        result = calculate_influence_score(1, 2, dummy_network.get_connections)
        # Distance from 1 to 2 is 1 hop => reachability = 1/(1+1) = 0.5.
        self.assertAlmostEqual(result, 0.5)

    def test_star_graph(self):
        # Central user connected to several leaves.
        graph = {
            1: [2, 3, 4, 5, 6],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: [1]
        }
        dummy_network = DummyNetwork(graph)
        result = calculate_influence_score(1, 6, dummy_network.get_connections)
        # Each direct connection contributes 1/2; total should be 5 * 1/2.
        self.assertAlmostEqual(result, 5 * 0.5)

    def test_cycle_and_duplicates(self):
        # Graph with cycle, duplicate connections and self-loops.
        graph = {
            1: [2, 2, 1],
            2: [1, 3, 3],
            3: [2, 1]
        }
        dummy_network = DummyNetwork(graph)
        result = calculate_influence_score(1, 3, dummy_network.get_connections)
        # Expected distances:
        # 1 to 2: 1 hop => 1/2,
        # 1 to 3: 2 hops via 2 (even with duplicates, minimal path is 1->2->3) => 1/3.
        self.assertAlmostEqual(result, 1/2 + 1/3)

    def test_disconnected_components(self):
        # Graph with two disconnected components.
        graph = {
            1: [2],
            2: [1],
            3: [4],
            4: [3]
        }
        dummy_network = DummyNetwork(graph)
        result = calculate_influence_score(1, 4, dummy_network.get_connections)
        # Only node 2 is reachable from node 1 with distance 1 => reachability = 1/2.
        self.assertAlmostEqual(result, 1/2)

    def test_estimate_n_mismatch(self):
        # Graph with user ids outside the typical range.
        graph = {
            100: [200],
            200: [100, 300],
            300: [200]
        }
        dummy_network = DummyNetwork(graph)
        # For user 100, reachable nodes are:
        # 200 at distance 1 => 1/2,
        # 300 at distance 2 => 1/3.
        result = calculate_influence_score(100, 2, dummy_network.get_connections)
        self.assertAlmostEqual(result, 1/2 + 1/3)

    def test_linear_chain(self):
        # Create a linear chain graph: 1-2-3-...-10, including duplicate entries and self-loops.
        graph = {}
        for i in range(1, 11):
            neighbors = []
            if i > 1:
                neighbors.append(i - 1)
            if i < 10:
                neighbors.append(i + 1)
            # Add self-loops and duplicates
            neighbors.append(i)
            neighbors += [i]
            graph[i] = neighbors
        dummy_network = DummyNetwork(graph)
        # For user 1, distances to others: 2->1 hop, 3->2 hops, ... 10->9 hops.
        expected = sum(1 / (distance + 1) for distance in range(1, 10))
        result = calculate_influence_score(1, 10, dummy_network.get_connections)
        self.assertAlmostEqual(result, expected)

if __name__ == '__main__':
    unittest.main()