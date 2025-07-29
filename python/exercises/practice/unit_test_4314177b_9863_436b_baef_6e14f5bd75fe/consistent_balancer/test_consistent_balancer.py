import unittest
import random
import string
from consistent_balancer import ConsistentBalancer

class TestConsistentBalancer(unittest.TestCase):
    def setUp(self):
        self.servers = ["server1", "server2", "server3"]
        self.virtual_nodes = 100
        self.balancer = ConsistentBalancer(self.servers, self.virtual_nodes)
        
    def test_initialization(self):
        self.assertEqual(len(self.balancer.ring), len(self.servers) * self.virtual_nodes)
        
    def test_add_server(self):
        new_server = "server4"
        self.balancer.add_server(new_server)
        self.assertEqual(len(self.balancer.ring), (len(self.servers) + 1) * self.virtual_nodes)
        
    def test_remove_server(self):
        server_to_remove = "server2"
        self.balancer.remove_server(server_to_remove)
        self.assertEqual(len(self.balancer.ring), (len(self.servers) - 1) * self.virtual_nodes)
        
    def test_get_server(self):
        content_id = "content123"
        server = self.balancer.get_server(content_id)
        self.assertIn(server, self.servers)
        
    def test_get_server_after_removal(self):
        content_id = "content123"
        original_server = self.balancer.get_server(content_id)
        self.balancer.remove_server(original_server)
        new_server = self.balancer.get_server(content_id)
        self.assertNotEqual(original_server, new_server)
        self.assertIn(new_server, [s for s in self.servers if s != original_server])
        
    def test_empty_servers(self):
        empty_balancer = ConsistentBalancer([], self.virtual_nodes)
        with self.assertRaises(ValueError):
            empty_balancer.get_server("content123")
            
    def test_consistent_hashing(self):
        content_id = "content123"
        original_server = self.balancer.get_server(content_id)
        
        # Add new server and verify minimal redistribution
        self.balancer.add_server("server4")
        self.assertEqual(self.balancer.get_server(content_id), original_server)
        
        # Remove a different server and verify no change
        other_servers = [s for s in self.servers if s != original_server]
        self.balancer.remove_server(other_servers[0])
        self.assertEqual(self.balancer.get_server(content_id), original_server)
        
    def test_load_distribution(self):
        content_ids = [''.join(random.choices(string.ascii_lowercase, k=10)) for _ in range(1000)]
        distribution = {}
        
        for cid in content_ids:
            server = self.balancer.get_server(cid)
            distribution[server] = distribution.get(server, 0) + 1
            
        # Verify relatively even distribution
        counts = list(distribution.values())
        self.assertLess(max(counts) - min(counts), 150)  # Allow 15% variance
        
    def test_virtual_nodes_impact(self):
        low_vnode_balancer = ConsistentBalancer(self.servers, 10)
        high_vnode_balancer = ConsistentBalancer(self.servers, 1000)
        
        content_ids = [''.join(random.choices(string.ascii_lowercase, k=10)) for _ in range(1000)]
        
        def get_std_dev(balancer):
            distribution = {}
            for cid in content_ids:
                server = balancer.get_server(cid)
                distribution[server] = distribution.get(server, 0) + 1
            counts = list(distribution.values())
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            return variance ** 0.5
            
        self.assertLess(get_std_dev(high_vnode_balancer), get_std_dev(low_vnode_balancer))

if __name__ == '__main__':
    unittest.main()