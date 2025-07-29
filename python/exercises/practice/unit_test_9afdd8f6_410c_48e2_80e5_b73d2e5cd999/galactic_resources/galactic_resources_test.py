import unittest
from galactic_resources import min_transportation_cost

class TestGalacticResources(unittest.TestCase):
    def test_trivial_case(self):
        # Only one planet, no transportation needed.
        N = 1
        M = 1
        demand = [[0]]
        cost = [[[0]]]
        self.assertEqual(min_transportation_cost(N, M, demand, cost), 0)

    def test_simple_supply_demand(self):
        # Two planets: planet 0 has surplus and planet 1 has an equivalent demand.
        # Planet 0 produces 5 units (represented as -5) and planet 1 requires 5 units.
        N = 2
        M = 1
        demand = [[-5], [5]]
        cost = [
            [[0], [2]],   # From planet 0 to planet 1 has cost 2 per unit.
            [[-1], [0]]
        ]
        # Expected total cost = 5 * 2 = 10.
        self.assertEqual(min_transportation_cost(N, M, demand, cost), 10)

    def test_intermediate_hop(self):
        # Three planets: planet 0 has supply, planet 2 has demand and planet 1 is an intermediate node.
        # planet 0 produces 10 units, planet 2 requires 10 units.
        N = 3
        M = 1
        demand = [[-10], [0], [10]]
        cost = [
            [[0], [1], [-1]],  # From planet 0: to planet 1 costs 1, direct route to 2 does not exist.
            [[-1], [0], [3]],  # From planet 1 to planet 2 costs 3.
            [[-1], [-1], [0]]
        ]
        # Optimal: transport 10 units via 0->1->2 with cost (1+3)=4 per unit, total cost = 40.
        self.assertEqual(min_transportation_cost(N, M, demand, cost), 40)

    def test_direct_vs_indirect(self):
        # Three planets with two possible routes: direct vs an indirect path.
        N = 3
        M = 1
        demand = [[-10], [0], [10]]
        cost = [
            [[0], [2], [10]],   # From planet 0: 0->1 cost 2, direct 0->2 cost 10.
            [[-1], [0], [2]],   # From planet 1 to planet 2 cost 2.
            [[-1], [-1], [0]]
        ]
        # Optimal is the indirect path: cost = 2 (0->1) + 2 (1->2) = 4 per unit, total = 40.
        self.assertEqual(min_transportation_cost(N, M, demand, cost), 40)

    def test_multiple_resources(self):
        # Multiple resource types with three planets.
        # Planet 0: surplus of 10 units of resource 0 and 5 units of resource 1.
        # Planet 2: demand of 10 units of resource 0 and 5 units of resource 1.
        # Planet 1: intermediate node.
        N = 3
        M = 2
        demand = [
            [-10, -5],
            [0, 0],
            [10, 5]
        ]
        cost = [
            # From planet 0:
            [[0, 0], [1, 1], [3, 4]],
            # From planet 1:
            [[-1, -1], [0, 0], [2, 3]],
            # From planet 2:
            [[-1, -1], [-1, -1], [0, 0]]
        ]
        # For both resources the optimal cost using either direct or indirect routes is:
        # Resource 0: 10 units * (min(3, 1+2=3)) = 30; Resource 1: 5 units * (min(4, 1+3=4)) = 20; Total cost = 50.
        self.assertEqual(min_transportation_cost(N, M, demand, cost), 50)

    def test_impossible(self):
        # Two planets with a necessary route missing.
        N = 2
        M = 1
        demand = [[-5], [5]]
        cost = [
            [[0], [-1]],   # No route from planet 0 to planet 1.
            [[-1], [0]]
        ]
        # It's impossible to transport the required units, so expected result is -1.
        self.assertEqual(min_transportation_cost(N, M, demand, cost), -1)

if __name__ == '__main__':
    unittest.main()