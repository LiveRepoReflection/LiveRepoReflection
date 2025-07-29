import unittest
import time
import sys

# Import the function under test. It is assumed that the implementation of find_optimal_path,
# as well as the functions get_travel_time, get_vehicle_count, and receive_event_update (if used)
# are located in optimal_pathfinder/optimal_pathfinder.py
from optimal_pathfinder import find_optimal_path

# For testing, we will monkey-patch the external functions used by find_optimal_path.
# We assume that the solution's module has these as global functions.
# Since our test harness cannot access internals of the solution implementation,
# we simulate our testing environment by overriding these functions here.
#
# The dummy implementations below simulate dynamic travel times, capacity constraints, and event updates.


# Dummy get_travel_time:
# It checks if the edge has a "time_variation" field which is a function that takes the timestamp and returns an adjustment.
# Otherwise, it returns the base_time stored in the edge.
def dummy_get_travel_time(edge, timestamp):
    # Simulate time-of-day variation or event-based blockage.
    if "event" in edge:
        event = edge["event"]
        # If the current timestamp is within the event period, adjust the travel time accordingly.
        if event["start_time"] <= timestamp <= event["end_time"]:
            if event.get("block", False):
                return float('inf')  # Blocked road
            # Multiply the base time by the event factor if present.
            return edge["base_time"] * event.get("multiplier", 1)
    # Check if there's a time variation function provided.
    if "time_variation" in edge and callable(edge["time_variation"]):
        return edge["time_variation"](timestamp)
    return edge["base_time"]

# Dummy get_vehicle_count: returns a simulated vehicle count.
def dummy_get_vehicle_count(edge):
    # If the edge has a predefined "current_vehicle_count", return it, else assume 0.
    return edge.get("current_vehicle_count", 0)

# Dummy receive_event_update: for our testing purposes, this function does nothing.
def dummy_receive_event_update():
    pass

# Patch the functions in the module under test.
# It is assumed that the module under test (optimal_pathfinder) uses these function names.
import optimal_pathfinder
optimal_pathfinder.get_travel_time = dummy_get_travel_time
optimal_pathfinder.get_vehicle_count = dummy_get_vehicle_count
optimal_pathfinder.receive_event_update = dummy_receive_event_update

# Helper function to create graph edges. Our graph will be represented as an adjacency list:
# The graph is a dictionary mapping each node to a list of outgoing edges.
# Each edge is a dictionary with keys: "to", "base_time", "capacity", and optional keys for events or time variations.
def make_edge(to, base_time, capacity, **kwargs):
    edge = {"to": to, "base_time": base_time, "capacity": capacity}
    edge.update(kwargs)
    return edge

