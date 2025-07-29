import unittest
from city_rescue import min_total_weighted_response_time

class TestCityRescue(unittest.TestCase):
    def test_example_case(self):
        N = 5
        roads = [(0, 1, 10), (1, 2, 10), (2, 3, 10), (3, 4, 10), (0, 4, 20)]
        damaged_roads = [(0, 1, 15), (2, 4, 5)]
        H = [0, 3]
        emergency_requests = [(1, 5), (4, 8)]
        expected = 155
        result = min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests)
        self.assertEqual(result, expected)

    def test_no_damage(self):
        N = 4
        roads = [(0, 1, 5), (1, 2, 10), (2, 3, 5), (3, 0, 10)]
        damaged_roads = []
        H = [0]
        emergency_requests = [(2, 3)]
        # Shortest path from hospital 0 to emergency 2: 0 -> 1 -> 2: 5 + 10 = 15, response time = 15 * 3 = 45
        expected = 45
        result = min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests)
        self.assertEqual(result, expected)

    def test_multiple_hospitals(self):
        N = 6
        roads = [(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2), (4, 5, 2), (0, 5, 10)]
        damaged_roads = [(0, 1, 3)]
        H = [0, 3]
        emergency_requests = [(2, 4), (5, 2)]
        # Emergency (2,4):
        #   From hospital 0: 0 -> 1 (3) + 1 -> 2 (2) = 5, cost = 5 * 4 = 20
        #   From hospital 3: 3 -> 2 (2) = 2, cost = 2 * 4 = 8  => choose hospital 3
        # Emergency (5,2):
        #   From hospital 0: best path = 0 -> 5 (10) = 10, cost = 10 * 2 = 20
        #   From hospital 3: 3 -> 4 (2) + 4 -> 5 (2) = 4, cost = 4 * 2 = 8  => choose hospital 3
        # Total expected = 8 + 8 = 16
        expected = 16
        result = min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests)
        self.assertEqual(result, expected)

    def test_complex_graph(self):
        N = 8
        roads = [(0, 1, 3), (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 7), (5, 6, 8), (6, 7, 9), (0, 7, 15)]
        damaged_roads = [(2, 3, 3), (4, 5, 4), (5, 6, 6)]
        H = [0, 4]
        emergency_requests = [(3, 5), (7, 2), (2, 10)]
        # Calculation:
        # For hospital 0:
        #   To 3: 0->1->2->3: 3 + 4 + 3 = 10 --> 10 * 5 = 50
        #   To 7: direct 15 --> 15 * 2 = 30
        #   To 2: 0->1->2: 3 + 4 = 7 --> 7 * 10 = 70
        # For hospital 4:
        #   To 3: 4->3: 6 (undamaged) or 4->3 route via other nodes may be longer --> 6 * 5 = 30
        #   To 7: 4->5->6->7: 4 + 6 + 9 = 19 --> 19 * 2 = 38
        #   To 2: 4->3->2: 6 + 3 = 9 --> 9 * 10 = 90
        # Best assignment:
        #   Emergency (3, 5): hospital 4 gives 30.
        #   Emergency (7, 2): hospital 0 gives 30.
        #   Emergency (2, 10): hospital 0 gives 70.
        # Total expected = 30 + 30 + 70 = 130
        expected = 130
        result = min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests)
        self.assertEqual(result, expected)

    def test_updated_edge_addition(self):
        N = 4
        roads = [(0, 1, 10), (1, 2, 10)]
        damaged_roads = [(2, 3, 5)]  # This road is newly added.
        H = [0]
        emergency_requests = [(3, 2)]
        # Shortest path: 0->1->2: 10 + 10 = 20, then 2->3: 5, total = 25, and response time = 25 * 2 = 50
        expected = 50
        result = min_total_weighted_response_time(N, roads, damaged_roads, H, emergency_requests)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()