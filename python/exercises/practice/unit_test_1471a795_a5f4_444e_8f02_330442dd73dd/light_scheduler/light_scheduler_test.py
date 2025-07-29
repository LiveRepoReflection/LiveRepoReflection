import unittest
from light_scheduler import optimal_average_travel_time

class TestLightScheduler(unittest.TestCase):
    def test_two_intersections_direct_route(self):
        # Two intersections connected by one road.
        n = 2
        m = 1
        # Road: between intersection 1 and 2 with travel time 10.
        roads = [
            (1, 2, 10)
        ]
        # Intersection definitions:
        # For intersection 1, no incoming roads matter (source).
        # For intersection 2, allow incoming from 1.
        intersections = {
            1: {
                'phases': [
                    (10, [])  # One phase of duration 10 with no relevant incoming roads.
                ]
            },
            2: {
                'phases': [
                    (10, [(1, 2)])  # One phase of duration 10 allowing traffic from 1.
                ]
            }
        }
        # One origin-destination pair: from 1 to 2 with a traffic volume of 5.
        q = 1
        od_pairs = [
            (1, 2, 5)
        ]
        
        # For this simple schedule, the optimal average travel time should be 10.0 seconds.
        expected = 10.0
        result = optimal_average_travel_time(n, m, roads, intersections, od_pairs)
        self.assertAlmostEqual(result, expected, places=6)

    def test_four_intersections_indirect_route(self):
        # Four intersections with two possible routes.
        n = 4
        m = 4
        # Define roads: a shorter path via intersections 1-2-3-4 and a direct longer road 1-4.
        roads = [
            (1, 2, 5),
            (2, 3, 5),
            (3, 4, 5),
            (1, 4, 20)
        ]
        # Define intersections with one-phase cycles designed such that waiting times are minimized.
        intersections = {
            1: {
                'phases': [
                    (10, [])  # Intersection 1 as origin.
                ]
            },
            2: {
                'phases': [
                    (10, [(1, 2), (3, 2)])  # Allowing traffic from 1 and 3.
                ]
            },
            3: {
                'phases': [
                    (10, [(2, 3), (4, 3)])  # Allowing traffic from 2 and 4.
                ]
            },
            4: {
                'phases': [
                    (10, [(3, 4), (1, 4)])  # Allowing traffic from 3 and 1.
                ]
            }
        }
        # A single O-D pair with high traffic volume to encourage the shorter route.
        q = 1
        od_pairs = [
            (1, 4, 10)
        ]
        
        # The optimal schedule should favor route 1-2-3-4 with a travel time of 15 seconds.
        expected = 15.0
        result = optimal_average_travel_time(n, m, roads, intersections, od_pairs)
        self.assertAlmostEqual(result, expected, places=6)
        
    def test_disconnected_network(self):
        # Test where one O-D pair is disconnected.
        n = 3
        m = 1
        roads = [
            (1, 2, 5)
        ]
        # Intersection definitions (all intersections still must have a schedule).
        intersections = {
            1: {
                'phases': [
                    (10, [])
                ]
            },
            2: {
                'phases': [
                    (10, [(1, 2)])
                ]
            },
            3: {
                'phases': [
                    (10, [])
                ]
            }
        }
        # Two O-D pairs. The second pair from 2 to 3 is disconnected.
        q = 2
        od_pairs = [
            (1, 2, 5),
            (2, 3, 5)
        ]
        
        # For a disconnected route, it is ignored. Thus the average should consider only the valid route:
        # For (1,2): travel time = 5 seconds.
        expected = 5.0
        result = optimal_average_travel_time(n, m, roads, intersections, od_pairs)
        self.assertAlmostEqual(result, expected, places=6)

if __name__ == '__main__':
    unittest.main()