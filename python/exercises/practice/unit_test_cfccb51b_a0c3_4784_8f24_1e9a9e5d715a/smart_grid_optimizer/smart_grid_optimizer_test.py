import unittest
from smart_grid_optimizer import solve

class TestSmartGridOptimizer(unittest.TestCase):
    def test_example_case(self):
        substations = {
            1: {'capacity': 100, 'current_load': 20},
            2: {'capacity': 150, 'current_load': 50},
            3: {'capacity': 200, 'current_load': 30}
        }
        power_lines = [
            (1, 2, 50, 2),
            (2, 3, 40, 1)
        ]
        power_demands = [
            (1, 3, 30),
            (2, 3, 20)
        ]
        total_cost, fulfilled_demands = solve(substations, power_lines, power_demands)
        # Expected outcome: Only 40 units can be delivered due to edge (2,3) capacity.
        # Optimal distribution: deliver 20 from (1, 3, 30) and 20 from (2, 3, 20), resulting in a cost of:
        # 20 units via (1,2, cost=2) and (2,3, cost=1) => cost = 20*(2+1)=60,
        # plus 20 units via (2,3, cost=1) => cost = 20*1=20, so total cost = 80.
        self.assertEqual(total_cost, 80)
        self.assertEqual(fulfilled_demands, {(1, 3, 30): 20, (2, 3, 20): 20})

    def test_disconnected_graph(self):
        substations = {
            1: {'capacity': 50, 'current_load': 0},
            2: {'capacity': 50, 'current_load': 0},
            3: {'capacity': 50, 'current_load': 0}
        }
        power_lines = [
            (1, 2, 20, 5)
        ]
        power_demands = [
            (1, 3, 10)
        ]
        total_cost, fulfilled_demands = solve(substations, power_lines, power_demands)
        # No available path from substation 1 to 3 so no power delivery.
        self.assertEqual(total_cost, 0)
        self.assertEqual(fulfilled_demands, {(1, 3, 10): 0})

    def test_cycle_case(self):
        substations = {
            1: {'capacity': 100, 'current_load': 0},
            2: {'capacity': 100, 'current_load': 0},
            3: {'capacity': 100, 'current_load': 0},
            4: {'capacity': 100, 'current_load': 0}
        }
        power_lines = [
            (1, 2, 50, 2),
            (2, 3, 30, 2),
            (3, 4, 50, 1),
            (1, 3, 40, 4),
            (2, 4, 20, 3)
        ]
        power_demands = [
            (1, 4, 60)
        ]
        total_cost, fulfilled_demands = solve(substations, power_lines, power_demands)
        # Possible optimal distribution:
        # Use path 1-2-4 for 20 units at cost (2+3)*20 = 100,
        # Use path 1-2-3-4 for 30 units at cost (2+2+1)*30 = 150,
        # Use path 1-3-4 for 10 units at cost (4+1)*10 = 50.
        # Total delivered = 60, total cost = 100+150+50 = 300.
        self.assertEqual(total_cost, 300)
        self.assertEqual(fulfilled_demands, {(1, 4, 60): 60})

    def test_insufficient_capacity(self):
        substations = {
            1: {'capacity': 100, 'current_load': 60},
            2: {'capacity': 100, 'current_load': 80},
            3: {'capacity': 100, 'current_load': 50}
        }
        power_lines = [
            (1, 2, 50, 2),
            (2, 3, 20, 1)
        ]
        power_demands = [
            (1, 3, 50)
        ]
        total_cost, fulfilled_demands = solve(substations, power_lines, power_demands)
        # Available capacity calculations:
        # Substation 1: available = 40, Substation 2: available = 20, Substation 3: available = 50.
        # Path limited by minimum value: min(40, 20, 50) = 20.
        # Cost: 20*(2+1) = 60.
        self.assertEqual(total_cost, 60)
        self.assertEqual(fulfilled_demands, {(1, 3, 50): 20})

if __name__ == '__main__':
    unittest.main()