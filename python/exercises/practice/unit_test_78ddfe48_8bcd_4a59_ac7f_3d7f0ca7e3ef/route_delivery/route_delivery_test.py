import unittest
from route_delivery import min_trips

class RouteDeliveryTest(unittest.TestCase):
    def test_single_trip_possible(self):
        # Simple graph with one valid path where one trip is sufficient.
        N = 3
        S = 0
        D = 2
        # Path: 0 -> 1 -> 2, capacities are high enough and latency is within limit.
        edges = [
            (0, 1, 10, 10),
            (1, 2, 10, 10)
        ]
        delivery_units = 5
        max_latency = 25  # Total latency along the only path = 20 which is <= 25.
        expected = 1
        self.assertEqual(min_trips(N, S, D, edges, delivery_units, max_latency), expected)

    def test_no_route_within_latency(self):
        # Graph with a valid path structure but the only available path exceeds max_latency.
        N = 3
        S = 0
        D = 2
        edges = [
            (0, 1, 10, 10),
            (1, 2, 10, 50)  # Total latency = 60
        ]
        delivery_units = 5
        max_latency = 55  # 60 > 55, so no valid path.
        expected = -1
        self.assertEqual(min_trips(N, S, D, edges, delivery_units, max_latency), expected)

    def test_multiple_trips_required(self):
        # Graph where the only path's capacity is less than required delivery_units so multiple trips are needed.
        N = 3
        S = 0
        D = 2
        edges = [
            (0, 1, 3, 5),
            (1, 2, 3, 5)
        ]
        delivery_units = 7
        max_latency = 15  # Total latency = 10 which is <= 15.
        # Bottleneck capacity is 3, so trips = ceil(7/3) = 3.
        expected = 3
        self.assertEqual(min_trips(N, S, D, edges, delivery_units, max_latency), expected)

    def test_multiple_paths_choose_optimal(self):
        # Graph with two valid paths from S to D.
        N = 4
        S = 0
        D = 3
        edges = [
            # Path A: 0 -> 1 -> 3 with bottleneck capacity 3 and low latency.
            (0, 1, 3, 5),
            (1, 3, 3, 5),
            # Path B: 0 -> 2 -> 3 with higher capacity 5 but slightly higher latency.
            (0, 2, 5, 15),
            (2, 3, 5, 2)
        ]
        delivery_units = 8
        max_latency = 20  # Path A has latency 10; Path B has latency 17.
        # Optimal is Path B: trips = ceil(8/5) = 2, while Path A would need 3.
        expected = 2
        self.assertEqual(min_trips(N, S, D, edges, delivery_units, max_latency), expected)

    def test_disconnected_graph(self):
        # Graph where D is unreachable from S.
        N = 4
        S = 0
        D = 3
        edges = [
            (0, 1, 5, 10),
            (1, 2, 5, 10)
            # No edge leads to city 3.
        ]
        delivery_units = 10
        max_latency = 50
        expected = -1
        self.assertEqual(min_trips(N, S, D, edges, delivery_units, max_latency), expected)

if __name__ == '__main__':
    unittest.main()