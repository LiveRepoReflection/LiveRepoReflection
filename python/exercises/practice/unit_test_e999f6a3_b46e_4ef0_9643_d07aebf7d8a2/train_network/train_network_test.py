import unittest
from train_network import optimal_train_network

class TrainNetworkTest(unittest.TestCase):
    def test_single_city(self):
        # With one city, no edges are needed so revenue is 0.
        self.assertEqual(optimal_train_network(1, [], 10, 5), 0)

    def test_two_cities_possible(self):
        # Two cities with one connecting edge that exactly fits the budget.
        # Revenue is passenger_volume * revenue_per_passenger = 100 * 2 = 200.
        edges = [(0, 1, 5, 100)]
        self.assertEqual(optimal_train_network(2, edges, 5, 2), 200)

    def test_two_cities_impossible(self):
        # Two cities with one connecting edge but the budget is insufficient.
        edges = [(0, 1, 5, 100)]
        self.assertEqual(optimal_train_network(2, edges, 4, 2), -1)

    def test_tree_structure_exact_budget(self):
        # Four cities connected in a spanning tree:
        # Edges: (0,1,3,10), (1,2,3,10), (2,3,3,10)
        # Total cost = 9, total revenue = 10*2 + 10*2 + 10*2 = 60.
        edges = [(0, 1, 3, 10), (1, 2, 3, 10), (2, 3, 3, 10)]
        self.assertEqual(optimal_train_network(4, edges, 9, 2), 60)

    def test_extra_edge_improves_revenue(self):
        # Four cities with an extra beneficial edge.
        # Spanning tree: (0,1,3,10), (1,2,3,10), (2,3,3,10) -> cost = 9, revenue = 60.
        # Extra edge: (0,3,5,50) -> cost = 5, revenue = 100.
        # With budget 14, optimal network includes all edges for total cost = 14 and revenue = 160.
        edges = [(0, 1, 3, 10), (1, 2, 3, 10), (2, 3, 3, 10), (0, 3, 5, 50)]
        self.assertEqual(optimal_train_network(4, edges, 14, 2), 160)

    def test_multiple_paths(self):
        # Five cities with a mix of edges.
        # Edges:
        # (0,1,4,30), (0,2,2,20), (1,2,1,10), (1,3,5,40), (2,3,8,20),
        # (3,4,3,50), (2,4,6,25)
        #
        # Case 1: revenue_per_passenger = 1, budget = 11.
        # One optimal configuration using edges: (1,2,1,10), (0,2,2,20), (1,3,5,40), (3,4,3,50)
        # Total cost = 1+2+5+3 = 11, revenue = 10+20+40+50 = 120.
        edges = [
            (0, 1, 4, 30),
            (0, 2, 2, 20),
            (1, 2, 1, 10),
            (1, 3, 5, 40),
            (2, 3, 8, 20),
            (3, 4, 3, 50),
            (2, 4, 6, 25)
        ]
        self.assertEqual(optimal_train_network(5, edges, 11, 1), 120)
        
        # Case 2: With increased budget = 15, an extra edge can be included.
        # For example, including the edge (0,1,4,30) in addition to the previous edges,
        # Total cost becomes 1+2+5+3+4 = 15, and revenue becomes 10+20+40+50+30 = 150.
        self.assertEqual(optimal_train_network(5, edges, 15, 1), 150)

    def test_no_possible_connection(self):
        # Four cities but the graph is disconnected.
        # Edges: (0,1,5,100) and (2,3,5,100) do not connect all cities.
        edges = [(0, 1, 5, 100), (2, 3, 5, 100)]
        self.assertEqual(optimal_train_network(4, edges, 20, 2), -1)

if __name__ == '__main__':
    unittest.main()