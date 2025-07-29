import unittest
import datetime

# Assuming the main function to be tested is "find_routes" in the transit_oracle module.
from transit_oracle import find_routes

class TransitOracleTestCase(unittest.TestCase):
    def setUp(self):
        # Construct a sample static network
        self.network = {
            "stations": {
                "A": {"lat": 40.712776, "lon": -74.005974},   # Example: New York
                "B": {"lat": 40.730610, "lon": -73.935242},   # Example: Brooklyn
                "C": {"lat": 40.650002, "lon": -73.949997},   # Example: Queens
                "D": {"lat": 40.844782, "lon": -73.864827}    # Example: Bronx
            },
            "lines": [
                {
                    "name": "Bus_1",
                    "mode": "bus",
                    "stations": ["A", "B", "C"],
                    "travel_times": [15, 20]  # minutes between A->B and B->C
                },
                {
                    "name": "Subway_1",
                    "mode": "subway",
                    "stations": ["A", "D"],
                    "travel_times": [10]
                },
                {
                    "name": "Train_1",
                    "mode": "train",
                    "stations": ["D", "B"],
                    "travel_times": [8]
                }
            ],
            "transfers": [
                {
                    "station": "B",
                    "transfer_time": 5  # minutes penalty for transferring at station B
                },
                {
                    "station": "D",
                    "transfer_time": 7  # minutes penalty for transferring at station D
                }
            ],
            "pricing": {
                "base_fare": 2.0,
                "per_min": 0.5,
                "dynamic_rules": [
                    # Each rule could be something like: {"start_hour": 7, "end_hour": 9, "multiplier": 1.5}
                    {"start_hour": 7, "end_hour": 9, "multiplier": 1.5},
                    {"start_hour": 17, "end_hour": 19, "multiplier": 1.3}
                ]
            },
            "capacity": {
                # Simulated capacity factor (lower value means more comfort penalty)
                "Bus_1": {"peak_hours": [(7, 9), (17, 19)], "penalty": 10},
                "Subway_1": {"peak_hours": [(7, 9), (17, 19)], "penalty": 8},
                "Train_1": {"peak_hours": [(7, 9), (17, 19)], "penalty": 6}
            }
        }

        # Base real-time updates: no delays initially.
        self.real_time_updates_no_delay = {
            "delays": {
                "Bus_1": 0,
                "Subway_1": 0,
                "Train_1": 0
            },
            "pricing_updates": {}
        }

        # Real-time update example: Delay on Subway_1
        self.real_time_updates_delay = {
            "delays": {
                "Bus_1": 0,
                "Subway_1": 5,
                "Train_1": 0
            },
            "pricing_updates": {}
        }

        # Query example: start near station A, end near station C
        self.query = {
            "start": {"lat": 40.712776, "lon": -74.005974},  # Near A
            "end": {"lat": 40.650002, "lon": -73.949997},      # Near C
            "departure_time": datetime.datetime(2023, 10, 25, 8, 0).timestamp()  # Peak hour
        }

    def validate_route_option(self, route):
        # Each route option should include required keys
        self.assertIsInstance(route, dict)
        expected_keys = {"stations", "lines", "segment_times", "segment_fares", "total_time", "total_fare", "comfort_score"}
        self.assertTrue(expected_keys.issubset(route.keys()),
                        f"Route option keys missing. Expected at least {expected_keys}, got {route.keys()}.")

    def test_direct_route_structure(self):
        # Test that the system returns a list of routes with the correct structure.
        results = find_routes(self.network, self.real_time_updates_no_delay, self.query)
        self.assertIsInstance(results, list, "find_routes should return a list of route options.")
        # Ensure at least one route option is returned.
        self.assertGreater(len(results), 0, "Expected at least one route option.")
        for route in results:
            self.validate_route_option(route)

    def test_transfer_penalty_effect(self):
        # Test that when multiple transfers are involved, the total time increases appropriately.
        results = find_routes(self.network, self.real_time_updates_no_delay, self.query)
        # Identify routes with and without transfers if possible.
        route_with_transfer = None
        route_direct = None
        for route in results:
            if len(route["lines"]) > 1:
                route_with_transfer = route
            elif len(route["lines"]) == 1:
                route_direct = route
        # If both types exist, a route with transfer should have increased total_time by at least one transfer penalty.
        if route_with_transfer and route_direct:
            self.assertGreaterEqual(route_with_transfer["total_time"], 
                                    route_direct["total_time"] + 5,
                                    "Route with transfer should add at least a 5 minute penalty.")

    def test_real_time_delay_influence(self):
        # Test that a delay update on a particular line affects the computed total_time.
        results_no_delay = find_routes(self.network, self.real_time_updates_no_delay, self.query)
        results_delay = find_routes(self.network, self.real_time_updates_delay, self.query)

        # For routes that use Subway_1, the delayed version should have a higher total_time.
        for route_no, route_delay in zip(results_no_delay, results_delay):
            # Check if Subway_1 is in the route lines; if so, then delay should have impacted total time.
            if "Subway_1" in route_no["lines"]:
                self.assertGreater(route_delay["total_time"],
                                   route_no["total_time"],
                                   "Expected total_time to increase due to delay on Subway_1.")

    def test_dynamic_pricing_effect(self):
        # Test that pricing rules are applied appropriately during peak hours.
        # Create an update to simulate surge pricing.
        real_time_updates_surge = {
            "delays": {
                "Bus_1": 0,
                "Subway_1": 0,
                "Train_1": 0
            },
            "pricing_updates": {
                "surge": {"multiplier": 2.0}  # simulate surge pricing doubling the fare.
            }
        }
        results_normal = find_routes(self.network, self.real_time_updates_no_delay, self.query)
        results_surge = find_routes(self.network, real_time_updates_surge, self.query)

        # For each corresponding route, the fare under surge should be higher than under normal pricing.
        for route_normal, route_surge in zip(results_normal, results_surge):
            self.assertGreater(route_surge["total_fare"],
                               route_normal["total_fare"],
                               "Expected total_fare to increase under surge pricing conditions.")

    def test_options_ranking(self):
        # Test that the returned route options are ranked by a cost function that considers travel time, fare, and comfort.
        results = find_routes(self.network, self.real_time_updates_no_delay, self.query)
        # Check that the list is not empty.
        self.assertGreater(len(results), 0, "Expected at least one route option.")
        # Verify that the route options are sorted by a combined score (we assume lower is better).
        scores = [route["total_time"] + route["total_fare"] + route["comfort_score"] for route in results]
        self.assertEqual(scores, sorted(scores),
                         "Route options should be ranked in ascending order by the cost function (total_time + total_fare + comfort_score).")

if __name__ == '__main__':
    unittest.main()