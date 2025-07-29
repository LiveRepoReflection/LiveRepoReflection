import unittest
from packet_routing import optimize_routing

class PacketRoutingTest(unittest.TestCase):
    def test_basic_routing(self):
        n = 5
        links = [(1, 2, 10), (2, 3, 5), (1, 4, 15), (4, 5, 8), (3, 5, 2)]
        queries = [
            (1, 5, 30, 1),  # Source 1, Destination 5, Deadline 30, Priority 1
            (2, 4, 20, 2),  # Source 2, Destination 4, Deadline 20, Priority 2
            (3, 1, 10, 3),  # Source 3, Destination 1, Deadline 10, Priority 3
        ]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(len(result), 3)
        # Check result types
        for decision in result:
            self.assertIn(decision, ["ROUTE", "DELAY", "DROP"])
    
    def test_same_source_destination(self):
        n = 3
        links = [(1, 2, 5), (2, 3, 5)]
        queries = [(1, 1, 10, 1)]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["ROUTE"])
    
    def test_no_links(self):
        n = 5
        links = []
        queries = [(1, 5, 30, 1)]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["DROP"])
    
    def test_disconnected_network(self):
        n = 5
        links = [(1, 2, 10), (3, 4, 5)]  # Two disconnected components
        queries = [(1, 4, 20, 2)]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["DROP"])
    
    def test_negative_latency(self):
        n = 4
        links = [(1, 2, 10), (2, 3, -5), (3, 4, 10)]  # Negative latency on one link
        queries = [(1, 4, 15, 1)]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["ROUTE"])
    
    def test_negative_latency_cycle(self):
        n = 4
        links = [(1, 2, 10), (2, 3, 5), (3, 1, -20)]  # Negative cycle
        queries = [(1, 3, 5, 1)]
        
        result = optimize_routing(n, links, queries)
        # No specific assertion for the result since handling negative cycles
        # could be implemented in different ways
        self.assertIn(result[0], ["ROUTE", "DELAY", "DROP"])
    
    def test_deadline_constraints(self):
        n = 4
        links = [(1, 2, 10), (2, 3, 10), (3, 4, 10)]
        queries = [
            (1, 4, 35, 1),  # Can meet deadline
            (1, 4, 25, 1),  # Just meeting deadline
            (1, 4, 20, 1),  # Cannot meet deadline
        ]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(len(result), 3)
        # First query should route, last query should delay or drop
        self.assertEqual(result[0], "ROUTE")
        self.assertIn(result[2], ["DELAY", "DROP"])
    
    def test_multiple_routes(self):
        n = 5
        links = [
            (1, 2, 10), (2, 5, 10),  # Route 1->2->5, total latency: 20
            (1, 3, 5), (3, 4, 5), (4, 5, 5)  # Route 1->3->4->5, total latency: 15
        ]
        queries = [(1, 5, 25, 1)]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["ROUTE"])
    
    def test_large_network(self):
        n = 100
        # Create a line graph with increasing latency
        links = [(i, i+1, i) for i in range(1, n)]
        queries = [(1, n, 5000, 1)]
        
        result = optimize_routing(n, links, queries)
        self.assertIn(result[0], ["ROUTE", "DELAY", "DROP"])
    
    def test_priority_consideration(self):
        n = 5
        links = [(1, 2, 10), (2, 3, 5), (1, 4, 15), (4, 5, 8), (3, 5, 2)]
        queries = [
            (1, 5, 15, 3),  # High priority but tight deadline
            (1, 5, 15, 1),  # Low priority with same deadline
        ]
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(len(result), 2)
        # No specific assertion for the exact values, as it depends on the implementation
        # of priority handling, but the results should be valid routing decisions
        for decision in result:
            self.assertIn(decision, ["ROUTE", "DELAY", "DROP"])
    
    def test_edge_case_all_negative(self):
        n = 4
        links = [(1, 2, -5), (2, 3, -5), (3, 4, -5)]
        queries = [(1, 4, 0, 1)]  # Even with zero deadline, route should be possible
        
        result = optimize_routing(n, links, queries)
        self.assertEqual(result, ["ROUTE"])

if __name__ == "__main__":
    unittest.main()