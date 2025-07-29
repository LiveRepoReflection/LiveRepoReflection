import unittest
from network_pathways import minimum_corruption

class NetworkPathwaysTest(unittest.TestCase):

    def test_direct_path_no_compromise(self):
        # Simple direct path with no compromised servers
        edges = [
            (1, 2, 5)
        ]
        compromised = []
        source = 1
        destination = 2
        # Expected: total latency 5 (no corruption added)
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 5)

    def test_direct_path_with_compromise(self):
        # Direct path where destination is compromised
        edges = [
            (1, 2, 5)
        ]
        compromised = [2]
        source = 1
        destination = 2
        # Expected: corruption = latency when 2 is first reached (5) + total latency (5) = 10
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 10)

    def test_multiple_paths_choose_best(self):
        # Two possible routes from 1 to 4:
        # Path 1: 1 -> 2 (3) -> 4 (3), node 2 is compromised, so cost = 3 (corruption) + 6 (latency) = 9
        # Path 2: 1 -> 3 (4) -> 4 (1), no compromised nodes, so cost = 0 + 5 = 5
        edges = [
            (1, 2, 3),
            (2, 4, 3),
            (1, 3, 4),
            (3, 4, 1)
        ]
        compromised = [2]
        source = 1
        destination = 4
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 5)

    def test_no_path(self):
        # Graph where destination is unreachable
        edges = [
            (1, 2, 3),
            (2, 3, 3)
        ]
        compromised = [2, 3]
        source = 1
        destination = 4
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), -1)

    def test_cycle_in_graph(self):
        # Graph with a cycle.
        # 1 -> 2 (2), 2 -> 3 (2), 3 -> 2 (2), 3 -> 4 (3)
        # Compromised: 2 is compromised.
        # Best path: 1->2->3->4; cost: corruption at first arrival at 2 is 2; total latency = 2+2+3=7; total = 2+7 = 9.
        edges = [
            (1, 2, 2),
            (2, 3, 2),
            (3, 2, 2),
            (3, 4, 3)
        ]
        compromised = [2]
        source = 1
        destination = 4
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 9)

    def test_multiple_compromised_nodes(self):
        # Two routes from 1 to 3, involving two compromised nodes
        # Route 1: 1->2 (2), 2->3 (2) with both 2 and 3 compromised
        #   Corruption: for node 2: 2, for node 3: 2, total latency = 2+2=4, expected cost = 2+2+4 = 8.
        # Route 2: 1->4 (5), 4->3 (1), no compromised on this route (if only 2 and 3 are compromised)
        #   Expected: cost = 0 + 5+1 = 6, choose best = 6.
        edges = [
            (1, 2, 2),
            (2, 3, 2),
            (1, 4, 5),
            (4, 3, 1)
        ]
        compromised = [2, 3]
        source = 1
        destination = 3
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 6)

    def test_source_equals_destination(self):
        # When the source and destination are the same, the cost is 0.
        edges = [
            (1, 2, 2),
            (2, 3, 2)
        ]
        compromised = [2]
        source = 1
        destination = 1
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 0)

    def test_compromised_revisited(self):
        # Test that a compromised server only adds its incoming link's latency once.
        # Graph:
        # 1 -> 2 (3), 2 -> 4 (3)
        # Another route: 1 -> 2 (3), 2 -> 3 (2), 3 -> 2 (2) and 2 -> 4 (3)
        # Compromised: 2 is compromised.
        # Even if the route revisits node 2, the cost for node 2's injection should be added only once.
        # Expected best route is 1->2->4: corruption = 3 (for node 2) and latency = 6, total = 9.
        edges = [
            (1, 2, 3),
            (2, 4, 3),
            (2, 3, 2),
            (3, 2, 2),
            (2, 4, 3)
        ]
        compromised = [2]
        source = 1
        destination = 4
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 9)

if __name__ == '__main__':
    unittest.main()