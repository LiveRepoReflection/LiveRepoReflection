import unittest
from cdn_deploy import min_cost

class CdnDeployTest(unittest.TestCase):
    def test_single_node(self):
        n = 1
        m = 0
        edges = []
        populations = [10]
        D = 100
        L = 10
        # With one city, the only option is to deploy a CDN server.
        expected_cost = 100
        self.assertEqual(min_cost(n, m, edges, populations, D, L), expected_cost)

    def test_chain_graph(self):
        n = 3
        m = 2
        edges = [(0, 1), (1, 2)]
        populations = [10, 20, 30]
        D = 50
        L = 1
        # Best option: deploy a server at node 1.
        # Cost = D + latency for node 0 (10*1) + latency for node 2 (30*1) = 50 + 10 + 30 = 90.
        expected_cost = 90
        self.assertEqual(min_cost(n, m, edges, populations, D, L), expected_cost)

    def test_complete_graph(self):
        n = 4
        m = 6
        edges = [(0, 1), (0, 2), (0, 3),
                 (1, 2), (1, 3), (2, 3)]
        populations = [5, 10, 15, 20]
        D = 100
        L = 5
        # Best option: deploy a server at the node with maximum population (node 3).
        # Total cost = D + L*(sum of populations of remaining nodes) = 100 + 5*(5+10+15) = 100 + 150 = 250.
        expected_cost = 250
        self.assertEqual(min_cost(n, m, edges, populations, D, L), expected_cost)
    
    def test_tree_graph(self):
        n = 5
        m = 4
        edges = [(0, 1), (0, 2), (1, 3), (1, 4)]
        populations = [10, 50, 20, 40, 30]
        D = 60
        L = 2
        # After careful analysis, the optimal deployment cost is computed as 260.
        expected_cost = 260
        self.assertEqual(min_cost(n, m, edges, populations, D, L), expected_cost)
        
    def test_cycle_graph(self):
        n = 6
        m = 8
        edges = [(0, 1), (0, 2), (1, 2), (1, 3),
                 (2, 4), (3, 4), (3, 5), (4, 5)]
        populations = [10, 100, 20, 200, 30, 50]
        D = 150
        L = 3
        # Through analysis, one optimal strategy yields a total cost of 630.
        expected_cost = 630
        self.assertEqual(min_cost(n, m, edges, populations, D, L), expected_cost)

if __name__ == '__main__':
    unittest.main()