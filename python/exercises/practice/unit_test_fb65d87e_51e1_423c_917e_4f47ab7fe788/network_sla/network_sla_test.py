import unittest
from network_sla.network_sla import NetworkSLA

class TestNetworkSLA(unittest.TestCase):
    def test_single_node_self_request(self):
        # Minimal graph with a single node and no edges.
        graph = {
            "nodes": {
                "A": {"capacity": 100}
            },
            "edges": []
        }
        # Request from A to A with zero latency requirement.
        requests = [
            {"source": "A", "destination": "A", "data_volume": 10, "latency_requirement": 0}
        ]
        solver = NetworkSLA(graph, requests)
        max_requests, request_deliveries, edge_flows = solver.solve()
        # Expect the self-transfer to be satisfied.
        self.assertEqual(max_requests, 1)
        self.assertEqual(len(request_deliveries), 1)
        self.assertEqual(request_deliveries[0], 10)
        # No edges should carry any flow.
        self.assertEqual(edge_flows, {})

    def test_chain_valid_request(self):
        # Simple chain: A -> B -> C.
        graph = {
            "nodes": {
                "A": {"capacity": 100},
                "B": {"capacity": 100},
                "C": {"capacity": 100}
            },
            "edges": [
                {"from": "A", "to": "B", "capacity": 50, "latency": 10},
                {"from": "B", "to": "C", "capacity": 50, "latency": 10}
            ]
        }
        # Single request from A to C, volume 30, total latency must be <= 25.
        requests = [
            {"source": "A", "destination": "C", "data_volume": 30, "latency_requirement": 25}
        ]
        solver = NetworkSLA(graph, requests)
        max_requests, request_deliveries, edge_flows = solver.solve()
        # The only request should be satisfied.
        self.assertEqual(max_requests, 1)
        self.assertEqual(len(request_deliveries), 1)
        self.assertEqual(request_deliveries[0], 30)
        # Check that flows on each edge are at least the required volume.
        self.assertIn(("A", "B"), edge_flows)
        self.assertIn(("B", "C"), edge_flows)
        self.assertEqual(edge_flows[("A", "B")], 30)
        self.assertEqual(edge_flows[("B", "C")], 30)

    def test_branching_paths_split_flow(self):
        # Graph with branching paths from A to D.
        graph = {
            "nodes": {
                "A": {"capacity": 100},
                "B": {"capacity": 100},
                "C": {"capacity": 100},
                "D": {"capacity": 100}
            },
            "edges": [
                {"from": "A", "to": "B", "capacity": 40, "latency": 5},
                {"from": "A", "to": "C", "capacity": 40, "latency": 5},
                {"from": "B", "to": "D", "capacity": 40, "latency": 5},
                {"from": "C", "to": "D", "capacity": 40, "latency": 5}
            ]
        }
        # Single request from A to D, volume 40 and latency requirement 15.
        requests = [
            {"source": "A", "destination": "D", "data_volume": 40, "latency_requirement": 15}
        ]
        solver = NetworkSLA(graph, requests)
        max_requests, request_deliveries, edge_flows = solver.solve()
        # Expect the request to be fully satisfied using split paths.
        self.assertEqual(max_requests, 1)
        self.assertEqual(len(request_deliveries), 1)
        self.assertEqual(request_deliveries[0], 40)
        # The flows on split edges should add up to 40.
        flow_AB = edge_flows.get(("A", "B"), 0)
        flow_AC = edge_flows.get(("A", "C"), 0)
        self.assertEqual(flow_AB + flow_AC, 40)
        flow_BD = edge_flows.get(("B", "D"), 0)
        flow_CD = edge_flows.get(("C", "D"), 0)
        self.assertEqual(flow_BD + flow_CD, 40)

    def test_latency_constraint_failure(self):
        # Graph where latency is too high for the given requirement.
        graph = {
            "nodes": {
                "A": {"capacity": 100},
                "B": {"capacity": 100}
            },
            "edges": [
                {"from": "A", "to": "B", "capacity": 100, "latency": 20}
            ]
        }
        # Request with latency requirement less than edge latency.
        requests = [
            {"source": "A", "destination": "B", "data_volume": 10, "latency_requirement": 10}
        ]
        solver = NetworkSLA(graph, requests)
        max_requests, request_deliveries, edge_flows = solver.solve()
        # No request should be satisfied due to latency violation.
        self.assertEqual(max_requests, 0)
        self.assertEqual(request_deliveries, [])
        # Edge flows should be zero.
        self.assertEqual(edge_flows.get(("A", "B"), 0), 0)

    def test_node_capacity_constraint_failure(self):
        # Graph where a node's processing capacity limits satisfying a request.
        graph = {
            "nodes": {
                "A": {"capacity": 50},
                "B": {"capacity": 20}
            },
            "edges": [
                {"from": "A", "to": "B", "capacity": 50, "latency": 5}
            ]
        }
        # Request requiring more data than node B can process.
        requests = [
            {"source": "A", "destination": "B", "data_volume": 40, "latency_requirement": 10}
        ]
        solver = NetworkSLA(graph, requests)
        max_requests, request_deliveries, edge_flows = solver.solve()
        # Expect that the request is not fully satisfied when node capacity is insufficient.
        self.assertEqual(max_requests, 0)
        self.assertEqual(request_deliveries, [])
        # Flow should not exceed node B's capacity.
        self.assertTrue(edge_flows.get(("A", "B"), 0) <= 20)

if __name__ == '__main__':
    unittest.main()