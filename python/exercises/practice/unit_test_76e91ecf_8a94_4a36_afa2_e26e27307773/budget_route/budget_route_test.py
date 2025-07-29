import unittest
from budget_route import budget_route

class TestBudgetRoute(unittest.TestCase):
    
    def test_valid_path_with_multiple_sources(self):
        # Graph:
        # 0 -> 1: time=10 toll=5
        # 1 -> 2: time=20 toll=10
        # 2 -> 3: time=10 toll=5
        # 3 -> 4: time=5 toll=2
        # 0 -> 2: time=25 toll=15
        # 2 -> 4: time=15 toll=8
        # Sources: 0 and 1, Destination: 4, Budget: 25, Checkpoints: [2, 3], P=1
        N = 5
        M = 6
        edges = [
            (0, 1, 10, 5),
            (1, 2, 20, 10),
            (2, 3, 10, 5),
            (3, 4, 5, 2),
            (0, 2, 25, 15),
            (2, 4, 15, 8)
        ]
        sources = [0, 1]
        D = 4
        B = 25
        checkpoints = [2, 3]
        P = 1
        # Expected: best route is from source 1:
        # 1 -> 2 -> 3 -> 4 with total time = 20 + 10 + 5 = 35 and toll = 10+5+2 = 17
        expected_time = 35
        self.assertEqual(budget_route(N, M, edges, sources, D, B, checkpoints, P), expected_time)

    def test_insufficient_checkpoints(self):
        # Graph:
        # 0 -> 1: time=5 toll=1
        # 1 -> 2: time=5 toll=1
        # Sources: [0], Destination: 2, Budget: 10, Checkpoints: [1], P=2
        N = 3
        M = 2
        edges = [
            (0, 1, 5, 1),
            (1, 2, 5, 1)
        ]
        sources = [0]
        D = 2
        B = 10
        checkpoints = [1]
        P = 2  # Only one checkpoint visited on the available path.
        expected_time = -1
        self.assertEqual(budget_route(N, M, edges, sources, D, B, checkpoints, P), expected_time)

    def test_exceed_budget(self):
        # Graph:
        # 0 -> 1: time=5 toll=50
        # 1 -> 2: time=5 toll=50
        # Sources: [0], Destination: 2, Budget: 80, Checkpoints: [1], P=1
        N = 3
        M = 2
        edges = [
            (0, 1, 5, 50),
            (1, 2, 5, 50)
        ]
        sources = [0]
        D = 2
        B = 80  # Total toll would be 100 which exceeds 80.
        checkpoints = [1]
        P = 1
        expected_time = -1
        self.assertEqual(budget_route(N, M, edges, sources, D, B, checkpoints, P), expected_time)

    def test_multiple_sources_alternative_routes(self):
        # Graph:
        # 0 -> 2: time=10 toll=10
        # 0 -> 3: time=20 toll=5
        # 1 -> 2: time=5 toll=1
        # 2 -> 4: time=15 toll=5
        # 3 -> 4: time=10 toll=5
        # 4 -> 5: time=5 toll=2
        # Also add cycle: 2 -> 3: time=5 toll=2 and 3 -> 2: time=5 toll=2
        # Sources: [0, 1], Destination: 5, Budget: 30, Checkpoints: [2, 3, 4], P=2
        N = 6
        edges = [
            (0, 2, 10, 10),
            (0, 3, 20, 5),
            (1, 2, 5, 1),
            (2, 4, 15, 5),
            (3, 4, 10, 5),
            (4, 5, 5, 2),
            (2, 3, 5, 2),
            (3, 2, 5, 2)
        ]
        sources = [0, 1]
        D = 5
        B = 30
        checkpoints = [2, 3, 4]
        P = 2
        # Best route: from source 1: 1 -> 2 -> 4 -> 5, time = 5 + 15 + 5 = 25, toll = 1 + 5 + 2 = 8, checkpoints visited: 2 and 4.
        expected_time = 25
        self.assertEqual(budget_route(N, len(edges), edges, sources, D, B, checkpoints, P), expected_time)

    def test_cycle_with_repeated_checkpoints(self):
        # Graph:
        # 0 -> 1: time=2 toll=2
        # 1 -> 2: time=2 toll=2
        # 2 -> 1: time=2 toll=2  (cycle between 1 and 2)
        # 2 -> 3: time=3 toll=3
        # Sources: [0], Destination: 3, Budget: 15, Checkpoints: [1, 2], P=3
        # Optimal route uses a cycle:
        # 0 -> 1 -> 2 -> 1 -> 2 -> 3, time = 2+2+2+2+3 = 11, toll = 2+2+2+2+3 = 11, visits checkpoints: 1,2,1,2 (total 4 visits)
        N = 4
        edges = [
            (0, 1, 2, 2),
            (1, 2, 2, 2),
            (2, 1, 2, 2),
            (2, 3, 3, 3)
        ]
        sources = [0]
        D = 3
        B = 15
        checkpoints = [1, 2]
        P = 3
        expected_time = 11
        self.assertEqual(budget_route(N, len(edges), edges, sources, D, B, checkpoints, P), expected_time)

if __name__ == '__main__':
    unittest.main()