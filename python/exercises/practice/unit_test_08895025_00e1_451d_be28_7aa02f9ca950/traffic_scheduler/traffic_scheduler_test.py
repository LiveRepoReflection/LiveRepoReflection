import unittest
import math
from traffic_scheduler import optimize_traffic

class TrafficSchedulerTest(unittest.TestCase):
    def test_simple_network(self):
        # Two intersections with a bidirectional connection. 
        # Cycle length C = 10. One phase each, allowing immediate movement.
        N = 2
        roads = [
            (0, 1, 5),
            (1, 0, 5)
        ]
        phases = {
            0: [({1}, {1}, 10)],
            1: [({0}, {0}, 10)]
        }
        # Expected: minimal average travel time = (5 + 5) / 2 = 5.0 seconds
        result = optimize_traffic(N, roads, phases)
        self.assertAlmostEqual(result, 5.0, places=6)

    def test_three_node_cycle(self):
        # Graph: 3 intersections with multiple paths.
        # Roads: direct and indirect connections.
        N = 3
        roads = [
            (0, 1, 3),
            (1, 2, 4),
            (2, 0, 5),
            (0, 2, 10),
            (2, 1, 7)
        ]
        # For simplicity, assign one phase per intersection with full permission,
        # so vehicles essentially travel with no additional waiting time.
        # Cycle length C = 10, phase duration = 10 for each.
        phases = {
            0: [({1, 2}, {1, 2}, 10)],
            1: [({0, 2}, {0, 2}, 10)],
            2: [({0, 1}, {0, 1}, 10)]
        }
        # Compute the expected shortest distances:
        # 0 -> 1: 3; 0 -> 2: min(10, 3+4 = 7)
        # 1 -> 2: 4; 1 -> 0: 4+5 = 9
        # 2 -> 0: 5; 2 -> 1: min(7, 5+3 = 8) = 7
        # Sum = 3 + 7 + 9 + 4 + 5 + 7 = 35; average = 35 / 6 ≈ 5.833333
        expected_average = 35 / 6
        result = optimize_traffic(N, roads, phases)
        self.assertAlmostEqual(result, expected_average, places=6)

    def test_unreachable_network(self):
        # Graph with 3 intersections where one pair is unreachable.
        # Even though the problem expects a strongly connected graph,
        # we test that the function returns float('inf') when unreachable.
        N = 3
        roads = [
            (0, 1, 5)
        ]
        # Dummy phases with cycle length C = 10. These phases are provided,
        # but the graph is not strongly connected.
        phases = {
            0: [({1}, {1}, 10)],
            1: [({0}, {0}, 10)],
            2: [({0}, {0}, 10)]
        }
        result = optimize_traffic(N, roads, phases)
        self.assertTrue(math.isinf(result))

if __name__ == '__main__':
    unittest.main()