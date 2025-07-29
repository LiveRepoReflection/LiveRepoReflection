import unittest
from cdn_deployment import find_optimal_cdn_locations

class CDNDeploymentTest(unittest.TestCase):
    def test_simple_graph(self):
        graph = {
            "A": {"B": 1, "C": 5},
            "B": {"A": 1, "D": 2, "C": 1},
            "C": {"A": 5, "B": 1, "E": 3},
            "D": {"B": 2, "F": 4},
            "E": {"C": 3, "F": 2},
            "F": {"D": 4, "E": 2}
        }
        num_servers = 2
        budget = 10
        server_cost = {
            "A": 3, "B": 2, "C": 4, "D": 1, "E": 2, "F": 3
        }
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(len(result), 2)
        # Verify that the solution is within budget
        self.assertTrue(sum(server_cost[city] for city in result) <= budget)

    def test_single_server(self):
        graph = {
            "A": {"B": 1},
            "B": {"A": 1, "C": 1},
            "C": {"B": 1}
        }
        num_servers = 1
        budget = 5
        server_cost = {"A": 2, "B": 1, "C": 2}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, {"B"})

    def test_insufficient_budget(self):
        graph = {
            "A": {"B": 1},
            "B": {"A": 1}
        }
        num_servers = 1
        budget = 1
        server_cost = {"A": 2, "B": 2}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(result, set())

    def test_large_graph(self):
        # Create a line graph with 10 nodes
        graph = {}
        server_cost = {}
        for i in range(10):
            node = str(i)
            server_cost[node] = 1
            graph[node] = {}
            if i > 0:
                graph[node][str(i-1)] = 1
                graph[str(i-1)][node] = 1
        
        num_servers = 3
        budget = 5
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertLessEqual(len(result), num_servers)
        self.assertLessEqual(sum(server_cost[city] for city in result), budget)

    def test_equal_cost_different_topology(self):
        graph = {
            "A": {"B": 1, "C": 2},
            "B": {"A": 1, "C": 2},
            "C": {"A": 2, "B": 2, "D": 1},
            "D": {"C": 1}
        }
        num_servers = 2
        budget = 4
        server_cost = {"A": 1, "B": 1, "C": 1, "D": 1}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(len(result), 2)
        # A and C should be chosen over B and D due to better coverage
        self.assertTrue({"A", "C"} == result or {"A", "D"} == result)

    def test_minimum_servers_needed(self):
        graph = {
            "A": {"B": 10},
            "B": {"A": 10, "C": 10},
            "C": {"B": 10}
        }
        num_servers = 1
        budget = 100
        server_cost = {"A": 1, "B": 1, "C": 1}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, {"B"})

    def test_edge_case_single_node(self):
        graph = {"A": {}}
        num_servers = 1
        budget = 1
        server_cost = {"A": 1}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(result, {"A"})

    def test_edge_case_no_solution(self):
        graph = {
            "A": {"B": 1},
            "B": {"A": 1}
        }
        num_servers = 0
        budget = 10
        server_cost = {"A": 1, "B": 1}
        result = find_optimal_cdn_locations(graph, num_servers, budget, server_cost)
        self.assertEqual(result, set())

if __name__ == '__main__':
    unittest.main()