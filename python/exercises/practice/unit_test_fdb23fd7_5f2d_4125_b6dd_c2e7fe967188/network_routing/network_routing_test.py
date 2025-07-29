import unittest
from network_routing.network_routing import optimize_routes

class TestNetworkRouting(unittest.TestCase):
    def setUp(self):
        # Helper to verify if a given path is valid in the graph
        # Considering bidirectional edges.
        self.maxDiff = None

    def is_valid_path(self, path, source, destination, allowed_edges):
        if path is None:
            return False
        if path[0] != source or path[-1] != destination:
            return False
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if (u, v) not in allowed_edges and (v, u) not in allowed_edges:
                return False
        return True

    def create_allowed_edges_set(self, edges):
        # create a set of tuples for allowed connections (bidirectional)
        allowed = set()
        for u, v, cost in edges:
            allowed.add((u, v))
            allowed.add((v, u))
        return allowed

    def test_single_packet_simple(self):
        n = 4
        edges = [
            (0, 1, 1.0),
            (1, 2, 1.0),
            (2, 3, 1.0)
        ]
        packets = [
            (0, 3, 100)
        ]
        result = optimize_routes(n, edges, packets)
        self.assertEqual(len(result), 1)
        allowed_edges = self.create_allowed_edges_set(edges)
        self.assertTrue(self.is_valid_path(result[0], 0, 3, allowed_edges))

    def test_no_path(self):
        n = 3
        edges = [
            (0, 1, 1.0)
        ]
        packets = [
            (1, 2, 50)
        ]
        result = optimize_routes(n, edges, packets)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0])

    def test_multiple_edges(self):
        n = 3
        edges = [
            (0, 1, 2.0),
            (0, 1, 1.0),
            (1, 2, 3.0)
        ]
        packets = [
            (0, 2, 100)
        ]
        result = optimize_routes(n, edges, packets)
        self.assertEqual(len(result), 1)
        allowed_edges = self.create_allowed_edges_set(edges)
        self.assertTrue(self.is_valid_path(result[0], 0, 2, allowed_edges))

    def test_multiple_packets(self):
        n = 5
        edges = [
            (0, 1, 1.0),
            (0, 2, 2.0),
            (1, 2, 0.5),
            (1, 3, 3.0),
            (2, 3, 1.5),
            (3, 4, 0.8)
        ]
        packets = [
            (0, 4, 100),
            (1, 4, 200),
            (0, 3, 50)
        ]
        result = optimize_routes(n, edges, packets)
        self.assertEqual(len(result), 3)
        allowed_edges = self.create_allowed_edges_set(edges)
        expected_endpoints = [(0, 4), (1, 4), (0, 3)]
        for route, (src, dst) in zip(result, expected_endpoints):
            self.assertIsNotNone(route)
            self.assertTrue(self.is_valid_path(route, src, dst, allowed_edges))

    def test_congestion_scenario(self):
        # In this scenario, there are two distinct routes from 0 to 3.
        # The network may try to distribute the packets to reduce the final cost.
        n = 4
        edges = [
            (0, 1, 1.0),
            (1, 3, 1.0),
            (0, 2, 1.1),
            (2, 3, 1.0)
        ]
        # Two packets from 0 to 3. Optimal routing might split them over different paths.
        packets = [
            (0, 3, 50),
            (0, 3, 50)
        ]
        result = optimize_routes(n, edges, packets)
        self.assertEqual(len(result), 2)
        allowed_edges = self.create_allowed_edges_set(edges)
        for route in result:
            self.assertIsNotNone(route)
            self.assertTrue(self.is_valid_path(route, 0, 3, allowed_edges))
        # Optionally, check if both routes are not identical if possible.
        if result[0] == result[1]:
            # It is acceptable for both routes to be identical if optimal,
            # but if they are different, then they should reflect different routing choices.
            self.assertEqual(result[0][0], 0)
            self.assertEqual(result[0][-1], 3)
        else:
            self.assertNotEqual(result[0], result[1])

if __name__ == '__main__':
    unittest.main()