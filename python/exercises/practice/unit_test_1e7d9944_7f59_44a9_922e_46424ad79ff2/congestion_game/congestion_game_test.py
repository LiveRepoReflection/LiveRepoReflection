import unittest
from congestion_game import find_equilibrium

class CongestionGameTest(unittest.TestCase):
    def test_single_path(self):
        # Only one available path from s to t.
        n = 2
        edges = [
            (0, 1, 5, 10)
        ]
        s = 0
        t = 1
        num_users = 3
        result = find_equilibrium(n, edges, s, t, num_users)
        expected = {
            (0, 1): 3
        }
        self.assertEqual(result, expected)

    def test_parallel_paths(self):
        # Two distinct routes from s to t.
        # Route 1: direct edge (0,1) with cost = 1*x + 1.
        # Route 2: via node 2: edges (0,2) cost = 2*x + 0 and (2,1) cost = 0*x + 2.
        # Based on fixed cost, initial path is (0,1) since 1 < (0+2)=2,
        # and equilibrium should maintain both users on (0,1) if switching is not beneficial.
        n = 3
        edges = [
            (0, 1, 1, 1),
            (0, 2, 2, 0),
            (2, 1, 0, 2)
        ]
        s = 0
        t = 1
        num_users = 2
        result = find_equilibrium(n, edges, s, t, num_users)
        # Expected: Both users remain on the direct edge (0,1).
        self.assertEqual(result.get((0, 1), 0), 2)
        self.assertEqual(result.get((0, 2), 0), 0)
        self.assertEqual(result.get((2, 1), 0), 0)

    def test_multiple_users_complex_network(self):
        # A more complex network including cycles and multiple intermediate nodes.
        # Graph:
        # 0 -> 1: cost = 1*x + 0
        # 1 -> 3: cost = 1*x + 2
        # 0 -> 2: cost = 2*x + 1
        # 2 -> 3: cost = 0*x + 3
        # 1 -> 2: cost = 1*x + 1
        # 2 -> 1: cost = 1*x + 1
        # Four users route from node 0 to node 3.
        n = 4
        edges = [
            (0, 1, 1, 0),
            (1, 3, 1, 2),
            (0, 2, 2, 1),
            (2, 3, 0, 3),
            (1, 2, 1, 1),
            (2, 1, 1, 1)
        ]
        s = 0
        t = 3
        num_users = 4
        result = find_equilibrium(n, edges, s, t, num_users)

        # Check that each key in result is a valid edge in the network and has a non-negative integer flow.
        valid_edges = {(0, 1), (1, 3), (0, 2), (2, 3), (1, 2), (2, 1)}
        for edge, flow in result.items():
            self.assertIn(edge, valid_edges)
            self.assertIsInstance(flow, int)
            self.assertGreaterEqual(flow, 0)

        # Check that the total flow leaving the source equals the number of users.
        flow_out = result.get((0, 1), 0) + result.get((0, 2), 0)
        self.assertEqual(flow_out, num_users)

    def test_no_switch_possible(self):
        # A network with only one path available, ensuring the algorithm immediately reaches equilibrium.
        n = 3
        edges = [
            (0, 1, 0, 1),
            (1, 2, 0, 1)
        ]
        s = 0
        t = 2
        num_users = 5
        result = find_equilibrium(n, edges, s, t, num_users)

        # Both edges should carry all the traffic.
        self.assertEqual(result.get((0, 1), 0), 5)
        self.assertEqual(result.get((1, 2), 0), 5)

if __name__ == '__main__':
    unittest.main()