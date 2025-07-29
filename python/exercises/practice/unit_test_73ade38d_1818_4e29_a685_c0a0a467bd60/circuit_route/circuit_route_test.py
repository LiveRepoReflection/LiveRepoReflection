import unittest
from circuit_route import optimal_circuit_routing

class TestOptimalCircuitRouting(unittest.TestCase):
    def test_empty_grid(self):
        self.assertEqual(optimal_circuit_routing(0, 0, [], []), -1)

    def test_single_component_same_start_end(self):
        self.assertEqual(optimal_circuit_routing(5, 5, [((1,1), (1,1))], []), 0)

    def test_single_component_straight_line(self):
        self.assertEqual(optimal_circuit_routing(5, 5, [((0,0), (0,4))], []), 4)

    def test_two_components_no_conflict(self):
        components = [((0,0), (4,4)), ((0,4), (4,0))]
        self.assertTrue(optimal_circuit_routing(5, 5, components, []) <= 8)

    def test_blocked_path(self):
        blocked = [(1,1), (1,2), (1,3)]
        self.assertEqual(optimal_circuit_routing(3, 5, [((0,0), (2,4))], blocked), 6)

    def test_impossible_route(self):
        blocked = [(1,0), (1,1), (1,2), (1,3), (1,4)]
        self.assertEqual(optimal_circuit_routing(3, 5, [((0,0), (2,4))], blocked), -1)

    def test_multiple_components_with_conflicts(self):
        components = [((0,0), (4,4)), ((0,1), (4,3)), ((0,2), (4,2))]
        blocked = [(2,2)]
        result = optimal_circuit_routing(5, 5, components, blocked)
        self.assertTrue(result >= 8 and result <= 12)

    def test_large_grid(self):
        components = [((0,0), (99,99)), ((0,99), (99,0))]
        result = optimal_circuit_routing(100, 100, components, [])
        self.assertTrue(result >= 198 and result <= 200)

    def test_complex_blocked_scenario(self):
        blocked = [(i, j) for i in range(1, 4) for j in range(1, 4)]
        components = [((0,0), (5,5)), ((0,5), (5,0))]
        result = optimal_circuit_routing(6, 6, components, blocked)
        self.assertTrue(result >= 10 and result <= 12)

    def test_edge_case_blocked_start_end(self):
        blocked = [(0,0), (4,4)]
        self.assertEqual(optimal_circuit_routing(5, 5, [((0,0), (4,4))], blocked), -1)

if __name__ == '__main__':
    unittest.main()