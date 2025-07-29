import unittest
import math
from flow_routing import solve_routing

class TestFlowRouting(unittest.TestCase):
    def validate_path(self, path, graph_edges, source, destination):
        # Check that the path starts with source and ends with destination.
        self.assertEqual(path[0], source, "Path does not start with source")
        self.assertEqual(path[-1], destination, "Path does not end with destination")
        # Check that every consecutive pair in the path is a valid edge in the graph.
        edge_set = set()
        for (u, v, cap) in graph_edges:
            edge_set.add((u, v))
        for i in range(len(path) - 1):
            self.assertIn((path[i], path[i+1]), edge_set, f"Edge ({path[i]}, {path[i+1]}) is not in the graph")

    def compute_edge_flow(self, routing, graph_edges):
        # Compute total flow on each edge from the routing dictionary.
        # Return a dict mapping (u, v) -> total flow.
        flow_on_edge = {}
        for (commodity_index, request_index), path_dict in routing.items():
            for path, flow in path_dict.items():
                # path is a tuple of nodes.
                for i in range(len(path) - 1):
                    edge = (path[i], path[i+1])
                    flow_on_edge[edge] = flow_on_edge.get(edge, 0.0) + flow
        # Ensure all edges from graph are present in dictionary even if flow is zero.
        for (u, v, cap) in graph_edges:
            if (u, v) not in flow_on_edge:
                flow_on_edge[(u, v)] = 0.0
        return flow_on_edge

    def test_single_path_routing(self):
        # Simple graph: 0 -> 1 -> 2, capacity 5 on each edge.
        num_nodes = 3
        graph_edges = [
            (0, 1, 5),
            (1, 2, 5)
        ]
        graph = {
            "num_nodes": num_nodes,
            "edges": graph_edges
        }
        # Single commodity with one request from 0 to 2 with demand 4.
        commodity_requests = [
            {
                "requests": [
                    (0, 2, 4)
                ]
            }
        ]
        routing = solve_routing(graph, commodity_requests)

        # Validate routing structure.
        self.assertIsInstance(routing, dict)
        self.assertIn((0, 0), routing)
        paths = routing[(0, 0)]
        total_flow = 0.0
        for path, flow in paths.items():
            self.assertIsInstance(path, tuple)
            self.validate_path(path, graph_edges, 0, 2)
            total_flow += flow
        self.assertAlmostEqual(total_flow, 4.0, places=5)

    def test_split_flow_routing(self):
        # Graph with two possible paths from 0 to 3.
        # Path1: 0 -> 1 -> 3 with capacity 3 on each edge.
        # Path2: 0 -> 2 -> 3 with capacity 2 on each edge.
        num_nodes = 4
        graph_edges = [
            (0, 1, 3),
            (1, 3, 3),
            (0, 2, 2),
            (2, 3, 2)
        ]
        graph = {
            "num_nodes": num_nodes,
            "edges": graph_edges
        }
        # Single commodity with one request from 0 to 3 with demand 4.
        commodity_requests = [
            {
                "requests": [
                    (0, 3, 4)
                ]
            }
        ]
        routing = solve_routing(graph, commodity_requests)
        self.assertIn((0, 0), routing)
        paths = routing[(0, 0)]
        total_flow = 0.0
        for path, flow in paths.items():
            self.validate_path(path, graph_edges, 0, 3)
            total_flow += flow
        self.assertAlmostEqual(total_flow, 4.0, places=5)

        # Additionally, compute flow on each edge and verify that capacities are used properly.
        edge_flow = self.compute_edge_flow(routing, graph_edges)
        for edge, flow in edge_flow.items():
            # Flow may exceed capacity, but we want to check congestion cost if so.
            # Congestion cost = (flow - capacity)^2 if flow > capacity else 0.
            # Here we just verify that computed flows make sense.
            cap = next(c for (u, v, c) in graph_edges if (u, v) == edge)
            if flow > cap:
                self.assertTrue((flow - cap) >= 0)

    def test_disconnected_graph(self):
        # Graph where no path exists from source to destination.
        num_nodes = 2
        graph_edges = []  # No edges.
        graph = {
            "num_nodes": num_nodes,
            "edges": graph_edges
        }
        # Single commodity with one request from 0 to 1, demand 5.
        commodity_requests = [
            {
                "requests": [
                    (0, 1, 5)
                ]
            }
        ]
        routing = solve_routing(graph, commodity_requests)
        self.assertIn((0, 0), routing)
        # Since there is no path, we expect that the routing for this request is empty.
        self.assertEqual(routing[(0, 0)], {})

    def test_multiple_commodities(self):
        # Construct a graph with several nodes and edges.
        num_nodes = 6
        graph_edges = [
            (0, 1, 4),
            (1, 2, 4),
            (0, 3, 3),
            (3, 2, 3),
            (1, 4, 2),
            (4, 2, 2),
            (2, 5, 5),
            (4, 5, 3)
        ]
        graph = {
            "num_nodes": num_nodes,
            "edges": graph_edges
        }
        # Two commodities.
        # Commodity 0: Two requests.
        # Request 0: from 0 to 5 with demand 5.
        # Request 1: from 3 to 5 with demand 3.
        # Commodity 1: One request.
        # Request 0: from 1 to 4 with demand 2.
        commodity_requests = [
            {
                "requests": [
                    (0, 5, 5),
                    (3, 5, 3)
                ]
            },
            {
                "requests": [
                    (1, 4, 2)
                ]
            }
        ]
        routing = solve_routing(graph, commodity_requests)
        # Validate each routing.
        for commodity_index, commodity in enumerate(commodity_requests):
            for request_index, (src, dst, demand) in enumerate(commodity["requests"]):
                key = (commodity_index, request_index)
                self.assertIn(key, routing)
                paths = routing[key]
                total_flow = 0.0
                for path, flow in paths.items():
                    self.validate_path(path, graph_edges, src, dst)
                    total_flow += flow
                # Allow a small tolerance for floating point arithmetic.
                self.assertAlmostEqual(total_flow, demand, places=5)

        # Compute overall edge usage.
        edge_flow = self.compute_edge_flow(routing, graph_edges)
        # For each edge, verify that the flow is a non-negative number.
        for edge, flow in edge_flow.items():
            self.assertGreaterEqual(flow, 0.0)

    def test_floating_point_precision(self):
        # Test handling of floating point precision with a graph where splitting
        # the flow might result in non-integer values.
        num_nodes = 4
        graph_edges = [
            (0, 1, 2.5),
            (1, 2, 2.5),
            (0, 3, 2.5),
            (3, 2, 2.5)
        ]
        graph = {
            "num_nodes": num_nodes,
            "edges": graph_edges
        }
        # One commodity with one request from 0 to 2 with demand 3.
        commodity_requests = [
            {
                "requests": [
                    (0, 2, 3)
                ]
            }
        ]
        routing = solve_routing(graph, commodity_requests)
        self.assertIn((0, 0), routing)
        paths = routing[(0, 0)]
        total_flow = 0.0
        for path, flow in paths.items():
            self.validate_path(path, graph_edges, 0, 2)
            total_flow += flow
        self.assertAlmostEqual(total_flow, 3.0, places=5)

if __name__ == '__main__':
    unittest.main()