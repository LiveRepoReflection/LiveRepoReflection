import unittest
from net_relief import mitigate_congestion

class TestNetRelief(unittest.TestCase):
    def apply_changes(self, graph, changes):
        """
        Returns a new dictionary representing the updated utilization for each edge.
        The new utilization is original utilization plus the change from the adjustments.
        """
        updated = {}
        for u in graph:
            for v in graph[u]:
                original_util = graph[u][v]["utilization"]
                change = changes.get((u, v), 0)
                updated[(u, v)] = original_util + change
        return updated

    def check_capacity_constraints(self, graph, updated):
        """
        Checks that for every edge, the updated utilization does not exceed its capacity.
        """
        for u in graph:
            for v in graph[u]:
                capacity = graph[u][v]["capacity"]
                self.assertLessEqual(updated[(u, v)], capacity, msg=f"Edge {(u, v)} exceeds capacity.")

    def check_valid_edges_in_changes(self, graph, changes):
        """
        Ensures that each key in the changes dictionary corresponds to an edge in the input graph.
        """
        for (u, v) in changes:
            self.assertIn(u, graph, msg=f"Node {u} not in graph.")
            self.assertIn(v, graph[u], msg=f"Edge ({u}, {v}) not found in graph.")

    def test_no_congestion(self):
        # Graph with no congested edges.
        graph = {
            1: {2: {"capacity": 10, "utilization": 3}},
            2: {3: {"capacity": 10, "utilization": 4}},
            3: {}
        }
        affected_servers = [1]
        congestion_threshold = 0.8
        communication_matrix = {1: {3}}
        weights = {(1, 3): 2}
        changes = mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights)
        # When no edge is congested, no rerouting is required.
        self.assertIsInstance(changes, dict)
        self.assertEqual(changes, {})

    def test_single_congested_edge_alternative_route(self):
        # Graph with a congested direct edge and a viable alternative route.
        graph = {
            1: {
                2: {"capacity": 10, "utilization": 9},  # congested: 9 > 8 (0.8*10)
                3: {"capacity": 10, "utilization": 2}
            },
            2: {
                3: {"capacity": 10, "utilization": 5}
            },
            3: {}
        }
        affected_servers = [1]
        congestion_threshold = 0.8
        communication_matrix = {1: {3}}
        weights = {(1, 3): 3}

        changes = mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights)
        self.assertIsInstance(changes, dict)
        # Ensure all keys in changes correspond to valid graph edges.
        self.check_valid_edges_in_changes(graph, changes)

        updated_util = self.apply_changes(graph, changes)
        # Check capacity constraints on all edges.
        self.check_capacity_constraints(graph, updated_util)

        # Check that the overall change sums up to 0
        total_delta = sum(changes.values())
        self.assertEqual(total_delta, 0, "Total net change should be zero.")

    def test_multiple_affected_servers(self):
        # Graph with multiple affected servers and multiple routes.
        graph = {
            1: {
                2: {"capacity": 15, "utilization": 10},
                4: {"capacity": 15, "utilization": 1}
            },
            2: {
                3: {"capacity": 15, "utilization": 5},
                4: {"capacity": 15, "utilization": 3}
            },
            3: {
                4: {"capacity": 15, "utilization": 14}  # congested: 14 > 12 (0.8*15)
            },
            4: {}
        }
        affected_servers = [1, 2]
        congestion_threshold = 0.8
        communication_matrix = {
            1: {4},
            2: {4}
        }
        weights = {
            (1, 4): 4,
            (2, 4): 2
        }

        changes = mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights)
        self.assertIsInstance(changes, dict)
        self.check_valid_edges_in_changes(graph, changes)

        updated_util = self.apply_changes(graph, changes)
        self.check_capacity_constraints(graph, updated_util)

        # Check that net change is balanced.
        total_delta = sum(changes.values())
        self.assertEqual(total_delta, 0, "Total net change should be zero.")

    def test_heavy_congestion_with_alternative_paths(self):
        # A more complex graph with several possible alternative routes.
        graph = {
            1: {
                2: {"capacity": 20, "utilization": 18},  # congested: 18 > 16 (0.8*20)
                3: {"capacity": 20, "utilization": 5},
                4: {"capacity": 20, "utilization": 3}
            },
            2: {
                5: {"capacity": 20, "utilization": 10}
            },
            3: {
                5: {"capacity": 20, "utilization": 4},
                4: {"capacity": 20, "utilization": 2}
            },
            4: {
                5: {"capacity": 20, "utilization": 2}
            },
            5: {}
        }
        affected_servers = [1]
        congestion_threshold = 0.8
        communication_matrix = {1: {5}}
        weights = {(1, 5): 6}

        changes = mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights)
        self.assertIsInstance(changes, dict)
        self.check_valid_edges_in_changes(graph, changes)

        updated_util = self.apply_changes(graph, changes)
        self.check_capacity_constraints(graph, updated_util)

        # Check that overall adjustment is balanced.
        total_delta = sum(changes.values())
        self.assertEqual(total_delta, 0, "Total net change should be zero.")

    def test_no_possible_reroute_due_to_capacity(self):
        # In this test, all alternative routes are too saturated to handle extra traffic.
        graph = {
            1: {
                2: {"capacity": 10, "utilization": 9},
                3: {"capacity": 10, "utilization": 9}  # Both nearly congested
            },
            2: {
                4: {"capacity": 10, "utilization": 9}
            },
            3: {
                4: {"capacity": 10, "utilization": 9}
            },
            4: {}
        }
        affected_servers = [1]
        congestion_threshold = 0.8
        communication_matrix = {1: {4}}
        weights = {(1, 4): 2}

        changes = mitigate_congestion(graph, affected_servers, congestion_threshold, communication_matrix, weights)
        self.assertIsInstance(changes, dict)
        self.check_valid_edges_in_changes(graph, changes)

        updated_util = self.apply_changes(graph, changes)
        self.check_capacity_constraints(graph, updated_util)

        # If no adequate reroute exists, the changes could be empty or minimal.
        # We simply check that capacity constraints are met and net change is balanced.
        total_delta = sum(changes.values())
        self.assertEqual(total_delta, 0, "Total net change should be zero when no valid reroute is possible.")

if __name__ == '__main__':
    unittest.main()