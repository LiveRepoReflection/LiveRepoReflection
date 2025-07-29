import unittest
import math

from optimal_rides.optimal_rides import plan_rides

class TestOptimalRides(unittest.TestCase):

    def setUp(self):
        # Define several sample graphs and ride requests for testing.

        # Graph 1: A simple two-node graph.
        # Graph structure: 0 -> 1 (travel time = 5)
        self.graph_simple = {
            0: [(1, 5)],
            1: []
        }
        self.requests_simple = [
            {"id": 1, "start": 0, "end": 1, "detour": 1.0}
        ]

        # Graph 2: A graph where start and end are the same node.
        self.graph_single = {
            0: []
        }
        self.requests_same = [
            {"id": 101, "start": 0, "end": 0, "detour": 1.0}
        ]

        # Graph 3: Disconnected graph.
        self.graph_disconnected = {
            0: [],
            1: []
        }
        self.requests_disconnected = [
            {"id": 201, "start": 0, "end": 1, "detour": 1.5}
        ]

        # Graph 4: More complex graph for potential ride sharing.
        # Graph structure:
        # 0 -> 1 (10), 0 -> 2 (5)
        # 1 -> 3 (10), 2 -> 3 (20)
        # 1 -> 2 (5), 2 -> 1 (5)
        self.graph_complex = {
            0: [(1, 10), (2, 5)],
            1: [(3, 10), (2, 5)],
            2: [(3, 20), (1, 5)],
            3: []
        }
        # Two ride requests with same start/end which might be grouped.
        self.requests_shared = [
            {"id": 301, "start": 0, "end": 3, "detour": 1.5},
            {"id": 302, "start": 0, "end": 3, "detour": 1.5}
        ]

    def validate_result_structure(self, result, request_id):
        # Each ride result must be a dict with keys: 'shared', 'travel_time', 'route', 'riders'
        self.assertIn("shared", result, f"Result for request {request_id} missing 'shared' key.")
        self.assertIn("travel_time", result, f"Result for request {request_id} missing 'travel_time' key.")
        self.assertIn("route", result, f"Result for request {request_id} missing 'route' key.")
        self.assertIn("riders", result, f"Result for request {request_id} missing 'riders' key.")

    def test_single_request(self):
        # Single ride request on a simple graph; expect direct ride with shortest path.
        results = plan_rides(self.graph_simple, self.requests_simple)
        self.assertIn(1, results)
        ride_result = results[1]
        self.validate_result_structure(ride_result, 1)
        # Expected ride: [0, 1] with travel_time 5, not shared.
        self.assertFalse(ride_result["shared"], "Single ride should not be marked as shared.")
        self.assertEqual(ride_result["travel_time"], 5, "Travel time for simple graph incorrect.")
        self.assertEqual(ride_result["route"], [0, 1], "Route for simple graph incorrect.")
        self.assertEqual(ride_result["riders"], [], "There should be no riders in a solo ride.")

    def test_same_start_end(self):
        # Ride request where start equals end; expect zero travel time.
        results = plan_rides(self.graph_single, self.requests_same)
        self.assertIn(101, results)
        ride_result = results[101]
        self.validate_result_structure(ride_result, 101)
        self.assertFalse(ride_result["shared"], "Ride with same start/end should not be shared.")
        self.assertEqual(ride_result["travel_time"], 0, "Travel time should be zero for same start and end.")
        self.assertEqual(ride_result["route"], [0], "Route should be only the single node for same start and end.")
        self.assertEqual(ride_result["riders"], [], "There should be no riders in a solo ride.")

    def test_disconnected_request(self):
        # Ride request where no path exists between start and end.
        results = plan_rides(self.graph_disconnected, self.requests_disconnected)
        self.assertIn(201, results)
        ride_result = results[201]
        self.validate_result_structure(ride_result, 201)
        # Assuming that an unreachable ride returns None route and travel_time as None or math.inf.
        self.assertIsNone(ride_result["route"], "Unreachable ride should return None route.")
        self.assertTrue(ride_result["travel_time"] is None or math.isinf(ride_result["travel_time"]),
                        "Unreachable ride should have travel_time as None or infinity.")
        self.assertFalse(ride_result["shared"], "Unreachable ride should not be shared.")
        self.assertEqual(ride_result["riders"], [], "There should be no riders for an unreachable ride.")

    def test_shared_ride(self):
        # Two ride requests with identical origin and destination that may share a ride.
        results = plan_rides(self.graph_complex, self.requests_shared)
        # Both requests should have a result.
        self.assertIn(301, results)
        self.assertIn(302, results)
        ride1 = results[301]
        ride2 = results[302]
        self.validate_result_structure(ride1, 301)
        self.validate_result_structure(ride2, 302)

        # They might get a shared ride if grouping respects the detour factor
        # Check that if marked as shared, each one's riders list includes the other.
        if ride1["shared"] or ride2["shared"]:
            self.assertTrue(ride1["shared"], "If any ride is shared, both should be marked shared.")
            self.assertTrue(ride2["shared"], "If any ride is shared, both should be marked shared.")
            self.assertIn(302, ride1["riders"], "Ride 301 should list ride 302 as shared partner.")
            self.assertIn(301, ride2["riders"], "Ride 302 should list ride 301 as shared partner.")
        else:
            # If not grouped, then each ride must be optimal solo ride.
            self.assertFalse(ride1["shared"], "Ride 301 expected to be solo if not grouped.")
            self.assertFalse(ride2["shared"], "Ride 302 expected to be solo if not grouped.")
            self.assertEqual(ride1["riders"], [], "Solo ride should not list any shared riders.")
            self.assertEqual(ride2["riders"], [], "Solo ride should not list any shared riders.")
            # In solo mode, travel time should equal the shortest path.
            expected_time = 20  # 0 -> 1 (10) + 1 -> 3 (10) as one optimal route
            self.assertEqual(ride1["travel_time"], expected_time, "Solo ride travel time incorrect for ride 301.")
            self.assertEqual(ride2["travel_time"], expected_time, "Solo ride travel time incorrect for ride 302.")
            self.assertEqual(ride1["route"], [0, 1, 3], "Solo ride route incorrect for ride 301.")
            self.assertEqual(ride2["route"], [0, 1, 3], "Solo ride route incorrect for ride 302.")

if __name__ == '__main__':
    unittest.main()