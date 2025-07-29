import unittest
from island_network import island_network

class TestIslandNetwork(unittest.TestCase):
    def test_two_islands_possible(self):
        # Two islands with one possible tunnel
        N = 2
        B = 50
        C = [
            [0, 20],
            [20, 0]
        ]
        T = [
            [0, 5],
            [5, 0]
        ]
        # Only one tunnel needed: cost 20, time 5, which is within budget.
        self.assertEqual(island_network(N, B, C, T), 5)

    def test_example_case(self):
        # The provided example case in the description.
        N = 4
        B = 100
        C = [
            [0, 20, 30, 40],
            [20, 0, 30, 30],
            [30, 30, 0, 20],
            [40, 30, 20, 0]
        ]
        T = [
            [0, 5, 7, 9],
            [5, 0, 6, 6],
            [7, 6, 0, 4],
            [9, 6, 4, 0]
        ]
        self.assertEqual(island_network(N, B, C, T), 15)

    def test_insufficient_budget(self):
        # A configuration where the only available tunnels exceed the budget.
        N = 3
        B = 10  # Too low budget to connect all islands
        C = [
            [0, 15, 20],
            [15, 0, 25],
            [20, 25, 0]
        ]
        T = [
            [0, 5, 7],
            [5, 0, 10],
            [7, 10, 0]
        ]
        self.assertEqual(island_network(N, B, C, T), -1)

    def test_no_possible_connection(self):
        # Case where some tunnels are not possible (-1 indicates tunnel cannot be built)
        N = 4
        B = 100
        # In this case, some connections are missing.
        C = [
            [0, 20, -1, 40],
            [20, 0, 30, -1],
            [-1, 30, 0, 20],
            [40, -1, 20, 0]
        ]
        T = [
            [0, 5, -1, 9],
            [5, 0, 6, -1],
            [-1, 6, 0, 4],
            [9, -1, 4, 0]
        ]
        # Only possible network uses tunnels:
        # 1-2: cost 20, time 5; 2-3: cost 30, time 6; 3-4: cost 20, time 4.
        # Total cost = 70, total time = 15.
        self.assertEqual(island_network(N, B, C, T), 15)

    def test_complex_case_multiple_choices(self):
        # A more complex test with multiple potential spanning trees.
        N = 5
        B = 150
        C = [
            [0,  10,  50,  40,  90],
            [10, 0,   20,  70,  80],
            [50, 20,  0,   30,  60],
            [40, 70,  30,  0,   20],
            [90, 80,  60,  20,  0]
        ]
        T = [
            [0,  4,  12, 10, 15],
            [4,  0,  5,  11, 13],
            [12, 5,  0,  3,  8],
            [10, 11, 3,  0,  2],
            [15, 13, 8,  2,  0]
        ]
        # In this network, several spanning trees are possible.
        # One optimal choice (one possibility) could be:
        # 1-2: cost 10, time 4; 2-3: cost 20, time 5; 3-4: cost 30, time 3; 4-5: cost 20, time 2.
        # Total cost = 10 + 20 + 30 + 20 = 80 (<= 150), total time = 4 + 5 + 3 + 2 = 14.
        self.assertEqual(island_network(N, B, C, T), 14)

if __name__ == '__main__':
    unittest.main()