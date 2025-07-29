import unittest
from data_transfer import optimal_transfer

class OptimalTransferTests(unittest.TestCase):
    def test_basic_example(self):
        N = 5
        routes = [(0, 1, 5, 2), (0, 2, 3, 4), (1, 3, 6, 1), (2, 3, 2, 3), (3, 4, 4, 5)]
        S = 0
        D = 4
        alpha = 1.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 21.00)
    
    def test_direct_path(self):
        N = 3
        routes = [(0, 2, 10, 5)]
        S = 0
        D = 2
        alpha = 1.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 15.00)  # cost 10 + (1.0 * time 5)
    
    def test_no_path_exists(self):
        N = 3
        routes = [(0, 1, 5, 2)]
        S = 0
        D = 2
        alpha = 1.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, -1)
        
    def test_multiple_paths_same_cost_prefer_faster(self):
        N = 4
        # Two paths from 0 to 3:
        # Path 1: 0->1->3 with cost 5+5=10 and time 2+6=8, total 10+(1*8)=18
        # Path 2: 0->2->3 with cost 8+2=10 and time 4+2=6, total 10+(1*6)=16
        routes = [(0, 1, 5, 2), (0, 2, 8, 4), (1, 3, 5, 6), (2, 3, 2, 2)]
        S = 0
        D = 3
        alpha = 1.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 16.00)  # Should choose the second path
        
    def test_higher_alpha_prefers_faster_path(self):
        N = 4
        # Two paths from 0 to 3:
        # Path 1: 0->1->3 with cost 2+2=4 and time 5+5=10, total 4+(2*10)=24
        # Path 2: 0->2->3 with cost 8+8=16 and time 1+2=3, total 16+(2*3)=22
        routes = [(0, 1, 2, 5), (0, 2, 8, 1), (1, 3, 2, 5), (2, 3, 8, 2)]
        S = 0
        D = 3
        alpha = 2.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 22.00)  # Should choose the second path due to higher alpha
        
    def test_zero_alpha_ignores_time(self):
        N = 4
        # Two paths from 0 to 3:
        # Path 1: 0->1->3 with cost 2+2=4 and time 10+10=20, total 4+(0*20)=4
        # Path 2: 0->2->3 with cost 5+5=10 and time 1+1=2, total 10+(0*2)=10
        routes = [(0, 1, 2, 10), (0, 2, 5, 1), (1, 3, 2, 10), (2, 3, 5, 1)]
        S = 0
        D = 3
        alpha = 0.0
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 4.00)  # Should choose the first path due to lower cost
        
    def test_large_network(self):
        N = 10
        routes = [
            (0, 1, 10, 5), (1, 2, 8, 6), (2, 9, 15, 10),  # Path 1: 0->1->2->9
            (0, 3, 5, 8), (3, 4, 6, 9), (4, 9, 12, 7),    # Path 2: 0->3->4->9
            (0, 5, 7, 4), (5, 6, 9, 6), (6, 9, 8, 5),     # Path 3: 0->5->6->9
            (0, 7, 12, 3), (7, 8, 6, 2), (8, 9, 4, 3),    # Path 4: 0->7->8->9
            (1, 7, 5, 7), (3, 5, 4, 3), (2, 4, 7, 8)      # Cross paths
        ]
        S = 0
        D = 9
        alpha = 1.5
        
        # Path 4 total: 12+6+4=22 cost, 3+2+3=8 time, 22+(1.5*8)=34
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 34.00)
        
    def test_fractional_alpha(self):
        N = 4
        # Two paths from 0 to 3:
        # Path 1: 0->1->3 with cost 10+10=20 and time 2+2=4, total 20+(0.5*4)=22
        # Path 2: 0->2->3 with cost 15+5=20 and time 1+1=2, total 20+(0.5*2)=21
        routes = [(0, 1, 10, 2), (0, 2, 15, 1), (1, 3, 10, 2), (2, 3, 5, 1)]
        S = 0
        D = 3
        alpha = 0.5
        
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 21.00)  # Should choose the second path
        
    def test_source_equals_destination(self):
        N = 5
        routes = [(0, 1, 5, 2), (0, 2, 3, 4), (1, 3, 6, 1), (2, 3, 2, 3), (3, 4, 4, 5)]
        S = 2
        D = 2
        alpha = 1.0
        
        # Since S=D, the cost and time should both be 0
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 0.00)
        
    def test_bidirectional_routes(self):
        N = 5
        # Create bidirectional routes (each connection works in both directions)
        routes = [
            (0, 1, 5, 2), (1, 0, 5, 2),  # 0 <-> 1
            (1, 2, 3, 4), (2, 1, 3, 4),  # 1 <-> 2
            (2, 3, 6, 1), (3, 2, 6, 1),  # 2 <-> 3
            (3, 4, 2, 3), (4, 3, 2, 3)   # 3 <-> 4
        ]
        S = 0
        D = 4
        alpha = 1.0
        
        # Path: 0->1->2->3->4 with cost 5+3+6+2=16 and time 2+4+1+3=10
        # Total: 16+(1*10)=26
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 26.00)
        
    def test_max_constraints(self):
        # Test with the maximum constraints given in the problem
        N = 1000
        # Generate a simple path from node 0 to node 999
        routes = [(i, i+1, 1, 1) for i in range(999)]
        S = 0
        D = 999
        alpha = 10.0
        
        # Path: 0->1->...->999 with cost 999 and time 999
        # Total: 999+(10*999)=10989
        result = optimal_transfer(N, routes, S, D, alpha)
        self.assertEqual(result, 10989.00)

if __name__ == '__main__':
    unittest.main()