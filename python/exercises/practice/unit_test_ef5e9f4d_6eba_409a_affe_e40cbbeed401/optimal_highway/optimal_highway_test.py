import math
import unittest
from optimal_highway import optimal_highway

class TestOptimalHighway(unittest.TestCase):
    def test_direct_highway(self):
        # Using the sample provided in the problem description.
        graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'D': 12},
            'C': {'A': 15, 'D': 5},
            'D': {'B': 12, 'C': 5}
        }
        highways = [
            ('A', 'B', 50, 2),
            ('B', 'D', 75, 3),
            ('A', 'D', 120, 4)
        ]
        budget = 125
        targets = ('A', 'D')
        # Optimal is building the direct highway A-D with travel time 4, total cost 120 <= 125.
        expected = 4
        result = optimal_highway(graph, highways, budget, targets)
        self.assertEqual(result, expected)

    def test_no_highway_possible_due_to_budget(self):
        # With zero budget, the highways cannot be constructed; use only existing roads.
        graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'D': 12},
            'C': {'A': 15, 'D': 5},
            'D': {'B': 12, 'C': 5}
        }
        highways = [
            ('A', 'B', 50, 2),
            ('B', 'D', 75, 3),
            ('A', 'D', 120, 4)
        ]
        budget = 0
        targets = ('A', 'D')
        # The only available route is via existing roads: A -> C -> D: 15 + 5 = 20.
        expected = 20
        result = optimal_highway(graph, highways, budget, targets)
        self.assertEqual(result, expected)

    def test_mixed_highway_and_road(self):
        # In this test, a combination of highway and road will yield the optimal route.
        graph = {
            'A': {'B': 10, 'D': 40},
            'B': {'A': 10, 'C': 10},
            'C': {'B': 10, 'D': 5},
            'D': {'A': 40, 'C': 5}
        }
        highways = [
            ('A', 'B', 15, 2),   # highway from A to B reduces time from 10 to 2.
            ('B', 'C', 20, 3),   # highway from B to C reduces time from 10 to 3.
            ('A', 'C', 30, 10)   # direct highway A to C.
        ]
        budget = 30
        targets = ('A', 'C')
        # Possibilities:
        # 1. Use highway A-C: cost=30, time=10.
        # 2. Use highway A-B (2) + road B-C (10): total time = 12, cost=15.
        # 3. Use road A-B (10) + highway B-C (3): total time = 13, cost=20.
        # 4. Only existing roads: A-B (10) + B-C (10) = 20, or A-D (40) + D-C (5) = 45.
        # The optimal route is via highway A-C with time 10.
        expected = 10
        result = optimal_highway(graph, highways, budget, targets)
        self.assertEqual(result, expected)
        
    def test_inaccessible_target(self):
        # In this test, one of the target nodes is not present in the graph.
        # Since graph G is expected to be connected among its nodes, missing target will mean no path.
        graph = {
            'A': {'B': 10},
            'B': {'A': 10}
        }
        highways = [
            ('A', 'B', 20, 2)
        ]
        budget = 50
        targets = ('A', 'C')  # 'C' does not exist in the graph.
        # There is no valid path to a non-existent city.
        expected = float('inf')
        result = optimal_highway(graph, highways, budget, targets)
        self.assertEqual(result, expected)
        
    def test_highway_combination_under_budget(self):
        # In this test, building a combination of highways is possible but only some combinations 
        # are allowed under budget. The optimal route includes a mix of highway and road.
        graph = {
            'X': {'Y': 20, 'Z': 50},
            'Y': {'X': 20, 'Z': 30, 'W': 60},
            'Z': {'X': 50, 'Y': 30, 'W': 10},
            'W': {'Y': 60, 'Z': 10}
        }
        highways = [
            ('X', 'Y', 25, 5),   # cheaper than road (20 becomes 5)
            ('Y', 'W', 40, 8),   # cheaper than road (60 becomes 8)
            ('X', 'W', 80, 7),   # direct highway X to W
            ('Y', 'Z', 30, 4)    # highway from Y to Z reducing time from 30 to 4
        ]
        budget = 65
        targets = ('X', 'W')
        # Possibilities:
        # 1. Build highway X-W: cost=80 (exceeds budget)
        # 2. Build highways: X-Y (25) and Y-W (40): total cost=65, travel time = 5 + 8 = 13.
        # 3. Build highway X-Y (25) and use road Y-W: time = 5 + 60 = 65.
        # 4. Use road entirely: X-Y (20) + Y-W (60) = 80, or X-Z (50) + Z-W (10) = 60.
        # 5. Other combination with Y-Z doesn't help to lower overall time.
        # Optimal is option 2 with travel time = 13.
        expected = 13
        result = optimal_highway(graph, highways, budget, targets)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()