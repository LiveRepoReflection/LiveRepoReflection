import unittest
from network_towers.network_towers import min_network_cost

class TestNetworkTowers(unittest.TestCase):
    def test_single_town_possible(self):
        # Single town, no edges. Tower capacity is sufficient.
        N = 1
        M = 0
        edges = []
        population = [100]  # population is not used in computation but provided for completeness.
        demand = [10]
        tower_cost = [50]
        capacity = 20
        expected = 50  # Single tower deployment cost.
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

    def test_simple_pair(self):
        # Two towns connected by an edge.
        N = 2
        M = 1
        edges = [(0, 1)]
        population = [100, 120]
        demand = [10, 15]
        tower_cost = [50, 70]
        capacity = 30  # Tower at node 0 covers both (10+15=25 <=30).
        expected = 50
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

    def test_disconnected_graph(self):
        # Three towns, with no edges. Each town must have its own tower.
        N = 3
        M = 0
        edges = []
        population = [100, 150, 120]
        demand = [10, 20, 15]
        tower_cost = [30, 40, 25]
        capacity = 20
        # Each tower covers only its own town. Total cost = 30+40+25 = 95.
        expected = 95
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

    def test_infeasible_due_to_capacity(self):
        # Two towns, no connection means each must cover itself.
        # One town has demand exceeding the capacity.
        N = 2
        M = 0
        edges = []
        population = [100, 100]
        demand = [5, 50]
        tower_cost = [10, 20]
        capacity = 30  # Town with demand 50 cannot be served.
        expected = -1
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

    def test_complex_graph(self):
        # Four towns in a chain: 0-1-2-3.
        # Strategic deployment is necessary to ensure each deployed tower's coverage area does not exceed capacity.
        N = 4
        M = 3
        edges = [(0, 1), (1, 2), (2, 3)]
        population = [100, 150, 200, 120]
        demand = [10, 15, 20, 10]
        tower_cost = [100, 30, 30, 100]
        capacity = 40
        # Analysis:
        # - A tower placed at node 0 covers {0,1}: demand = 10+15 = 25 (valid).
        # - A tower placed at node 3 covers {3,2}: demand = 10+20 = 30 (valid).
        # Towns 0,1,2,3 all get covered.
        # The total cost is 100 + 100 = 200.
        expected = 200
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

    def test_complete_graph_single_tower(self):
        # Three towns fully connected, so a single tower can cover all nodes.
        N = 3
        M = 3
        edges = [(0, 1), (0, 2), (1, 2)]
        population = [100, 100, 100]
        demand = [10, 10, 10]
        tower_cost = [40, 50, 60]
        capacity = 30  # Sum of demands is exactly 30 if covered by one tower.
        # Best option is tower at node 0 with cost 40.
        expected = 40
        self.assertEqual(min_network_cost(N, M, edges, population, demand, tower_cost, capacity), expected)

if __name__ == '__main__':
    unittest.main()