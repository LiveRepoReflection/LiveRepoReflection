import unittest
import json
from traffic_reroute import optimize_traffic_flow

class TrafficRerouteTest(unittest.TestCase):
    def test_simple_network(self):
        input_data = {
            "nodes": [1, 2, 3],
            "edges": [
                {"source": 1, "destination": 2, "capacity": 10, "flow": 5},
                {"source": 2, "destination": 3, "capacity": 8, "flow": 3}
            ],
            "demands": [
                {"origin": 1, "destination": 3, "demand": 3}
            ]
        }
        expected_output = {
            "edges": [
                {"source": 1, "destination": 2, "flow": 8},
                {"source": 2, "destination": 3, "flow": 6}
            ]
        }
        self.assertEqual(optimize_traffic_flow(input_data), expected_output)

    def test_capacity_constraints(self):
        input_data = {
            "nodes": [1, 2, 3],
            "edges": [
                {"source": 1, "destination": 2, "capacity": 5, "flow": 4},
                {"source": 2, "destination": 3, "capacity": 5, "flow": 4}
            ],
            "demands": [
                {"origin": 1, "destination": 3, "demand": 10}
            ]
        }
        result = optimize_traffic_flow(input_data)
        for edge in result["edges"]:
            self.assertLessEqual(edge["flow"], 5)

    def test_multiple_paths(self):
        input_data = {
            "nodes": [1, 2, 3, 4],
            "edges": [
                {"source": 1, "destination": 2, "capacity": 10, "flow": 5},
                {"source": 2, "destination": 4, "capacity": 8, "flow": 3},
                {"source": 1, "destination": 3, "capacity": 10, "flow": 2},
                {"source": 3, "destination": 4, "capacity": 8, "flow": 1}
            ],
            "demands": [
                {"origin": 1, "destination": 4, "demand": 5}
            ]
        }
        result = optimize_traffic_flow(input_data)
        self.assertEqual(len(result["edges"]), 4)

    def test_proportional_demand_satisfaction(self):
        input_data = {
            "nodes": [1, 2, 3],
            "edges": [
                {"source": 1, "destination": 3, "capacity": 10, "flow": 0}
            ],
            "demands": [
                {"origin": 1, "destination": 3, "demand": 20},
                {"origin": 1, "destination": 3, "demand": 10}
            ]
        }
        result = optimize_traffic_flow(input_data)
        self.assertLessEqual(result["edges"][0]["flow"], 10)

    def test_large_network(self):
        nodes = list(range(1, 101))
        edges = []
        for i in range(1, 99):
            edges.append({
                "source": i,
                "destination": i + 1,
                "capacity": 100,
                "flow": 50
            })
        input_data = {
            "nodes": nodes,
            "edges": edges,
            "demands": [
                {"origin": 1, "destination": 100, "demand": 10}
            ]
        }
        result = optimize_traffic_flow(input_data)
        self.assertEqual(len(result["edges"]), len(edges))

    def test_cycle_detection(self):
        input_data = {
            "nodes": [1, 2, 3],
            "edges": [
                {"source": 1, "destination": 2, "capacity": 10, "flow": 5},
                {"source": 2, "destination": 3, "capacity": 10, "flow": 5},
                {"source": 3, "destination": 1, "capacity": 10, "flow": 5}
            ],
            "demands": [
                {"origin": 1, "destination": 3, "demand": 5}
            ]
        }
        result = optimize_traffic_flow(input_data)
        total_flow = sum(edge["flow"] for edge in result["edges"])
        self.assertLess(total_flow, 30)  # Ensure no infinite cycling

    def test_invalid_input(self):
        invalid_input = {
            "nodes": [1],
            "edges": [
                {"source": 1, "destination": 2, "capacity": -1, "flow": 0}
            ],
            "demands": [
                {"origin": 1, "destination": 2, "demand": 1}
            ]
        }
        with self.assertRaises(ValueError):
            optimize_traffic_flow(invalid_input)

    def test_empty_network(self):
        input_data = {
            "nodes": [],
            "edges": [],
            "demands": []
        }
        expected_output = {"edges": []}
        self.assertEqual(optimize_traffic_flow(input_data), expected_output)

    def test_no_possible_route(self):
        input_data = {
            "nodes": [1, 2, 3],
            "edges": [
                {"source": 1, "destination": 2, "capacity": 0, "flow": 0}
            ],
            "demands": [
                {"origin": 1, "destination": 3, "demand": 5}
            ]
        }
        result = optimize_traffic_flow(input_data)
        self.assertEqual(result["edges"][0]["flow"], 0)

if __name__ == '__main__':
    unittest.main()