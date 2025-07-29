import unittest
import math
from optimal_route import plan_routes

class TestOptimalRoute(unittest.TestCase):
    def assertFloatAlmostEqual(self, a, b, tol=1e-6):
        self.assertTrue(math.isclose(a, b, abs_tol=tol), f"{a} != {b} within tolerance {tol}")

    def test_simple_route_no_waiting(self):
        # Graph: single edge from 1 to 2, distance 10, constant traffic multiplier 1 over full time.
        city_graph = {
            "nodes": [1, 2],
            "edges": [
                {
                    "src": 1,
                    "dest": 2,
                    "distance": 10,
                    "traffic": [(0, 1000, 1)]
                }
            ]
        }
        # Drone info: one drone starting at node 1, schedule: destination 2 within window (0, 100) and turnaround 5.
        drones = [
            {
                "id": "drone1",
                "start": 1,
                "schedule": [
                    {
                        "destination": 2,
                        "time_window": (0, 100),
                        "turnaround": 5
                    }
                ]
            }
        ]
        base_speed = 10  # distance units per time unit (10 units / 10 = 1 time unit travel)

        result = plan_routes(city_graph, drones, base_speed)
        # Expected: route for drone1: Arrive at node 2 at time = 1 (travel time = 10/10 = 1, no waiting).
        expected = {"drone1": [(2, 1.0)]}
        self.assertEqual(len(result), 1)
        self.assertIn("drone1", result)
        self.assertEqual(len(result["drone1"]), 1)
        dest, arrival = result["drone1"][0]
        self.assertEqual(dest, expected["drone1"][0][0])
        self.assertFloatAlmostEqual(arrival, expected["drone1"][0][1])

    def test_route_with_waiting(self):
        # Graph: single edge from 1 to 2 with distance 10, constant multiplier 1.
        city_graph = {
            "nodes": [1, 2],
            "edges": [
                {
                    "src": 1,
                    "dest": 2,
                    "distance": 10,
                    "traffic": [(0, 1000, 1)]
                }
            ]
        }
        # Drone: Must not arrive until time 5.
        drones = [
            {
                "id": "drone2",
                "start": 1,
                "schedule": [
                    {
                        "destination": 2,
                        "time_window": (5, 20),
                        "turnaround": 3
                    }
                ]
            }
        ]
        base_speed = 10  # travel time = 10/10 = 1, but window forces waiting until time 5.

        result = plan_routes(city_graph, drones, base_speed)
        # Expected: waiting required, so arrival recorded as 5.
        expected = {"drone2": [(2, 5.0)]}
        self.assertEqual(len(result), 1)
        self.assertIn("drone2", result)
        self.assertEqual(len(result["drone2"]), 1)
        dest, arrival = result["drone2"][0]
        self.assertEqual(dest, expected["drone2"][0][0])
        self.assertFloatAlmostEqual(arrival, expected["drone2"][0][1])

    def test_alternative_path_selection(self):
        # Graph: Three nodes with two paths from 1 to 3.
        # Path A: 1 -> 3 directly, distance 12.
        # Path B: 1 -> 2 -> 3, distances 5 and 5.
        # Both edges have constant multiplier 1.
        city_graph = {
            "nodes": [1, 2, 3],
            "edges": [
                {
                    "src": 1,
                    "dest": 3,
                    "distance": 12,
                    "traffic": [(0, 1000, 1)]
                },
                {
                    "src": 1,
                    "dest": 2,
                    "distance": 5,
                    "traffic": [(0, 1000, 1)]
                },
                {
                    "src": 2,
                    "dest": 3,
                    "distance": 5,
                    "traffic": [(0, 1000, 1)]
                }
            ]
        }
        # Drone: start at node 1, schedule: destination 3 with wide time window.
        drones = [
            {
                "id": "drone3",
                "start": 1,
                "schedule": [
                    {
                        "destination": 3,
                        "time_window": (0, 100),
                        "turnaround": 2
                    }
                ]
            }
        ]
        base_speed = 5  # For direct route: 12/5 = 2.4, via 2: 5/5 + 5/5 = 1+1 = 2.
        # Expected: optimal route via node 2 should lead to arrival at 3 at time 2.
        expected = {"drone3": [(3, 2.0)]}
        result = plan_routes(city_graph, drones, base_speed)
        self.assertEqual(len(result), 1)
        self.assertIn("drone3", result)
        self.assertEqual(len(result["drone3"]), 1)
        dest, arrival = result["drone3"][0]
        self.assertEqual(dest, expected["drone3"][0][0])
        self.assertFloatAlmostEqual(arrival, expected["drone3"][0][1])

    def test_multiple_stops_route(self):
        # Graph: A more complex graph for multiple stops.
        city_graph = {
            "nodes": [1, 2, 3, 4],
            "edges": [
                {"src": 1, "dest": 2, "distance": 4, "traffic": [(0, 1000, 1)]},
                {"src": 2, "dest": 3, "distance": 6, "traffic": [(0, 1000, 1)]},
                {"src": 3, "dest": 4, "distance": 5, "traffic": [(0, 1000, 1)]},
                {"src": 1, "dest": 4, "distance": 20, "traffic": [(0, 1000, 1)]}
            ]
        }
        drones = [
            {
                "id": "drone4",
                "start": 1,
                "schedule": [
                    {
                        "destination": 2,
                        "time_window": (0, 10),
                        "turnaround": 1
                    },
                    {
                        "destination": 3,
                        "time_window": (6, 20),
                        "turnaround": 2
                    },
                    {
                        "destination": 4,
                        "time_window": (12, 40),
                        "turnaround": 0
                    }
                ]
            }
        ]
        base_speed = 2  # slower speed
        # Calculate expected:
        # Leg1: 1 -> 2: time = 4/2 = 2.0, arrival 2.0 (within window (0,10)), finish turnaround at 3.0.
        # Leg2: 2 -> 3: time = 6/2 = 3.0, depart at 3.0, arrival at 6.0 (exactly at lower bound),
        # finish turnaround at 8.0.
        # Leg3: 3 -> 4: time = 5/2 = 2.5, depart at 8.0, arrival at 10.5 which is within window (12,40),
        # but arrives earlier than window start, so wait until 12.0.
        # Therefore, final arrival at 4 is 12.0.
        expected = {"drone4": [(2, 2.0), (3, 6.0), (4, 12.0)]}
        result = plan_routes(city_graph, drones, base_speed)
        self.assertEqual(len(result), 1)
        self.assertIn("drone4", result)
        self.assertEqual(len(result["drone4"]), 3)
        for (exp_dest, exp_time), (res_dest, res_time) in zip(expected["drone4"], result["drone4"]):
            self.assertEqual(exp_dest, res_dest)
            self.assertFloatAlmostEqual(exp_time, res_time)

    def test_impossible_schedule(self):
        # Graph: Two nodes, edge from 1->2.
        city_graph = {
            "nodes": [1, 2],
            "edges": [
                {
                    "src": 1,
                    "dest": 2,
                    "distance": 15,
                    "traffic": [(0, 1000, 1)]
                }
            ]
        }
        # Drone: the required time window is not achievable: window (0, 1) but travel time is >1.
        drones = [
            {
                "id": "drone5",
                "start": 1,
                "schedule": [
                    {
                        "destination": 2,
                        "time_window": (0, 1),
                        "turnaround": 0
                    }
                ]
            }
        ]
        base_speed = 10  # travel time = 15/10 = 1.5 > window end.
        
        result = plan_routes(city_graph, drones, base_speed)
        # If a drone cannot complete its delivery schedule, the returned list should be empty.
        expected = {"drone5": []}
        self.assertEqual(len(result), 1)
        self.assertIn("drone5", result)
        self.assertEqual(result["drone5"], expected["drone5"])

    def test_multiple_drones(self):
        # Graph: Four nodes, multiple edges.
        city_graph = {
            "nodes": [1, 2, 3, 4],
            "edges": [
                {"src": 1, "dest": 2, "distance": 3, "traffic": [(0, 1000, 1)]},
                {"src": 2, "dest": 3, "distance": 4, "traffic": [(0, 1000, 1)]},
                {"src": 3, "dest": 4, "distance": 5, "traffic": [(0, 1000, 1)]},
                {"src": 1, "dest": 4, "distance": 15, "traffic": [(0, 1000, 1)]}
            ]
        }
        drones = [
            {
                "id": "drone6",
                "start": 1,
                "schedule": [
                    {
                        "destination": 4,
                        "time_window": (0, 50),
                        "turnaround": 2
                    }
                ]
            },
            {
                "id": "drone7",
                "start": 2,
                "schedule": [
                    {
                        "destination": 3,
                        "time_window": (0, 50),
                        "turnaround": 1
                    },
                    {
                        "destination": 4,
                        "time_window": (10, 60),
                        "turnaround": 0
                    }
                ]
            }
        ]
        base_speed = 3  # speed base

        # For drone6: Path options
        # Direct: 1 -> 4 = 15/3 = 5.0, arrival at 5.0.
        # Alternative: 1->2->3->4 = (3/3)+(4/3)+(5/3)= 1+1.33+1.67 = 4.0 approx, arrival at 4.0.
        # Optimal: choose 4.0 arrival.
        # For drone7: start at 2:
        # Leg1: 2->3 = 4/3 = 1.33, arrival at 1.33 which is within time window (0,50), turnaround 1 => depart at 2.33.
        # Leg2: 3->4 = 5/3 = 1.67, arrival at 2.33+1.67 = 4.0. But the window for delivery at 4 is (10,60),
        # so wait until 10.0.
        expected = {
            "drone6": [(4, 4.0)],  # arriving via optimal route with arrival time approx 4.0.
            "drone7": [(3, 1.33), (4, 10.0)]
        }
        result = plan_routes(city_graph, drones, base_speed)
        # Validate drone6 route
        self.assertIn("drone6", result)
        self.assertEqual(len(result["drone6"]), 1)
        d6_dest, d6_arrival = result["drone6"][0]
        self.assertEqual(d6_dest, expected["drone6"][0][0])
        self.assertFloatAlmostEqual(d6_arrival, expected["drone6"][0][1], tol=0.1)
        # Validate drone7 route
        self.assertIn("drone7", result)
        self.assertEqual(len(result["drone7"]), 2)
        d7_stop1 = result["drone7"][0]
        d7_stop2 = result["drone7"][1]
        self.assertEqual(d7_stop1[0], expected["drone7"][0][0])
        self.assertFloatAlmostEqual(d7_stop1[1], expected["drone7"][0][1], tol=0.1)
        self.assertEqual(d7_stop2[0], expected["drone7"][1][0])
        self.assertFloatAlmostEqual(d7_stop2[1], expected["drone7"][1][1], tol=0.1)

if __name__ == '__main__':
    unittest.main()