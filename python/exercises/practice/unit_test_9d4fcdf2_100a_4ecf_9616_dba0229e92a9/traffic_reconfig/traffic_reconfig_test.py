import unittest
from traffic_reconfig import optimal_traffic_flow

class TrafficReconfigTest(unittest.TestCase):
    def test_single_edge(self):
        # Single edge, single OD pair, no capacity change allowed.
        n = 2
        edges = [
            (0, 1, 10, 5)  # from node 0 to node 1, capacity 10, travel time 5
        ]
        od_pairs = [
            (0, 1, 5)     # demand of 5 vehicles from node 0 to node 1
        ]
        max_capacity_changes = 0
        # All vehicles take the only available edge.
        expected_total_time = 5 * 5  # 5 vehicles * travel time 5
        self.assertEqual(optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes), expected_total_time)

    def test_basic_graph_no_change(self):
        # Graph with two possible paths, using no capacity changes.
        n = 4
        edges = [
            (0, 1, 10, 5),
            (0, 2, 15, 3),
            (1, 3, 7, 4),
            (2, 3, 12, 2)
        ]
        od_pairs = [
            (0, 3, 8)
        ]
        max_capacity_changes = 0
        # Optimal is to send all demand via path 0->2->3 with cost (3+2)=5 per vehicle.
        expected_total_time = 8 * 5  # 40
        self.assertEqual(optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes), expected_total_time)

    def test_basic_graph_with_change(self):
        # Same graph as previous, but allowing one capacity change.
        # Even with capacity changes allowed, the optimal routing remains on the faster route.
        n = 4
        edges = [
            (0, 1, 10, 5),
            (0, 2, 15, 3),
            (1, 3, 7, 4),
            (2, 3, 12, 2)
        ]
        od_pairs = [
            (0, 3, 8)
        ]
        max_capacity_changes = 1
        expected_total_time = 8 * 5  # Still 40, as the faster route remains best.
        self.assertEqual(optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes), expected_total_time)

    def test_multi_od_pairs(self):
        # Graph with multiple origin-destination pairs.
        n = 6
        edges = [
            (0, 1, 6, 2),
            (1, 2, 6, 2),
            (0, 3, 8, 3),
            (3, 2, 8, 1),
            (2, 4, 10, 2),
            (1, 5, 6, 4),
            (5, 4, 6, 3),
            (3, 4, 8, 3)
        ]
        od_pairs = [
            (0, 4, 10),
            (0, 2, 3)
        ]
        max_capacity_changes = 1
        # For this configuration, assume the optimal total travel time is computed as follows:
        # OD (0,4): best achievable with travel time 6 per vehicle = 10 * 6 = 60
        # OD (0,2): best achievable with travel time 4 per vehicle = 3 * 4 = 12
        # Total expected = 60 + 12 = 72
        expected_total_time = 72
        self.assertEqual(optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes), expected_total_time)

    def test_trivial_case(self):
        # Trivial case with a single intersection; no travel required.
        n = 1
        edges = []
        od_pairs = [
            (0, 0, 10)
        ]
        max_capacity_changes = 0
        # No travel is needed if origin and destination are the same.
        expected_total_time = 0
        self.assertEqual(optimal_traffic_flow(n, edges, od_pairs, max_capacity_changes), expected_total_time)

if __name__ == '__main__':
    unittest.main()