import unittest
from optimal_routing import find_optimal_route

class TestOptimalRouting(unittest.TestCase):
    
    def test_simple_network(self):
        N = 4
        links = [(0, 1, 10), (1, 2, 15), (2, 3, 20), (0, 3, 5)]
        critical_nodes = {1, 2}
        start = 0
        end = 3
        penalty_factor = 2
        
        # Direct path 0->3 should be optimal (avoiding critical nodes)
        expected_route = [0, 3]
        self.assertEqual(find_optimal_route(N, links, critical_nodes, start, end, penalty_factor), expected_route)
    
    def test_route_through_critical_nodes(self):
        N = 3
        links = [(0, 1, 10), (1, 2, 15)]
        critical_nodes = {1}
        start = 0
        end = 2
        penalty_factor = 0.5
        
        # Only path is through the critical node
        expected_route = [0, 1, 2]
        self.assertEqual(find_optimal_route(N, links, critical_nodes, start, end, penalty_factor), expected_route)
    
    def test_no_route_exists(self):
        N = 4
        links = [(0, 1, 10), (2, 3, 15)]  # Disconnected graph
        critical_nodes = {1, 3}
        start = 0
        end = 3
        penalty_factor = 2
        
        # No route exists
        expected_route = []
        self.assertEqual(find_optimal_route(N, links, critical_nodes, start, end, penalty_factor), expected_route)
    
    def test_complex_network(self):
        N = 6
        links = [
            (0, 1, 10), (0, 2, 15), (1, 2, 5),
            (1, 3, 10), (2, 3, 20), (2, 4, 15),
            (3, 4, 10), (3, 5, 5), (4, 5, 10)
        ]
        critical_nodes = {1, 3}
        start = 0
        end = 5
        penalty_factor = 3
        
        # Should find optimal path considering penalties
        # Route 0->2->4->5 avoids both critical nodes 1 and 3
        expected_route = [0, 2, 4, 5]
        result = find_optimal_route(N, links, critical_nodes, start, end, penalty_factor)
        self.assertEqual(result, expected_route)
    
    def test_high_penalty_critical_nodes(self):
        N = 5
        links = [
            (0, 1, 10), (0, 2, 5), 
            (1, 3, 10), (2, 3, 15),
            (3, 4, 10)
        ]
        critical_nodes = {1, 3}
        start = 0
        end = 4
        penalty_factor = 100
        
        # With very high penalty, might take a longer path to avoid critical nodes
        # But there's no way to avoid node 3 when going from 0 to 4
        # So optimal route is 0->2->3->4 (avoiding critical node 1)
        result = find_optimal_route(N, links, critical_nodes, start, end, penalty_factor)
        self.assertEqual(result, [0, 2, 3, 4])
    
    def test_all_critical_nodes(self):
        N = 4
        links = [(0, 1, 10), (1, 2, 15), (2, 3, 20)]
        critical_nodes = {0, 1, 2, 3}  # All nodes are critical
        start = 0
        end = 3
        penalty_factor = 1
        
        # All nodes are critical, so the shortest path is still optimal
        expected_route = [0, 1, 2, 3]
        self.assertEqual(find_optimal_route(N, links, critical_nodes, start, end, penalty_factor), expected_route)
    
    def test_zero_penalty_factor(self):
        N = 5
        links = [
            (0, 1, 10), (0, 2, 20),
            (1, 3, 15), (2, 3, 10),
            (3, 4, 5)
        ]
        critical_nodes = {1, 2}
        start = 0
        end = 4
        penalty_factor = 0
        
        # With zero penalty, the shortest path is optimal regardless of critical nodes
        # Should choose 0->1->3->4 as it has fewer hops than 0->2->3->4
        result = find_optimal_route(N, links, critical_nodes, start, end, penalty_factor)
        self.assertEqual(result, [0, 1, 3, 4])

    def test_higher_bandwidth_preference(self):
        N = 4
        links = [(0, 1, 100), (1, 3, 50), (0, 2, 20), (2, 3, 20)]
        critical_nodes = {1, 2}
        start = 0
        end = 3
        penalty_factor = 0.5
        
        # All paths have equal length, and both go through a critical node
        # Should prefer the path with higher bandwidth: 0->1->3
        expected_route = [0, 1, 3]
        self.assertEqual(find_optimal_route(N, links, critical_nodes, start, end, penalty_factor), expected_route)
    
    def test_large_network_performance(self):
        # Create a larger network to test performance
        N = 1000
        links = []
        
        # Create a grid-like network
        for i in range(30):
            for j in range(30):
                node = i * 30 + j
                if j < 29:  # Connect horizontally
                    links.append((node, node + 1, 10))
                if i < 29:  # Connect vertically
                    links.append((node, node + 30, 10))
        
        critical_nodes = {i for i in range(0, 900, 100)}  # Some critical nodes
        start = 0
        end = 899
        penalty_factor = 1
        
        # Just test that it runs without timing out - this is a performance test
        route = find_optimal_route(N, links, critical_nodes, start, end, penalty_factor)
        self.assertIsInstance(route, list)
        if route:  # If a route was found
            self.assertEqual(route[0], start)
            self.assertEqual(route[-1], end)

if __name__ == '__main__':
    unittest.main()