import unittest
from light_sync import optimal_travel_time

class LightSyncTest(unittest.TestCase):
    def test_same_intersection(self):
        # When source and destination are the same, no travel is needed.
        N = 1
        M = 0
        edges = []
        S = 0
        D = 0
        T = 10
        G = 3
        expected = 0
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

    def test_direct_edge_no_wait(self):
        # A simple case with one direct edge.
        # Graph: 0 -> 1 with travel time 5.
        # With proper offset assignment, arrival at 1 is exactly within the green interval.
        N = 2
        M = 1
        edges = [(0, 1, 5)]
        S = 0
        D = 1
        T = 10
        G = 5
        expected = 5
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

    def test_two_edge_path(self):
        # Graph: 0 -> 1 (4), 1 -> 2 (4)
        # Optimal offsets can be chosen so there is no waiting delay.
        N = 3
        M = 2
        edges = [(0, 1, 4), (1, 2, 4)]
        S = 0
        D = 2
        T = 10
        G = 3
        expected = 8
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

    def test_multiple_paths(self):
        # Graph with two different paths from 0 to 3.
        # Path 1: 0 -> 1 (5) -> 3 (5) total = 10 (with optimal offsets).
        # Path 2: 0 -> 2 (6) -> 3 (1) total = 7 (with optimal alignment).
        # The optimal maximum travel time is 7.
        N = 4
        M = 4
        edges = [(0, 1, 5), (1, 3, 5), (0, 2, 6), (2, 3, 1)]
        S = 0
        D = 3
        T = 10
        G = 3
        expected = 7
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

    def test_no_path(self):
        # Graph where there is no route from S to D.
        N = 3
        M = 1
        edges = [(0, 1, 5)]
        S = 0
        D = 2
        T = 10
        G = 3
        expected = -1
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

    def test_cycle_in_graph(self):
        # Graph with a cycle: 0 -> 1 -> 2 and 2 -> 1 forms a cycle; 1 -> 3 is the exit.
        # With optimal offset assignment:
        # Arrival at 1 from 0 takes 3 seconds.
        # Then going directly 1 -> 3, travel time is 6, total = 9 seconds.
        N = 4
        M = 4
        edges = [(0, 1, 3), (1, 2, 3), (2, 1, 1), (1, 3, 6)]
        S = 0
        D = 3
        T = 7
        G = 3
        expected = 9
        self.assertEqual(optimal_travel_time(N, M, edges, S, D, T, G), expected)

if __name__ == '__main__':
    unittest.main()