class OptimalPathfinderTest(unittest.TestCase):

    def test_basic_two_node(self):
        # Graph with two nodes and one direct edge.
        graph = {
            "A": [make_edge("B", base_time=10, capacity=100)],
            "B": []
        }
        departure_time = 1000
        expected_path = ["A", "B"]
        expected_total_time = 10
        optimal_path, total_time = find_optimal_path(graph, "A", "B", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

    def test_multiple_routes_choose_shortest(self):
        # Graph where there are two routes from A to D.
        # Route 1: A -> B -> D with travel times 5 + 5 = 10.
        # Route 2: A -> C -> D with travel times 2 + 20 = 22.
        graph = {
            "A": [make_edge("B", base_time=5, capacity=100),
                  make_edge("C", base_time=2, capacity=100)],
            "B": [make_edge("D", base_time=5, capacity=100)],
            "C": [make_edge("D", base_time=20, capacity=100)],
            "D": []
        }
        departure_time = 2000
        expected_path = ["A", "B", "D"]
        expected_total_time = 10
        optimal_path, total_time = find_optimal_path(graph, "A", "D", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

    def test_route_blocked_by_event(self):
        # Graph where the direct route is normally fastest, but an event blocks it.
        # Route 1: A -> B with base_time 10, but an event blocks the edge.
        # Route 2: A -> C -> B with travel times 15 and 15 respectively = 30.
        graph = {
            "A": [make_edge("B", base_time=10, capacity=100, event={"start_time": 500, "end_time": 1500, "block": True}),
                  make_edge("C", base_time=15, capacity=100)],
            "C": [make_edge("B", base_time=15, capacity=100)],
            "B": []
        }
        # Test with departure time during blockage.
        departure_time = 1000
        expected_path = ["A", "C", "B"]
        expected_total_time = 15 + 15
        optimal_path, total_time = find_optimal_path(graph, "A", "B", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

        # Test with departure time outside event period: the blocked edge becomes available.
        departure_time = 1600
        expected_path = ["A", "B"]
        expected_total_time = 10
        optimal_path, total_time = find_optimal_path(graph, "A", "B", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

    def test_capacity_constraint(self):
        # Graph where an excess vehicle count causes congestion.
        # For simplicity, assume that if vehicle count exceeds capacity, travel time doubles.
        def capacity_adjusted_time(edge, timestamp):
            current_vehicle = edge.get("current_vehicle_count", 0)
            if current_vehicle > edge["capacity"]:
                return edge["base_time"] * 2
            return edge["base_time"]

        # Use time_variation to simulate capacity effect.
        graph = {
            "A": [make_edge("B", base_time=10, capacity=50, time_variation=lambda ts: capacity_adjusted_time(graph["A"][0], ts)),
                  make_edge("C", base_time=20, capacity=100)],
            "B": [make_edge("D", base_time=10, capacity=100)],
            "C": [make_edge("D", base_time=5, capacity=100)],
            "D": []
        }
        # Set vehicle count on edge A->B above capacity to trigger delay.
        graph["A"][0]["current_vehicle_count"] = 60
        departure_time = 3000
        # The A->B route will now take 20 (10*2) + 10 = 30.
        # The alternative path A->C->D takes 20 + 5 = 25.
        expected_path = ["A", "C", "D"]
        expected_total_time = 25
        optimal_path, total_time = find_optimal_path(graph, "A", "D", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

    def test_complex_graph_dynamic_time(self):
        # Graph with multiple nodes where travel time on one edge changes based on departure time.
        # Use a time_variation function that returns a lower travel time after a threshold.
        def varying_time(timestamp):
            # Before timestamp 1000, travel time is 20; afterwards it becomes 5.
            return 20 if timestamp < 1000 else 5

        graph = {
            "A": [make_edge("B", base_time=10, capacity=100),
                  make_edge("C", base_time=15, capacity=100, time_variation=varying_time)],
            "B": [make_edge("D", base_time=10, capacity=100)],
            "C": [make_edge("D", base_time=10, capacity=100)],
            "D": []
        }
        # Test with departure time before threshold; edge A -> C takes 20.
        departure_time = 900
        # Route options:
        # A->B->D = 10 + 10 = 20.
        # A->C->D = 20 + 10 = 30.
        expected_path = ["A", "B", "D"]
        expected_total_time = 20
        optimal_path, total_time = find_optimal_path(graph, "A", "D", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

        # Test with departure time after threshold; edge A -> C takes 5.
        departure_time = 1100
        # Route options:
        # A->B->D = 10 + 10 = 20.
        # A->C->D = 5 + 10 = 15.
        expected_path = ["A", "C", "D"]
        expected_total_time = 15
        optimal_path, total_time = find_optimal_path(graph, "A", "D", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

    def test_no_possible_route(self):
        # Graph where destination is not reachable.
        graph = {
            "A": [make_edge("B", base_time=10, capacity=100)],
            "B": [make_edge("C", base_time=10, capacity=100)],
            "C": [],
            "D": []  # D is isolated.
        }
        departure_time = 1000
        # It is assumed that if there is no path, the function returns ([], float('inf')).
        expected_path = []
        expected_total_time = float('inf')
        optimal_path, total_time = find_optimal_path(graph, "A", "D", departure_time)
        self.assertEqual(optimal_path, expected_path)
        self.assertEqual(total_time, expected_total_time)

if __name__ == "__main__":
    unittest.main()