import unittest
from adaptive_routing import AdaptiveRouter

class TestAdaptiveRouter(unittest.TestCase):
    def test_basic_routing(self):
        # Test case from the example
        router = AdaptiveRouter(5, [(0, 1, 2), (1, 2, 3), (2, 3, 1), (3, 4, 4)])
        self.assertEqual(router.route(0, 4), 10)
        router.edge_update(1, 2, 5)
        self.assertEqual(router.route(0, 4), 12)
        router.node_failure(2)
        self.assertEqual(router.route(0, 4), -1)
        router.edge_update(1, 3, -1)
        self.assertEqual(router.route(0, 4), -1)

    def test_empty_graph(self):
        router = AdaptiveRouter(2, [])
        self.assertEqual(router.route(0, 1), -1)

    def test_single_edge(self):
        router = AdaptiveRouter(2, [(0, 1, 5)])
        self.assertEqual(router.route(0, 1), 5)
        router.edge_update(0, 1, -1)
        self.assertEqual(router.route(0, 1), -1)

    def test_multiple_paths(self):
        # Test graph with multiple possible paths
        router = AdaptiveRouter(4, [(0, 1, 1), (1, 3, 4), (0, 2, 2), (2, 3, 2)])
        self.assertEqual(router.route(0, 3), 4)  # Should choose path 0->2->3
        router.edge_update(2, 3, 5)
        self.assertEqual(router.route(0, 3), 5)  # Should choose path 0->1->3

    def test_node_failures(self):
        router = AdaptiveRouter(5, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)])
        self.assertEqual(router.route(0, 4), 4)
        router.node_failure(2)
        self.assertEqual(router.route(0, 4), -1)
        router.edge_update(1, 3, 1)  # Add bypass edge
        self.assertEqual(router.route(0, 4), 3)

    def test_edge_updates(self):
        router = AdaptiveRouter(3, [(0, 1, 5), (1, 2, 5)])
        self.assertEqual(router.route(0, 2), 10)
        router.edge_update(0, 2, 8)  # Add direct edge
        self.assertEqual(router.route(0, 2), 8)
        router.edge_update(0, 2, 12)  # Update direct edge
        self.assertEqual(router.route(0, 2), 10)  # Should use original path

    def test_large_network(self):
        # Test with maximum constraints
        edges = [(i, i+1, 1) for i in range(99999)]
        router = AdaptiveRouter(100000, edges)
        self.assertEqual(router.route(0, 99999), 99999)
        router.node_failure(50000)
        self.assertEqual(router.route(0, 99999), -1)

    def test_isolated_nodes(self):
        router = AdaptiveRouter(5, [(0, 1, 1), (2, 3, 1)])
        self.assertEqual(router.route(0, 2), -1)
        self.assertEqual(router.route(0, 4), -1)
        self.assertEqual(router.route(2, 3), 1)

    def test_cycle_handling(self):
        router = AdaptiveRouter(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)])
        self.assertEqual(router.route(0, 2), 2)
        router.edge_update(0, 2, 1)  # Add shortcut
        self.assertEqual(router.route(0, 2), 1)

    def test_edge_weight_limits(self):
        router = AdaptiveRouter(3, [(0, 1, 1000), (1, 2, 1000)])
        self.assertEqual(router.route(0, 2), 2000)
        router.edge_update(0, 1, -1)
        self.assertEqual(router.route(0, 2), -1)

if __name__ == '__main__':
    unittest.main()