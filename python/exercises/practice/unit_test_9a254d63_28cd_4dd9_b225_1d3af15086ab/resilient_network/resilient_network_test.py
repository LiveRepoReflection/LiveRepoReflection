import unittest
from resilient_network.resilient_network import min_links

class TestResilientNetwork(unittest.TestCase):
    def test_no_links(self):
        n = 3
        links = []
        max_cost = 100
        min_reliability = 0.5
        self.assertEqual(min_links(n, links, max_cost, min_reliability), -1)

    def test_two_nodes_success(self):
        n = 2
        links = [(0, 1, 10, 0.8)]
        max_cost = 10
        min_reliability = 0.8
        self.assertEqual(min_links(n, links, max_cost, min_reliability), 1)

    def test_two_nodes_fail_due_to_threshold(self):
        n = 2
        links = [(0, 1, 10, 0.5)]
        max_cost = 20
        min_reliability = 0.6
        self.assertEqual(min_links(n, links, max_cost, min_reliability), -1)

    def test_basic_cycle(self):
        n = 3
        links = [
            (0, 1, 5, 0.9),
            (1, 2, 5, 0.9),
            (0, 2, 20, 0.7)
        ]
        max_cost = 10
        min_reliability = 0.8
        # Using edges (0,1) and (1,2) gives a total cost of 10 and a reliability product of 0.9*0.9 = 0.81 >= 0.8.
        self.assertEqual(min_links(n, links, max_cost, min_reliability), 2)

    def test_sample(self):
        n = 4
        links = [
            (0, 1, 10, 0.9),
            (0, 2, 15, 0.8),
            (1, 2, 12, 0.7),
            (1, 3, 8, 0.95),
            (2, 3, 20, 0.6)
        ]
        max_cost = 40
        min_reliability = 0.65
        self.assertEqual(min_links(n, links, max_cost, min_reliability), 3)

    def test_cost_exceed(self):
        n = 3
        links = [
            (0, 1, 50, 0.9),
            (1, 2, 50, 0.9),
            (0, 2, 80, 0.95)
        ]
        max_cost = 30
        min_reliability = 0.8
        self.assertEqual(min_links(n, links, max_cost, min_reliability), -1)

    def test_multiple_approaches(self):
        n = 5
        links = [
            (0, 1, 10, 0.8),
            (1, 2, 10, 0.8),
            (2, 3, 10, 0.8),
            (3, 4, 10, 0.8),
            (0, 4, 50, 0.9),
            (1, 3, 20, 0.4),
            (0, 2, 15, 0.85)
        ]
        max_cost = 40
        min_reliability = 0.4
        # The minimal solution is to use the edges (0,1), (1,2), (2,3), (3,4) with total cost 40.
        self.assertEqual(min_links(n, links, max_cost, min_reliability), 4)

if __name__ == '__main__':
    unittest.main()