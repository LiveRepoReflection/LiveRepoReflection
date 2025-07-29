import unittest
from supply_routing import min_cost_flow

class TestSupplyRouting(unittest.TestCase):
    def test_basic_example(self):
        N = 2
        M = 2
        capacities = [100, 50]
        demands = [70, 80]
        costs = [[2, 3], [4, 1]]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        # Verify flow satisfies warehouse capacities
        for i in range(N):
            self.assertLessEqual(sum(flow[i]), capacities[i])
        
        # Verify flow satisfies retail store demands
        for j in range(M):
            store_flow = sum(flow[i][j] for i in range(N))
            self.assertEqual(store_flow, demands[j])
        
        # Calculate total cost and ensure it's optimal
        total_cost = sum(flow[i][j] * costs[i][j] for i in range(N) for j in range(M))
        self.assertLessEqual(total_cost, 280)  # Known optimal cost for this example
    
    def test_no_feasible_solution(self):
        N = 2
        M = 2
        capacities = [50, 20]  # Total capacity (70) < Total demand (100)
        demands = [40, 60]
        costs = [[1, 2], [3, 4]]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        self.assertIsNone(flow)
    
    def test_exactly_enough_capacity(self):
        N = 3
        M = 3
        capacities = [30, 40, 50]  # Total capacity (120) = Total demand (120)
        demands = [30, 40, 50]
        costs = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        # Verify flow satisfies warehouse capacities
        for i in range(N):
            self.assertLessEqual(sum(flow[i]), capacities[i])
        
        # Verify flow satisfies retail store demands
        for j in range(M):
            store_flow = sum(flow[i][j] for i in range(N))
            self.assertEqual(store_flow, demands[j])
    
    def test_excess_capacity(self):
        N = 2
        M = 3
        capacities = [100, 150]  # Total capacity (250) > Total demand (150)
        demands = [50, 60, 40]
        costs = [
            [10, 8, 6],
            [9, 12, 10]
        ]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        # Verify flow satisfies warehouse capacities
        for i in range(N):
            self.assertLessEqual(sum(flow[i]), capacities[i])
        
        # Verify flow satisfies retail store demands
        for j in range(M):
            store_flow = sum(flow[i][j] for i in range(N))
            self.assertEqual(store_flow, demands[j])
    
    def test_optimal_assignment(self):
        N = 3
        M = 3
        capacities = [20, 30, 10]
        demands = [15, 25, 20]
        costs = [
            [2, 4, 3],
            [1, 5, 2],
            [5, 1, 6]
        ]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        # Verify flow satisfies warehouse capacities
        for i in range(N):
            self.assertLessEqual(sum(flow[i]), capacities[i])
        
        # Verify flow satisfies retail store demands
        for j in range(M):
            store_flow = sum(flow[i][j] for i in range(N))
            self.assertEqual(store_flow, demands[j])
        
        # Calculate total cost
        total_cost = sum(flow[i][j] * costs[i][j] for i in range(N) for j in range(M))
        
        # Manual calculation of a potentially optimal solution (not necessarily the only one)
        manual_flow = [
            [15, 0, 5],   # Warehouse 0
            [0, 25, 5],   # Warehouse 1
            [0, 0, 10]    # Warehouse 2
        ]
        manual_cost = sum(manual_flow[i][j] * costs[i][j] for i in range(N) for j in range(M))
        
        # The algorithm should find a solution at least as good as our manual one
        self.assertLessEqual(total_cost, manual_cost)
    
    def test_large_scale(self):
        # A larger test case to evaluate performance
        N = 10
        M = 10
        capacities = [100] * N
        demands = [100] * M
        costs = [[i * j % 10 + 1 for j in range(M)] for i in range(N)]
        
        flow = min_cost_flow(N, M, capacities, demands, costs)
        
        # Verify flow satisfies warehouse capacities
        for i in range(N):
            self.assertLessEqual(sum(flow[i]), capacities[i])
        
        # Verify flow satisfies retail store demands
        for j in range(M):
            store_flow = sum(flow[i][j] for i in range(N))
            self.assertEqual(store_flow, demands[j])

if __name__ == '__main__':
    unittest.main()