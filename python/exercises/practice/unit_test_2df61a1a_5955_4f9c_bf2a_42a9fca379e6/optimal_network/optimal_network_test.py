import unittest
from optimal_network import optimal_network

class OptimalNetworkTest(unittest.TestCase):
    def test_triangle_network_valid(self):
        # Triangle network (3 nodes, complete cycle)
        # Edges: (0,1)=10 cost, (1,2)=15 cost, (2,0)=20 cost with failure probability 0.2 each.
        # Total cost = 10 + 15 + 20 = 45 and product = 0.2^3 = 0.008 which is <= threshold 0.01.
        n = 3
        links = [
            (0, 1, 10, 0.2),
            (1, 2, 15, 0.2),
            (2, 0, 20, 0.2)
        ]
        m = len(links)
        P = 0.01
        self.assertEqual(optimal_network(n, m, links, P), 45)

    def test_chain_network_non_resilient(self):
        # Chain network: 4 nodes, but not 2-vertex-connected.
        # Removing node 1 disconnects the network.
        n = 4
        links = [
            (0, 1, 10, 0.1),
            (1, 2, 20, 0.1),
            (2, 3, 30, 0.1)
        ]
        m = len(links)
        P = 0.1
        self.assertEqual(optimal_network(n, m, links, P), -1)

    def test_square_cycle_network(self):
        # Square cycle: 4 nodes in a cycle. Resilient because removal of any node still leaves an edge.
        # Total cost = 5 + 5 + 5 + 5 = 20, failure probability product = 0.3^4 = 0.0081 <= 0.1.
        n = 4
        links = [
            (0, 1, 5, 0.3),
            (1, 2, 5, 0.3),
            (2, 3, 5, 0.3),
            (3, 0, 5, 0.3)
        ]
        m = len(links)
        P = 0.1
        self.assertEqual(optimal_network(n, m, links, P), 20)

    def test_complete_graph_multiple_choices(self):
        # Complete graph on 4 nodes with 6 possible edges.
        # One valid cycle covering all nodes is: (0,1), (1,2), (2,3), (3,0)
        # Total cost = 10 + 25 + 35 + 20 = 90 with product = 0.1^4 = 0.0001 <= threshold (0.001).
        n = 4
        links = [
            (0, 1, 10, 0.1),
            (0, 2, 15, 0.1),
            (0, 3, 20, 0.1),
            (1, 2, 25, 0.1),
            (1, 3, 30, 0.1),
            (2, 3, 35, 0.1)
        ]
        m = len(links)
        P = 0.001
        self.assertEqual(optimal_network(n, m, links, P), 90)

    def test_unattainable_failure_probability(self):
        # Triangle network but with high failure probabilities that cannot meet the threshold.
        # Each edge failure probability is 0.9 so product = 0.9^3 = 0.729 which exceeds threshold 0.5.
        n = 3
        links = [
            (0, 1, 10, 0.9),
            (1, 2, 10, 0.9),
            (2, 0, 10, 0.9)
        ]
        m = len(links)
        P = 0.5
        # No valid resilient network can satisfy the failure probability constraint.
        self.assertEqual(optimal_network(n, m, links, P), -1)

    def test_no_possible_network_due_to_insufficient_links(self):
        # When there are no links, no network is possible.
        n = 4
        links = []
        m = len(links)
        P = 0.5
        self.assertEqual(optimal_network(n, m, links, P), -1)

    def test_resilient_network_with_extra_edges(self):
        # A network with extra edges available; the algorithm must choose the optimal subset.
        # Graph: 5 nodes, several possible edges.
        # One optimal resilient network might be to select a cycle covering all nodes.
        n = 5
        links = [
            (0, 1, 12, 0.2),
            (1, 2, 15, 0.2),
            (2, 3, 10, 0.2),
            (3, 4, 20, 0.2),
            (4, 0, 18, 0.2),
            (0, 2, 50, 0.05),
            (1, 3, 30, 0.05),
            (2, 4, 25, 0.05)
        ]
        m = len(links)
        # Cycle: (0,1), (1,2), (2,3), (3,4), (4,0)
        # Total cost = 12 + 15 + 10 + 20 + 18 = 75
        # Failure probability product = 0.2^5 = 0.00032 which is <= 0.01.
        P = 0.01
        self.assertEqual(optimal_network(n, m, links, P), 75)

if __name__ == '__main__':
    unittest.main()