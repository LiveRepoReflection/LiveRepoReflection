import unittest
from network_route import min_average_latency

class NetworkRouteTest(unittest.TestCase):
    def test_single_edge_single_packet(self):
        # Graph: two nodes with a single edge between them.
        n = 2
        m = 1
        edges = [(0, 1, 10)]
        k = 1
        packets = [(0, 1)]
        # Only one possible route with latency 10.
        expected = 10.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

    def test_single_path_multiple_packets(self):
        # Graph: a linear chain of 5 nodes.
        n = 5
        m = 4
        # Only one path exists from 0 to 4 (0-1-2-3-4) with latency = 5+5+5+5 = 20.
        edges = [(0, 1, 5), (1, 2, 5), (2, 3, 5), (3, 4, 5)]
        # Two packets: one from 0 to 4 and one from 4 to 0.
        k = 2
        packets = [(0, 4), (4, 0)]
        expected = 20.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

    def test_diamond_graph_single_packet(self):
        # Diamond shaped graph with alternative routes.
        n = 4
        m = 5
        edges = [
            (0, 1, 1),
            (1, 3, 1),
            (0, 2, 1),
            (2, 3, 2),
            (1, 2, 2)
        ]
        k = 1
        packets = [(0, 3)]
        # The best path is 0 -> 1 -> 3 with total latency 1+1=2.
        expected = 2.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

    def test_provided_example(self):
        # Provided sample example from the problem description.
        n = 4
        m = 4
        edges = [(0, 1, 10), (1, 2, 10), (0, 3, 1), (3, 2, 10)]
        k = 2
        packets = [(0, 2), (1, 3)]
        # For packet (0,2): Best route is 0->3->2 : 1 + 10 = 11.
        # For packet (1,3): Best route is 1->0->3 : 10 + 1 = 11.
        # If congestion does not alter the route choice then average = 11.
        expected = 11.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

    def test_multiple_packets_shared_route(self):
        # Graph where multiple packets share a route and have an unambiguous best path.
        n = 3
        m = 3
        edges = [(0, 1, 100), (1, 2, 100), (0, 2, 300)]
        # Three packets, all from 0 to 2.
        k = 3
        packets = [(0, 2), (0, 2), (0, 2)]
        # Best path for each is 0->1->2 with total latency 200.
        expected = 200.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

    def test_no_packets(self):
        # Edge Case: Zero packets. Expected average latency is 0.
        n = 5
        m = 4
        edges = [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2)]
        k = 0
        packets = []
        expected = 0.0
        result = min_average_latency(n, m, edges, k, packets)
        self.assertAlmostEqual(result, expected, places=6)

if __name__ == '__main__':
    unittest.main()