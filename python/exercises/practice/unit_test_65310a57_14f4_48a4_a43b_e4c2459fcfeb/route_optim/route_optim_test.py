import unittest
from route_optim.route_optim import min_delivery_cost

class TestRouteOptim(unittest.TestCase):

    def test_single_feasible_order(self):
        city_graph = {
            'A': [('B', 10, 5)],
            'B': []
        }
        delivery_orders = [
            ('A', 'B', 15)
        ]
        # Only one order feasible, cost should be 5.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 5)

    def test_single_infeasible_order_due_to_deadline(self):
        city_graph = {
            'A': [('B', 10, 5)],
            'B': []
        }
        delivery_orders = [
            ('A', 'B', 5)  # deadline too tight; travel takes 10 minutes
        ]
        # Infeasible: no orders can be completed.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 0)

    def test_single_infeasible_order_due_to_no_path(self):
        city_graph = {
            'A': [('B', 10, 5)],
            'B': [],
            'C': []
        }
        delivery_orders = [
            ('C', 'B', 20)  # No path exists from C to B.
        ]
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 0)

    def test_multiple_orders_all_feasible(self):
        city_graph = {
            'A': [('B', 5, 2), ('C', 10, 4)],
            'B': [('D', 6, 3)],
            'C': [('D', 5, 2)],
            'D': []
        }
        delivery_orders = [
            ('A', 'D', 20),  # Two possible routes: A->B->D (time=11, cost=5) or A->C->D (time=15, cost=6).
            ('B', 'D', 10)   # Direct route: B->D, time=6, cost=3.
        ]
        # For order 1, optimal route is A->B->D (cost 2+3=5).
        # Order 2 cost is 3.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 8)

    def test_multiple_orders_some_infeasible(self):
        city_graph = {
            'A': [('B', 5, 2), ('C', 10, 4)],
            'B': [('D', 16, 3)],  # This edge makes travel time too high for deadline.
            'C': [('D', 5, 2)],
            'D': [],
            'E': [('F', 3, 1)],
            'F': []
        }
        delivery_orders = [
            ('A', 'D', 20),  # A->C->D feasible: time=15, cost=6; A->B->D is time=21, infeasible.
            ('B', 'D', 15),  # B->D: time=16, infeasible.
            ('E', 'F', 10)   # Direct feasible.
        ]
        # Only orders 1 and 3 are feasible. Total cost = 6 + 1 = 7.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 7)

    def test_order_with_cycle(self):
        # Graph contains a cycle but optimal route does not cycle indefinitely.
        city_graph = {
            'A': [('B', 3, 2), ('C', 4, 3)],
            'B': [('A', 3, 2), ('D', 5, 4)],
            'C': [('D', 3, 2)],
            'D': []
        }
        delivery_orders = [
            ('A', 'D', 10)
        ]
        # Two routes:
        # 1. A->B->D: time = 3+5 = 8, cost = 2+4 = 6.
        # 2. A->C->D: time = 4+3 = 7, cost = 3+2 = 5.
        # Optimal route is A->C->D.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 5)

    def test_multiple_paths_with_same_cost(self):
        # Test where multiple paths yield same cost but different travel times.
        city_graph = {
            'A': [('B', 2, 1), ('C', 5, 1)],
            'B': [('D', 4, 3)],
            'C': [('D', 1, 3)],
            'D': []
        }
        delivery_orders = [
            ('A', 'D', 10)
        ]
        # Two paths both cost 4:
        # 1. A->B->D: time= 2+4 = 6, cost = 1+3 = 4.
        # 2. A->C->D: time= 5+1 = 6, cost = 1+3 = 4.
        # Total cost should be 4.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 4)

    def test_large_graph(self):
        # Create a larger graph with 10 nodes and multiple edges.
        city_graph = {
            'A': [('B', 2, 1), ('C', 4, 2)],
            'B': [('D', 3, 2), ('E', 2, 1)],
            'C': [('E', 1, 1), ('F', 5, 3)],
            'D': [('G', 2, 2)],
            'E': [('G', 3, 2), ('H', 4, 3)],
            'F': [('H', 2, 1)],
            'G': [('I', 1, 1)],
            'H': [('I', 1, 1), ('J', 2, 2)],
            'I': [('J', 3, 3)],
            'J': []
        }
        delivery_orders = [
            ('A', 'J', 20),  # Feasible through multiple routes; need lowest cost.
            ('C', 'I', 10),  # Two options: C->F->H->I or C->E->G->I.
            ('B', 'H', 9),   # Feasible only if route through E is chosen.
            ('D', 'J', 10)   # D->G->I->J path.
        ]
        # With optimal paths chosen:
        # Order 1: A->B->E->H->J => cost: 1+1+3+2 = 7, time: 2+2+4+2 = 10 (alternative routes might exist)
        # Order 2: C->E->G->I => cost: 1+2+1 = 4, time: 1+3+1 = 5
        # Order 3: B->E->H => cost: 1+3 = 4, time: 2+4 = 6
        # Order 4: D->G->I->J => cost: 2+1+3 = 6, time: 2+1+3 = 6
        # Total optimal cost = 7 + 4 + 4 + 6 = 21.
        # Note: Actual optimal values might depend on the algorithm finding the lowest cost among alternatives.
        self.assertEqual(min_delivery_cost(city_graph, delivery_orders), 21)

if __name__ == '__main__':
    unittest.main()