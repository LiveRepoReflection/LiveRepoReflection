import unittest
from optimal_network_path import find_optimal_path

class TestOptimalNetworkPath(unittest.TestCase):

    def test_sample_scenario(self):
        # Test scenario based on the provided example.
        N = 4
        edges = [(0, 1, 5), (1, 2, 3), (0, 2, 10), (2, 3, 1)]
        start_node = 0
        end_node = 3
        latency_updates = [(1, 2, 2), (0, 1, 1), (0, 3, 15)]
        # After update 1: edge (1,2) now 2, so best path = 0->1->2->3 = 5+2+1 = 8.
        # After update 2: edge (0,1) now 1, so best path = 0->1->2->3 = 1+2+1 = 4.
        # After update 3: new edge (0,3) with 15 is added, best remains = 4.
        expected = [8, 4, 4]
        result = find_optimal_path(N, edges, start_node, end_node, latency_updates)
        self.assertEqual(result, expected)

    def test_no_updates(self):
        # Test where there are no latency updates.
        N = 3
        edges = [(0, 1, 4), (1, 2, 6), (0, 2, 15)]
        start_node = 0
        end_node = 2
        latency_updates = []
        # With no update, the function should return an empty list.
        expected = []
        result = find_optimal_path(N, edges, start_node, end_node, latency_updates)
        self.assertEqual(result, expected)

    def test_disconnected_graph(self):
        # Test where the graph is disconnected and no path exists.
        N = 5
        edges = [(0, 1, 10), (1, 2, 5), (3, 4, 1)]
        start_node = 0
        end_node = 4
        latency_updates = [(3, 4, 10), (0, 1, 2)]
        # Initially, there is no path between 0 and 4.
        # Even after updates, the two components remain disconnected.
        expected = [-1, -1]
        result = find_optimal_path(N, edges, start_node, end_node, latency_updates)
        self.assertEqual(result, expected)

    def test_multiple_updates_same_edge(self):
        # Test where multiple updates occur on the same edge.
        N = 4
        edges = [(0, 1, 8), (1, 2, 4), (2, 3, 7), (0, 3, 20)]
        start_node = 0
        end_node = 3
        latency_updates = [(1, 2, 2), (1, 2, 10), (0, 3, 5), (0, 1, 1)]
        # Initially best = 0->1->2->3 = 8+4+7 = 19, alternative = 20.
        # After update 1: (1,2)=2, path= 8+2+7 = 17.
        # After update 2: (1,2)=10, path= 8+10+7 = 25 (worse), so best is still alternative 20.
        # After update 3: new edge (0,3)=5, best becomes 5.
        # After update 4: (0,1)=1, possible path becomes 1+10+7 = 18; still best remains 5 from direct.
        expected = [17, 20, 5, 5]
        result = find_optimal_path(N, edges, start_node, end_node, latency_updates)
        self.assertEqual(result, expected)

    def test_path_becomes_unavailable(self):
        # Test when an update increases the latency such that the best route is no longer viable (simulate removal by very high latency)
        N = 4
        edges = [(0, 1, 3), (1, 2, 3), (2, 3, 3)]
        start_node = 0
        end_node = 3
        latency_updates = [(1, 2, 10**9)]
        # After update, optimal route latency becomes 3 + 10**9 + 3, but if we simulate removal by checking for a limit,
        # However, our problem statement does not specify removal, so we treat high latency as valid.
        # We calculate expected latency.
        expected_latency = 3 + 10**9 + 3
        expected = [expected_latency]
        result = find_optimal_path(N, edges, start_node, end_node, latency_updates)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()