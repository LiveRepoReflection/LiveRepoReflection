import unittest
from route_lookup import find_best_route

class TestRouteLookup(unittest.TestCase):
    
    def test_exact_longest_prefix(self):
        routing_table = [
            ("10.0.0.0/8", "192.168.1.1"),
            ("10.1.0.0/16", "192.168.2.1"),
            ("10.1.2.0/24", "192.168.3.1"),
            ("0.0.0.0/0", "192.168.0.1"),
        ]
        destination_ip = "10.1.2.3"
        expected = "192.168.3.1"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Should return the next hop for the longest matching prefix")
        
    def test_multiple_matches_longest_wins(self):
        routing_table = [
            ("192.168.0.0/16", "A"),
            ("192.168.1.0/24", "B"),
        ]
        destination_ip = "192.168.1.50"
        expected = "B"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Should return the next hop corresponding to the longest matching prefix")
        
    def test_no_match_returns_none(self):
        routing_table = [
            ("10.0.0.0/8", "A"),
            ("172.16.0.0/12", "B")
        ]
        destination_ip = "192.168.1.1"
        expected = None
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Should return None if no matching route is found")
        
    def test_default_route_when_no_other_matches(self):
        routing_table = [
            ("10.0.0.0/8", "A"),
            ("0.0.0.0/0", "default"),
        ]
        destination_ip = "8.8.8.8"
        expected = "default"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Default route must be used when no other routes match")
        
    def test_edge_ip_of_range(self):
        routing_table = [
            ("10.0.0.0/8", "A"),
            ("10.0.0.0/24", "B"),
        ]
        # Testing highest IP in the /8 range that is not in /24 range
        destination_ip = "10.255.255.255"
        expected = "A"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Should correctly handle edge IP addresses for matching prefixes")
        
    def test_empty_routing_table(self):
        routing_table = []
        destination_ip = "192.168.1.1"
        expected = None
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "When routing table is empty, should return None")
        
    def test_order_irrelevance(self):
        # The order of entries should not affect the outcome.
        routing_table = [
            ("0.0.0.0/0", "default"),
            ("10.0.0.0/8", "A"),
            ("10.1.0.0/16", "B"),
            ("10.1.2.0/24", "C"),
        ]
        destination_ip = "10.1.2.100"
        expected = "C"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Order of the routing table entries should not affect the result")
        
    def test_overlapping_routes(self):
        routing_table = [
            ("192.168.0.0/16", "Net1"),
            ("192.168.1.0/24", "Net2"),
            ("192.168.1.128/25", "Net3")
        ]
        # 192.168.1.200 falls within all, longest prefix is /25 -> Net3
        destination_ip = "192.168.1.200"
        expected = "Net3"
        result = find_best_route(routing_table, destination_ip)
        self.assertEqual(result, expected, "Should choose the overlapping route with the longest prefix")
        
if __name__ == "__main__":
    unittest.main()