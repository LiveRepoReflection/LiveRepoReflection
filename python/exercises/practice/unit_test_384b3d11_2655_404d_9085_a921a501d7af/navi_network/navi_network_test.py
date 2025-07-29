import unittest
import random
import time

# Assuming the existence of these functions in navi_network/navi_network.py
from navi_network import find_least_risky_path, update_occupancy

class TestNaviNetwork(unittest.TestCase):
    def setUp(self):
        # Create a basic graph for testing.
        # Graph structure: Each node is an integer,
        # and the graph is a dict mapping node -> dict of neighbor: {length, speed_limit, base_risk}
        self.graph = {
            1: {2: {'length': 5, 'speed_limit': 10, 'base_risk': 1},
                3: {'length': 10, 'speed_limit': 8, 'base_risk': 2}},
            2: {4: {'length': 3, 'speed_limit': 10, 'base_risk': 0.5}},
            3: {4: {'length': 4, 'speed_limit': 9, 'base_risk': 1}},
            4: {}
        }
        # In practice, occupancy is maintained in the module state.
        # Reset occupancy values if needed (simulate a reset mechanism through update_occupancy)
        # For testing, assume update_occupancy with negative delta can reset to 0.
        for u in self.graph:
            for v in self.graph[u]:
                # Reset occupancy to 0.
                update_occupancy((u, v), -1000)

        self.congestion_factor = 0.2
        self.exploration_factor = 0.1

    def test_basic_path(self):
        # Test to ensure the algorithm finds the path with minimal risk.
        # For the given graph, there are two potential paths: 1->2->4 and 1->3->4.
        # Determine expected by manually computing:
        # Path risk for 1->2->4: 
        #   risk(1,2) = 1 + 0 * 0.2 = 1, risk(2,4) = 0.5 + 0 * 0.2 = 0.5, total=1.5.
        # Path risk for 1->3->4: 
        #   risk(1,3) = 2 + 0 * 0.2 = 2, risk(3,4) = 1 + 0 * 0.2 = 1, total=3.
        expected_path = [1, 2, 4]
        path = find_least_risky_path(self.graph, 1, 4, self.congestion_factor, self.exploration_factor)
        self.assertEqual(path, expected_path)

    def test_no_path(self):
        # Test when no path exists (disconnect the graph)
        graph = {
            1: {2: {'length': 5, 'speed_limit': 10, 'base_risk': 1}},
            2: {},
            3: {4: {'length': 4, 'speed_limit': 9, 'base_risk': 1}},
            4: {}
        }
        path = find_least_risky_path(graph, 1, 4, self.congestion_factor, self.exploration_factor)
        self.assertEqual(path, [])

    def test_occupancy_update_effect(self):
        # Initially, best path from 1 to 4 is [1,2,4] as computed earlier.
        initial_path = find_least_risky_path(self.graph, 1, 4, self.congestion_factor, self.exploration_factor)
        self.assertEqual(initial_path, [1, 2, 4])
        
        # Increase occupancy on edge (1,2) significantly to simulate congestion.
        update_occupancy((1, 2), 10)
        # Now risk on edge (1,2) becomes 1 + 10*0.2 = 3, path risk [1,2,4] becomes 3 + 0.5 = 3.5,
        # whereas path [1,3,4] remains at risk 2+1 = 3.
        new_path = find_least_risky_path(self.graph, 1, 4, self.congestion_factor, self.exploration_factor)
        self.assertEqual(new_path, [1, 3, 4])

        # Now, reduce occupancy to revert the change.
        update_occupancy((1, 2), -10)
        reverted_path = find_least_risky_path(self.graph, 1, 4, self.congestion_factor, self.exploration_factor)
        self.assertEqual(reverted_path, [1, 2, 4])

    def test_exploration_randomization(self):
        # Test that different calls with a high exploration_factor might result in different valid paths.
        # Create a graph with two nearly equal paths.
        graph = {
            1: {
                2: {'length': 5, 'speed_limit': 10, 'base_risk': 1},
                3: {'length': 5, 'speed_limit': 10, 'base_risk': 1}
            },
            2: {
                4: {'length': 4, 'speed_limit': 10, 'base_risk': 1}
            },
            3: {
                4: {'length': 4, 'speed_limit': 10, 'base_risk': 1}
            },
            4: {}
        }
        # Reset occupancy for all edges in this graph.
        for u in graph:
            for v in graph[u]:
                update_occupancy((u, v), -1000)
                
        # With a higher exploration factor, multiple calls might not always pick the same path.
        paths = set()
        high_exploration = 0.9
        for _ in range(20):
            path = find_least_risky_path(graph, 1, 4, self.congestion_factor, high_exploration)
            paths.add(tuple(path))
        # We expect at least two different paths due to randomization.
        self.assertTrue(len(paths) >= 2)

    def test_large_scale_graph_performance(self):
        # Construct a larger graph with 1000 nodes in a simple chain plus extra random edges,
        # ensuring the algorithm completes quickly.
        large_graph = {}
        num_nodes = 1000
        for i in range(1, num_nodes + 1):
            large_graph[i] = {}
        # Create a chain from 1 to num_nodes.
        for i in range(1, num_nodes):
            large_graph[i][i+1] = {'length': 1, 'speed_limit': 10, 'base_risk': 0.5}
        # Add some random extra edges.
        random.seed(42)
        for _ in range(500):
            u = random.randint(1, num_nodes - 1)
            v = random.randint(u+1, num_nodes)
            large_graph[u][v] = {'length': random.uniform(1, 10), 'speed_limit': random.uniform(5, 15), 'base_risk': random.uniform(0, 2)}
            update_occupancy((u, v), -1000)
        start_time = time.time()
        path = find_least_risky_path(large_graph, 1, num_nodes, self.congestion_factor, self.exploration_factor)
        end_time = time.time()
        # Check path is found and performance is within required time (1 second).
        self.assertTrue(path[0] == 1 and path[-1] == num_nodes)
        self.assertLess(end_time - start_time, 1.0)

if __name__ == '__main__':
    unittest.main()