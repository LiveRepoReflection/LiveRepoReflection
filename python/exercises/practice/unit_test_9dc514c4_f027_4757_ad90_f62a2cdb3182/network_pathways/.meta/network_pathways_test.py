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
        # Expected: corruption = latency 5 (first arrival) + 5 latency = 10
        self.assertEqual(minimum_corruption(edges, compromised, source, destination), 10)

    def test_multiple_paths_choose_best(self):
        # Two possible routes from 1 to 4:
        # Path 1: 1 -> 2 (3) -> 4 (3), node 2 is compromised, so cost = 3+corruption(3) + 3 = 9
        # Path 2: 1 -> 3 (4) -> 4 (1), no compromised nodes, so cost = 4+1 = 5
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
        # Best path: 1->2->3->4; cost:
        #   1->2 triggers cost: 0+2*2=4,
        #   2->3: 4+2=6,
        #   3->4: 6+3=9.
        self.assertEqual(minimum_corruption(
            [
                (1, 2, 2),
                (2, 3, 2),
                (3, 2, 2),
                (3, 4, 3)
            ],
            [2],
            1,
            4
        ), 9)

    def test_multiple_compromised_nodes(self):
        # Two routes from 1 to 3, involving two compromised nodes.
        # Route 1: 1->2 (2), 2->3 (2) with both 2 and 3 compromised.
        #   For 1->2: cost = 0 + 2*2 = 4.
        #   Then 2->3: 2 is already triggered, so cost = 4 + 2 = 6.
        # Route 2: 1->4 (5), 4->3 (1), no compromised nodes on this route.
        #   Cost = 5 + 1 = 6.
        # Expected cost = 6.
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
        # Another route: 1 -> 2 (3), 2 -> 3 (2), 3 -> 2 (2), then 2 -> 4 (3)
        # For the direct route 1->2->4: cost = 0+2*3=6 for node 2, then 6+3=9.
        # The cycle route would add extra cost when reaching 2 for the first time:
        #   1->2: 0+2*3=6, 2->3: 6+2=8, 3->2: since 2 is already triggered, cost=8+2=10, then 2->4: 10+3=13.
        # So best cost is 9.
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