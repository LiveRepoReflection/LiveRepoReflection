import unittest
from optimal_meeting import optimal_meeting_point

class TestOptimalMeeting(unittest.TestCase):
    def test_single_node(self):
        n = 1
        edges = []
        w = [5]
        self.assertEqual(optimal_meeting_point(n, edges, w), 0)

    def test_two_nodes_equal_weight(self):
        n = 2
        edges = [[0, 1, 10]]
        w = [3, 3]
        self.assertEqual(optimal_meeting_point(n, edges, w), 0)

    def test_star_graph(self):
        n = 4
        edges = [[0, 1, 2], [0, 2, 2], [0, 3, 2]]
        w = [1, 10, 10, 10]
        self.assertEqual(optimal_meeting_point(n, edges, w), 0)

    def test_line_graph(self):
        n = 5
        edges = [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1]]
        w = [1, 2, 3, 2, 1]
        self.assertEqual(optimal_meeting_point(n, edges, w), 2)

    def test_complex_tree(self):
        n = 7
        edges = [
            [0, 1, 3],
            [0, 2, 2],
            [1, 3, 1],
            [1, 4, 4],
            [2, 5, 5],
            [2, 6, 6]
        ]
        w = [2, 3, 1, 4, 5, 2, 3]
        self.assertEqual(optimal_meeting_point(n, edges, w), 1)

    def test_large_edge_costs(self):
        n = 3
        edges = [[0, 1, 1000], [1, 2, 1000]]
        w = [1, 100, 1]
        self.assertEqual(optimal_meeting_point(n, edges, w), 1)

    def test_tie_breaker(self):
        n = 4
        edges = [[0, 1, 1], [1, 2, 1], [2, 3, 1]]
        w = [1, 1, 1, 1]
        self.assertEqual(optimal_meeting_point(n, edges, w), 1)

    def test_unbalanced_weights(self):
        n = 6
        edges = [
            [0, 1, 2],
            [1, 2, 3],
            [2, 3, 1],
            [3, 4, 4],
            [4, 5, 2]
        ]
        w = [1, 1, 100, 1, 1, 1]
        self.assertEqual(optimal_meeting_point(n, edges, w), 2)

if __name__ == '__main__':
    unittest.main()