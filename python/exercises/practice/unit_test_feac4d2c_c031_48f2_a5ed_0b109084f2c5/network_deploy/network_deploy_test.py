import unittest
from network_deploy import optimal_router_placement

class TestNetworkDeploy(unittest.TestCase):
    def test_single_node_single_router(self):
        nodes = [(0, 0)]
        k = 1
        expected = [(0, 0)]
        result = optimal_router_placement(nodes, k)
        self.assertEqual(result, expected)

    def test_two_nodes_one_router(self):
        nodes = [(0, 0), (1, 1)]
        k = 1
        result = optimal_router_placement(nodes, k)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0] in [(0, 0), (1, 1), (0, 1), (1, 0)])

    def test_grid_layout(self):
        nodes = [(0, 0), (0, 2), (2, 0), (2, 2)]
        k = 2
        result = optimal_router_placement(nodes, k)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(0 <= x <= 2 and 0 <= y <= 2 for x, y in result))

    def test_cluster_of_nodes(self):
        nodes = [(1, 1), (1, 2), (2, 1), (2, 2)] * 5
        k = 2
        result = optimal_router_placement(nodes, k)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(1 <= x <= 2 and 1 <= y <= 2 for x, y in result))

    def test_edge_case_coordinates(self):
        nodes = [(0, 0), (1000, 1000)]
        k = 2
        result = optimal_router_placement(nodes, k)
        self.assertEqual(result, [(0, 0), (1000, 1000)])

    def test_duplicate_nodes(self):
        nodes = [(5, 5), (5, 5), (5, 5)]
        k = 1
        result = optimal_router_placement(nodes, k)
        self.assertEqual(result, [(5, 5)])

    def test_large_k_value(self):
        nodes = [(i, i) for i in range(20)]
        k = 10
        result = optimal_router_placement(nodes, k)
        self.assertEqual(len(result), 10)
        self.assertTrue(all(0 <= x <= 19 and x == y for x, y in result))

    def test_random_distribution(self):
        nodes = [(10, 20), (30, 40), (50, 60), (70, 80)]
        k = 2
        result = optimal_router_placement(nodes, k)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(10 <= x <= 70 and 20 <= y <= 80 for x, y in result))

if __name__ == '__main__':
    unittest.main()