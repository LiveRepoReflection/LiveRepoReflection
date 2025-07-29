import unittest
from optimal_deploy import find_optimal_deployment

class TestOptimalDeploy(unittest.TestCase):
    def test_single_node(self):
        graph = {0: {}}
        T = 1
        C = 1
        costs = [5]
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        expected_servers = {0}
        expected_latency = 0
        self.assertEqual(servers, expected_servers)
        self.assertEqual(total_latency, expected_latency)

    def test_two_nodes_capacity_one(self):
        graph = {
            0: {1: 3},
            1: {0: 3}
        }
        T = 3
        C = 1
        costs = [10, 1]
        # With capacity 1, each node must have its own server.
        expected_servers = {0, 1}
        expected_latency = 0  # each node is a server.
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        self.assertEqual(servers, expected_servers)
        self.assertEqual(total_latency, expected_latency)

    def test_triangle(self):
        # Triangle graph where each edge has weight such that T = 1.
        # Graph: 0--1 (1), 1--2 (1), and 0--2 (3).
        graph = {
            0: {1: 1, 2: 3},
            1: {0: 1, 2: 1},
            2: {0: 3, 1: 1}
        }
        T = 1
        C = 2
        costs = [5, 5, 5]
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        # With capacity 2, two servers are required.
        self.assertEqual(len(servers), 2)
        # Verify that every node is assigned a server within T.
        # For each node, if it is not a server, its distance to the nearest server must be 1.
        # Therefore, the total minimal latency must be 1.
        self.assertEqual(total_latency, 1)
    
    def test_chain(self):
        # Chain: 0 -2-> 1 -2-> 2 -2-> 3 -2-> 4
        graph = {
            0: {1: 2},
            1: {0: 2, 2: 2},
            2: {1: 2, 3: 2},
            3: {2: 2, 4: 2},
            4: {3: 2}
        }
        T = 3
        C = 2
        costs = [3, 100, 3, 100, 3]
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        # Expected optimal deployment is to deploy servers at nodes 0, 2, and 4.
        expected_servers = {0, 2, 4}
        # Assignments:
        # Node 0 served by server 0 (latency 0).
        # Node 1 served by server 0 (latency 2) or server 2 (latency 2).
        # Node 2 served by server 2 (latency 0).
        # Node 3 served by server 2 (latency 2) or server 4 (latency 2).
        # Node 4 served by server 4 (latency 0).
        # Total latency should be 2 + 2 = 4.
        self.assertEqual(servers, expected_servers)
        self.assertEqual(total_latency, 4)
    
    def test_square_cost_latency(self):
        # Square graph: 0,1,2,3 in a cycle.
        graph = {
            0: {1: 1, 3: 1},
            1: {0: 1, 2: 1},
            2: {1: 1, 3: 1},
            3: {0: 1, 2: 1}
        }
        T = 1
        C = 2
        costs = [10, 1, 10, 1]
        # Optimal deployment is to deploy at nodes 1 and 3.
        expected_servers = {1, 3}
        # Assignment:
        # Nodes 1 and 3 are servers (latency 0).
        # Node 0: min(dist from 1=1, from 3=1) = 1.
        # Node 2: min(dist from 1=1, from 3=1) = 1.
        # Total latency = 1 + 1 = 2.
        expected_latency = 2
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        self.assertEqual(servers, expected_servers)
        self.assertEqual(total_latency, expected_latency)

    def test_all_coverage_with_single_server(self):
        # Chain of 4 nodes where one server can cover all nodes due to high capacity.
        graph = {
            0: {1: 1},
            1: {0: 1, 2: 1},
            2: {1: 1, 3: 1},
            3: {2: 1}
        }
        T = 2
        C = 4
        costs = [5, 5, 5, 5]
        # Deploying one server at node 1 covers all:
        # Distances: node0:1, node1:0, node2:1, node3:2.
        # Total latency = 1 + 0 + 1 + 2 = 4.
        expected_servers = {1}
        expected_latency = 4
        servers, total_latency = find_optimal_deployment(graph, T, C, costs)
        self.assertEqual(servers, expected_servers)
        self.assertEqual(total_latency, expected_latency)

if __name__ == '__main__':
    unittest.main()