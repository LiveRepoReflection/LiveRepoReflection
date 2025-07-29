import unittest
from router_config.router_config import optimize_router_config

class RouterConfigTest(unittest.TestCase):
    def test_trivial_no_change(self):
        # Single router with no potential changes. Expected output is the initial score.
        N = 1
        adjacency_list = [
            []
        ]
        initial_scores = [500]
        target_router = 0
        potential_changes = []
        influence_matrix = [
            [0]
        ]
        expected = 500
        result = optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix)
        self.assertEqual(result, expected)

    def test_two_router(self):
        # Two routers that are connected. Two potential changes that affect each other.
        N = 2
        adjacency_list = [
            [1],
            [0]
        ]
        initial_scores = [300, 400]
        target_router = 1
        potential_changes = [(0, 100), (1, 50)]
        influence_matrix = [
            [0, 0.5],
            [0.2, 0]
        ]
        # Options:
        # Applying (0,100) alone: router0:300->400; router1:400+0.5*100=450.
        # Applying (1,50) alone: router1:400->450.
        # Applying both: router1 becomes 400 + 0.5*100 + 50 = 500.
        expected = 500
        result = optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix)
        self.assertEqual(result, expected)

    def test_invalid_change(self):
        # Three routers. One potential change is invalid as it would push a score above 1000.
        N = 3
        adjacency_list = [
            [1],
            [0, 2],
            [1]
        ]
        initial_scores = [100, 500, 900]
        target_router = 2
        potential_changes = [(1, 600), (0, 50), (1, 100)]
        influence_matrix = [
            [0, 0.1, 0],
            [0.2, 0, 0.3],
            [0, 0, 0]
        ]
        # (1,600) is invalid because it would change router1's score from 500 to 1100.
        # Only (0,50) and (1,100) are applied:
        # (0,50): router0: 100+50=150; router1: 500+0.1*50=505.
        # (1,100): router1: 505+100=605; plus cascading: router0 gets +0.2*100=20 (total 170), router2 gets +0.3*100=30 -> 900+30=930.
        expected = 930
        result = optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix)
        self.assertEqual(result, expected)

    def test_complex_cascading(self):
        # Four routers with cascading effects.
        N = 4
        adjacency_list = [
            [1, 2],
            [0, 2, 3],
            [0, 1],
            [1]
        ]
        initial_scores = [200, 300, 400, 500]
        target_router = 3
        potential_changes = [(0, 100), (1, 50), (2, 150), (3, 20)]
        influence_matrix = [
            [0,   0.5, 0.2, 0],
            [0.3, 0,   0.4, 0.6],
            [0.1, 0.5, 0,   0.0],
            [0,   0.2, 0.1, 0]
        ]
        # Applying all changes:
        # (0,100): router0: 200->300; router1: +0.5*100 = +50; router2: +0.2*100 = +20.
        # (1,50): router1: 300+50->350; router0: +15, router2: +20, router3: +30.
        # (2,150): router2: 400+150->550; router0: +15, router1: +75.
        # (3,20): router3: 500+20->520; router1: +4.
        # Final target router 3: initial 500 +30 (from router1 change) +20 (self) = 550.
        expected = 550
        result = optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix)
        self.assertEqual(result, expected)

    def test_change_with_near_limit(self):
        # Three routers where one change would exceed the upper limit and should be ignored.
        N = 3
        adjacency_list = [
            [1],
            [0, 2],
            [1]
        ]
        initial_scores = [990, 50, 10]
        target_router = 0
        potential_changes = [(1, 100), (2, 50), (0, 20)]
        influence_matrix = [
            [0,    0.2, 0],
            [0.1,  0,   0.5],
            [0,    0.3, 0]
        ]
        # (0,20) is invalid because router0 would go from 990 to 1010.
        # (1,100): router1: 50->150; cascades: router0: +10, router2: +50.
        # (2,50): router2: 10->60; cascades: router1: +15.
        # Final router0 becomes: 990+10 = 1000.
        expected = 1000
        result = optimize_router_config(N, adjacency_list, initial_scores, target_router, potential_changes, influence_matrix)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()