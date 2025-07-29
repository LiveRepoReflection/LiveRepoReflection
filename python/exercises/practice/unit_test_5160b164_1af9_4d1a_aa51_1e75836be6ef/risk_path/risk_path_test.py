import unittest
from risk_path import find_optimal_path

class TestRiskPath(unittest.TestCase):
    def test_simple_linear_path(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        
        def risk_levels(t):
            return [10, 20, 30]
        
        def transfer_risks(t):
            return {(0, 1): 0.5, (1, 2): 0.5}
            
        start = 0
        end = 2
        T = 1
        max_path_length = 2
        
        result = find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length)
        self.assertEqual(result, [0, 1, 2])

    def test_multiple_paths_with_different_risks(self):
        N = 4
        edges = [(0, 1), (1, 3), (0, 2), (2, 3)]
        
        def risk_levels(t):
            return [10, 40, 20, 30]
        
        def transfer_risks(t):
            return {(0, 1): 0.8, (1, 3): 0.5, (0, 2): 0.5, (2, 3): 0.5}
            
        start = 0
        end = 3
        T = 1
        max_path_length = 2
        
        result = find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length)
        self.assertEqual(result, [0, 2, 3])

    def test_time_varying_risks(self):
        N = 3
        edges = [(0, 1), (1, 2)]
        
        def risk_levels(t):
            return [10 + t, 20 - t, 30]
        
        def transfer_risks(t):
            return {(0, 1): 0.5, (1, 2): 0.5}
            
        start = 0
        end = 2
        T = 2
        max_path_length = 2
        
        result = find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length)
        self.assertEqual(result, [0, 1, 2])

    def test_no_valid_path(self):
        N = 3
        edges = [(0, 1), (2, 1)]
        
        def risk_levels(t):
            return [10, 20, 30]
        
        def transfer_risks(t):
            return {(0, 1): 0.5, (2, 1): 0.5}
            
        start = 0
        end = 2
        T = 1
        max_path_length = 2
        
        result = find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length)
        self.assertEqual(result, [])

    def test_path_length_constraint(self):
        N = 4
        edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
        
        def risk_levels(t):
            return [10, 20, 30, 40]
        
        def transfer_risks(t):
            return {(0, 1): 0.5, (1, 2): 0.5, (2, 3): 0.5, (0, 3): 0.9}
            
        start = 0
        end = 3
        T = 1
        max_path_length = 1
        
        result = find_optimal_path(N, edges, risk_levels, transfer_risks, start, end, T, max_path_length)
        self.assertEqual(result, [0, 3])

if __name__ == '__main__':
    unittest.main()