import unittest
from transit_network import maximum_ridership

class TransitNetworkTest(unittest.TestCase):
    def test_single_node(self):
        # Only one node, no routes needed. Connected by default.
        N = 1
        edges = []
        budget = 0
        start_node = 0
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 0)

    def test_disconnected_graph(self):
        # Graph where not all nodes can be connected regardless of budget.
        N = 3
        # Only one route connecting node 0 and 1. Node 2 remains disconnected.
        edges = [
            (0, 1, 10, 100)
        ]
        budget = 100
        start_node = 0
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 0)

    def test_simple_network(self):
        # Basic test with two nodes and a single connecting edge.
        N = 2
        edges = [
            (0, 1, 5, 50)
        ]
        budget = 5
        start_node = 0
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 50)

    def test_budget_constraint(self):
        # Graph where a spanning tree exists only if budget is sufficient.
        N = 3
        edges = [
            (0, 1, 5, 50),
            (1, 2, 6, 60),
            (0, 2, 20, 100)
        ]
        budget = 10  # Not enough to connect all nodes with any spanning tree.
        start_node = 0
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 0)

    def test_multiple_options(self):
        # Graph with multiple possible spanning trees to maximize ridership.
        N = 4
        edges = [
            (0, 1, 4, 40),
            (0, 2, 3, 30),
            (1, 2, 2, 20),
            (1, 3, 6, 60),
            (2, 3, 5, 50)
        ]
        budget = 12
        start_node = 0
        # Optimal spanning tree can yield total ridership of 120.
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 120)

    def test_cyclic_graph(self):
        # A cyclic graph where multiple cycles exist; the algorithm must choose the best spanning tree.
        N = 5
        edges = [
            (0, 1, 2, 20),
            (1, 2, 3, 30),
            (2, 3, 4, 40),
            (3, 4, 5, 50),
            (4, 0, 6, 60),
            (1, 3, 2, 20)
        ]
        budget = 12
        start_node = 0
        # Best selection yields total ridership of 120.
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 120)

    def test_complex_network(self):
        # A more complex network with 6 nodes and multiple edges.
        N = 6
        edges = [
            (0, 1, 3, 30),
            (0, 2, 1, 10),
            (1, 2, 1, 20),
            (1, 3, 4, 40),
            (2, 3, 2, 30),
            (2, 4, 5, 50),
            (3, 4, 3, 30),
            (3, 5, 6, 60),
            (4, 5, 2, 20)
        ]
        budget = 15
        start_node = 0
        # One optimal spanning tree:
        # (0,2): cost=1, ridership=10
        # (1,2): cost=1, ridership=20
        # (2,3): cost=2, ridership=30
        # (3,5): cost=6, ridership=60
        # (3,4): cost=3, ridership=30
        # Total cost = 1+1+2+6+3 = 13 (if within budget, otherwise alternative tree)
        # However, an alternative tree:
        # (0,2): cost=1, ridership=10, (1,2): cost=1, ridership=20,
        # (2,3): cost=2, ridership=30, (3,4): cost=3, ridership=30, (4,5): cost=2, ridership=20
        # Total cost = 1+1+2+3+2 = 9, Total ridership = 10+20+30+30+20 = 110
        # Best found option with budget 15 is:
        # (0,1): cost=3, ridership=30, (1,2): cost=1, ridership=20,
        # (2,3): cost=2, ridership=30, (3,5): cost=6, ridership=60, (3,4): cost=3, ridership=30
        # Total cost = 3+1+2+6+3 = 15, Total ridership = 30+20+30+60+30 = 170
        # Expected optimal total ridership is 170.
        self.assertEqual(maximum_ridership(N, edges, budget, start_node), 170)

if __name__ == '__main__':
    unittest.main()