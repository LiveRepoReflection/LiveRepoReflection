import unittest
from delivery_route import find_route

class DeliveryRouteTest(unittest.TestCase):
    def test_start_equals_end(self):
        # When the start and end intersections are the same, the route should contain only that intersection.
        num_intersections = 3
        edges = []
        start_intersection = 1
        end_intersection = 1
        max_delivery_time = 60
        risk_factor = 1.0
        charging_stations = []
        max_range = 500
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [1])

    def test_simple_route(self):
        # A simple case with two possible routes; the optimal one should be chosen based on travel time and congestion risk.
        num_intersections = 3
        edges = [
            (0, 1, 100, 0.1),
            (1, 2, 100, 0.1),
            (0, 2, 250, 0.3)
        ]
        start_intersection = 0
        end_intersection = 2
        max_delivery_time = 60  # seconds
        risk_factor = 0.5
        charging_stations = []
        max_range = 300  # meters
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [0, 1, 2])

    def test_route_with_charging(self):
        # Test a scenario where the vehicle must recharge because a direct path exceeds the max range.
        num_intersections = 5
        edges = [
            (0, 1, 200, 0.2),
            (1, 4, 200, 0.2),
            (0, 2, 150, 0.2),
            (2, 3, 150, 0.2),
            (3, 4, 150, 0.2)
        ]
        start_intersection = 0
        end_intersection = 4
        max_delivery_time = 300  # seconds
        risk_factor = 1.0
        charging_stations = [2, 3]
        max_range = 300  # meters, so direct travel from 0->1->4 is not possible without recharge
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [0, 2, 3, 4])

    def test_no_possible_route_due_to_time(self):
        # Test a situation where the only available route exceeds the maximum delivery time.
        num_intersections = 3
        edges = [
            (0, 1, 1000, 0.0),
            (1, 2, 1000, 0.0)
        ]
        start_intersection = 0
        end_intersection = 2
        max_delivery_time = 10  # seconds: too strict for the given distances.
        risk_factor = 1.0
        charging_stations = []
        max_range = 3000
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [])

    def test_cycle_graph(self):
        # Ensure that graphs containing cycles do not cause infinite loops and produce a valid optimal route.
        num_intersections = 4
        edges = [
            (0, 1, 100, 0.1),
            (1, 2, 100, 0.1),
            (2, 1, 100, 0.1),
            (2, 3, 100, 0.1)
        ]
        start_intersection = 0
        end_intersection = 3
        max_delivery_time = 60
        risk_factor = 0.5
        charging_stations = []
        max_range = 300
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [0, 1, 2, 3])

    def test_route_with_risk_factor_zero(self):
        # With a risk factor of zero, the objective minimizes travel time only.
        num_intersections = 4
        edges = [
            (0, 1, 100, 0.5),
            (1, 3, 100, 0.5),
            (0, 2, 150, 0.0),
            (2, 3, 150, 0.0)
        ]
        start_intersection = 0
        end_intersection = 3
        max_delivery_time = 60
        risk_factor = 0.0
        charging_stations = []
        max_range = 300
        result = find_route(num_intersections, edges, start_intersection, end_intersection, max_delivery_time, risk_factor, charging_stations, max_range)
        self.assertEqual(result, [0, 2, 3])

if __name__ == '__main__':
    unittest.main()