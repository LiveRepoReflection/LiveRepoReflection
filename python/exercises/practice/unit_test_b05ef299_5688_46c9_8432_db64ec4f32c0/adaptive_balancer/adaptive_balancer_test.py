import unittest
from adaptive_balancer import LoadBalancer, Node, Request


class AdaptiveBalancerTest(unittest.TestCase):
    def setUp(self):
        # Initialize test nodes with different capacities, latencies, and locations
        self.node1 = Node("node1", 34.0522, -118.2437, capacity=100, latency=50)  # Los Angeles
        self.node2 = Node("node2", 37.7749, -122.4194, capacity=50, latency=100)  # San Francisco
        self.node3 = Node("node3", 40.7128, -74.0060, capacity=75, latency=75)    # New York
        self.load_balancer = LoadBalancer([self.node1, self.node2, self.node3])

    def test_initialization(self):
        self.assertEqual(len(self.load_balancer.nodes), 3)

    def test_basic_request_routing(self):
        request = Request("req1", 34.0522, -118.2437, priority="medium")  # Los Angeles location
        node_id = self.load_balancer.handle_request(request)
        self.assertIsNotNone(node_id)
        self.assertTrue(node_id in ["node1", "node2", "node3"])

    def test_geographic_routing(self):
        # Request from LA should prefer node1
        request_la = Request("req_la", 34.0522, -118.2437, priority="medium")
        node_id_la = self.load_balancer.handle_request(request_la)
        self.assertEqual(node_id_la, "node1")

    def test_priority_routing(self):
        # High priority request should get the lowest latency node
        request_high = Request("req_high", 35.0, -120.0, priority="high")
        node_id_high = self.load_balancer.handle_request(request_high)
        self.assertEqual(node_id_high, "node1")  # node1 has lowest latency

        # Low priority request might get higher latency node
        request_low = Request("req_low", 35.0, -120.0, priority="low")
        node_id_low = self.load_balancer.handle_request(request_low)
        self.assertIn(node_id_low, ["node1", "node2", "node3"])

    def test_capacity_updates(self):
        original_capacity = self.node1.capacity
        self.load_balancer.update_node_capacity("node1", 150)
        self.assertEqual(self.node1.capacity, 150)
        
        # Test that the load balancer adapts to capacity changes
        requests = [Request(f"req{i}", 34.0522, -118.2437, priority="medium") 
                   for i in range(200)]
        node_assignments = [self.load_balancer.handle_request(req) for req in requests]
        self.assertTrue(len(set(node_assignments)) > 1)  # Should use multiple nodes

    def test_latency_updates(self):
        self.load_balancer.update_node_latency("node2", 25)  # Make node2 fastest
        request = Request("req1", 37.7749, -122.4194, priority="high")
        node_id = self.load_balancer.handle_request(request)
        self.assertEqual(node_id, "node2")

    def test_node_failure_handling(self):
        self.node1.set_unhealthy()
        request = Request("req1", 34.0522, -118.2437, priority="medium")
        node_id = self.load_balancer.handle_request(request)
        self.assertNotEqual(node_id, "node1")  # Should not route to unhealthy node

    def test_load_distribution(self):
        # Generate many requests and check if load is distributed
        requests = [Request(f"req{i}", 36.0, -119.0, priority="medium") 
                   for i in range(100)]
        node_assignments = [self.load_balancer.handle_request(req) for req in requests]
        
        # Count assignments to each node
        assignment_counts = {node_id: node_assignments.count(node_id) 
                           for node_id in ["node1", "node2", "node3"]}
        
        # Verify that all nodes received some requests
        self.assertTrue(all(count > 0 for count in assignment_counts.values()))

    def test_edge_cases(self):
        # Test with all nodes at capacity
        self.load_balancer.update_node_capacity("node1", 0)
        self.load_balancer.update_node_capacity("node2", 0)
        self.load_balancer.update_node_capacity("node3", 0)
        
        request = Request("req1", 34.0522, -118.2437, priority="high")
        with self.assertRaises(Exception):  # Should raise exception when no capacity available
            self.load_balancer.handle_request(request)

        # Test with all nodes unhealthy
        self.node1.set_unhealthy()
        self.node2.set_unhealthy()
        self.node3.set_unhealthy()
        
        with self.assertRaises(Exception):  # Should raise exception when no healthy nodes
            self.load_balancer.handle_request(request)

    def test_concurrent_requests(self):
        # Simulate concurrent requests
        import threading
        
        def make_request():
            request = Request("req_concurrent", 34.0522, -118.2437, priority="medium")
            return self.load_balancer.handle_request(request)
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def test_priority_queue_ordering(self):
        # Test that high priority requests are handled before lower priority ones
        requests = [
            Request("req1", 34.0522, -118.2437, priority="low"),
            Request("req2", 34.0522, -118.2437, priority="high"),
            Request("req3", 34.0522, -118.2437, priority="medium")
        ]
        
        node_assignments = [self.load_balancer.handle_request(req) for req in requests]
        
        # The high priority request should get the lowest latency node
        self.assertEqual(node_assignments[1], "node1")

if __name__ == '__main__':
    unittest.main()