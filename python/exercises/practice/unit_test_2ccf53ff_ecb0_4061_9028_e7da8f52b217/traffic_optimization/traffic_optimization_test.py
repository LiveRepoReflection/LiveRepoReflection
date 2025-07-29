import unittest
from traffic_optimization import optimize_traffic_lights

class TrafficOptimizationTest(unittest.TestCase):
    def test_single_intersection(self):
        # Single node, no pairs exist so average travel time is 0.0.
        n = 1
        roads = []
        budget = 1
        delay = 5
        result = optimize_traffic_lights(n, roads, budget, delay)
        self.assertAlmostEqual(result, 0.000000, places=6)

    def test_triangle_graph(self):
        # Provided sample:
        # Graph: 0--10--1, 1--10--2, 0--15--2; budget = 1, delay = 5
        # Optimal is to not add any traffic lights:
        # Expected average = 11.666667
        n = 3
        roads = [(0, 1, 10), (1, 2, 10), (0, 2, 15)]
        budget = 1
        delay = 5
        result = optimize_traffic_lights(n, roads, budget, delay)
        self.assertAlmostEqual(result, 11.666667, places=6)

    def test_square_with_diagonal(self):
        # Graph: 4 nodes forming a square with an extra diagonal
        # Roads: 0-1:10, 1-2:10, 2-3:10, 3-0:10, and 0-2:15.
        # Budget=2, delay=5.
        # Without any traffic light, shortest paths:
        # 0-1=10, 0-2=15, 0-3=10; 1-2=10, 1-3=20; 2-3=10.
        # Total sum for unique pairs = (10 + 15 + 10 + 10 + 20 + 10) = 75;
        # Total for both directions = 150; Average = 150 / 12 = 12.5.
        n = 4
        roads = [(0, 1, 10), (1, 2, 10), (2, 3, 10), (3, 0, 10), (0, 2, 15)]
        budget = 2
        delay = 5
        result = optimize_traffic_lights(n, roads, budget, delay)
        self.assertAlmostEqual(result, 12.500000, places=6)

    def test_zero_delay(self):
        # When delay is 0, installing a traffic light does not add travel time.
        # With the triangle graph, the result should be same as no installation.
        n = 3
        roads = [(0, 1, 10), (1, 2, 10), (0, 2, 15)]
        budget = 1
        delay = 0
        result = optimize_traffic_lights(n, roads, budget, delay)
        self.assertAlmostEqual(result, 11.666667, places=6)

    def test_cycle_with_chords(self):
        # Graph: 5 nodes in a cycle with additional chords:
        # Roads: (0,1):3, (1,2):4, (2,3):5, (3,4):6, (4,0):7, (0,2):8, (1,3):9.
        # Budget = 2, delay = 2.
        # Calculated shortest distances:
        # 0-1: 3, 0-2: min(0-1-2=7, chord=8) = 7, 0-3: 12, 0-4: 7, 
        # 1-2: 4, 1-3: 9, 1-4: 10, 2-3: 5, 2-4: 11, 3-4: 6.
        # Sum unique pairs = 3+7+12+7+4+9+10+5+11+6 = 74.
        # Total for both directions = 148, average = 148 / 20 = 7.4.
        n = 5
        roads = [(0, 1, 3), (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 0, 7), (0, 2, 8), (1, 3, 9)]
        budget = 2
        delay = 2
        result = optimize_traffic_lights(n, roads, budget, delay)
        self.assertAlmostEqual(result, 7.400000, places=6)

if __name__ == '__main__':
    unittest.main()