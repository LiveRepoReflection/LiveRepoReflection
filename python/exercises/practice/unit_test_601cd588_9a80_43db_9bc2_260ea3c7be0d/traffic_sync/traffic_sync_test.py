import unittest
from traffic_sync import optimize_traffic_lights


class TrafficSyncTest(unittest.TestCase):
    def test_single_intersection_one_trip(self):
        N = 1
        edges = []  # No roads, just one intersection
        trips = [(0, 0, 100)]  # Trip from and to the same intersection
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        self.assertEqual(len(light_durations[0]), 2)
        self.assertTrue(min_duration <= light_durations[0][0] <= max_duration)
        self.assertTrue(min_duration <= light_durations[0][1] <= max_duration)

    def test_simple_linear_path(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 7)]  # Linear path: 0 -> 1 -> 2
        trips = [(0, 2, 100)]  # Trip from 0 to 2
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_simple_loop(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 7), (2, 0, 6)]  # Loop: 0 -> 1 -> 2 -> 0
        trips = [(0, 2, 50), (1, 0, 70)]
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_disconnected_graph(self):
        N = 4
        edges = [(0, 1, 5), (2, 3, 7)]  # Two separate components
        trips = [(0, 1, 100), (2, 3, 150)]  # Trips within components
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_impossible_trip(self):
        N = 4
        edges = [(0, 1, 5), (2, 3, 7)]  # Two separate components
        trips = [(0, 3, 100)]  # Trip between disconnected components
        min_duration = 10
        max_duration = 30
        
        # The function should handle this gracefully, not throw an error
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_multiple_paths(self):
        N = 4
        # Diamond shape with different path lengths
        edges = [(0, 1, 5), (0, 2, 10), (1, 3, 15), (2, 3, 5)]
        trips = [(0, 3, 100)]
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_complex_city_grid(self):
        N = 9
        # 3x3 grid with bidirectional roads
        edges = [
            (0, 1, 5), (1, 0, 5), (1, 2, 5), (2, 1, 5),
            (0, 3, 5), (3, 0, 5), (1, 4, 5), (4, 1, 5), (2, 5, 5), (5, 2, 5),
            (3, 4, 5), (4, 3, 5), (4, 5, 5), (5, 4, 5),
            (3, 6, 5), (6, 3, 5), (4, 7, 5), (7, 4, 5), (5, 8, 5), (8, 5, 5),
            (6, 7, 5), (7, 6, 5), (7, 8, 5), (8, 7, 5)
        ]
        trips = [
            (0, 8, 100),  # Diagonal trip across grid
            (2, 6, 80),   # Diagonal trip across grid
            (1, 7, 120),  # Vertical trip through middle
            (3, 5, 90)    # Horizontal trip through middle
        ]
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_no_trips(self):
        N = 5
        edges = [(0, 1, 5), (1, 2, 7), (2, 3, 6), (3, 4, 8)]
        trips = []  # No trips
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)

    def test_min_equals_max_duration(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 7)]
        trips = [(0, 2, 100)]
        min_duration = 20
        max_duration = 20  # min equals max
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertEqual(light[0], 20)
            self.assertEqual(light[1], 20)

    def test_large_input(self):
        N = 50
        edges = [(i, i+1, 5) for i in range(N-1)]  # Linear path
        trips = [(0, N-1, 100)]  # One long trip
        min_duration = 10
        max_duration = 30
        
        light_durations = optimize_traffic_lights(N, edges, trips, min_duration, max_duration)
        
        self.assertEqual(len(light_durations), N)
        for light in light_durations:
            self.assertEqual(len(light), 2)
            self.assertTrue(min_duration <= light[0] <= max_duration)
            self.assertTrue(min_duration <= light[1] <= max_duration)


if __name__ == "__main__":
    unittest.main()