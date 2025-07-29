import unittest
import threading
import time
from unittest.mock import patch
from dist_load_balancer import LoadBalancer, Server, HealthCheckStatus

class TestDistLoadBalancer(unittest.TestCase):
    def setUp(self):
        self.load_balancer = LoadBalancer()
    
    def test_add_and_remove_server(self):
        # Add a server
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        self.assertEqual(len(self.load_balancer.servers), 1)
        self.assertIn("server1", self.load_balancer.servers)
        
        # Add another server
        self.load_balancer.add_server("server2", "192.168.1.2:8080", 2)
        self.assertEqual(len(self.load_balancer.servers), 2)
        
        # Remove a server
        self.load_balancer.remove_server("server1")
        self.assertEqual(len(self.load_balancer.servers), 1)
        self.assertNotIn("server1", self.load_balancer.servers)
        self.assertIn("server2", self.load_balancer.servers)
    
    def test_server_health_checks(self):
        # Add a server
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        
        # By default, server should be healthy
        self.assertTrue(self.load_balancer.servers["server1"].is_healthy())
        
        # Mark server as unhealthy
        self.load_balancer.health_check_failed("server1")
        self.assertFalse(self.load_balancer.servers["server1"].is_healthy())
        
        # Mark server as healthy again
        self.load_balancer.health_check_passed("server1")
        self.assertTrue(self.load_balancer.servers["server1"].is_healthy())
    
    def test_weighted_round_robin_strategy(self):
        # Set strategy to weighted round robin
        self.load_balancer.set_strategy("weighted_round_robin")
        
        # Add servers with different weights
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)  # weight 1
        self.load_balancer.add_server("server2", "192.168.1.2:8080", 2)  # weight 2
        
        # Track how many times each server is selected
        selections = {"192.168.1.1:8080": 0, "192.168.1.2:8080": 0}
        
        # Make 300 requests
        for _ in range(300):
            next_server = self.load_balancer.get_next_server()
            selections[next_server] += 1
        
        # Server2 should be selected approximately twice as often as server1
        # Allow for some variation due to randomness in distribution
        ratio = selections["192.168.1.2:8080"] / selections["192.168.1.1:8080"]
        self.assertGreater(ratio, 1.8)  # Should be close to 2
        self.assertLess(ratio, 2.2)     # Allow for some variation
    
    def test_least_connections_strategy(self):
        # Set strategy to least connections
        self.load_balancer.set_strategy("least_connections")
        
        # Add servers
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        self.load_balancer.add_server("server2", "192.168.1.2:8080", 1)
        
        # Simulate server1 having 5 active connections
        self.load_balancer.servers["server1"].active_connections = 5
        
        # Server2 should be selected as it has fewer connections
        self.assertEqual(self.load_balancer.get_next_server(), "192.168.1.2:8080")
        
        # Now server2 has 1 active connection, server1 has 5
        self.assertEqual(self.load_balancer.servers["server2"].active_connections, 1)
        
        # Add 10 more connections to server2
        self.load_balancer.servers["server2"].active_connections = 10
        
        # Now server1 should be selected
        self.assertEqual(self.load_balancer.get_next_server(), "192.168.1.1:8080")
    
    def test_unhealthy_servers_skipped(self):
        # Add servers
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        self.load_balancer.add_server("server2", "192.168.1.2:8080", 1)
        
        # Mark server1 as unhealthy
        self.load_balancer.health_check_failed("server1")
        
        # Server2 should always be selected as server1 is unhealthy
        for _ in range(10):
            self.assertEqual(self.load_balancer.get_next_server(), "192.168.1.2:8080")
        
        # Mark server2 as unhealthy
        self.load_balancer.health_check_failed("server2")
        
        # No healthy servers, should raise exception
        with self.assertRaises(Exception):
            self.load_balancer.get_next_server()
    
    def test_consistent_hashing(self):
        # Add many servers
        for i in range(100):
            self.load_balancer.add_server(f"server{i}", f"192.168.1.{i}:8080", 1)
        
        # Get the server assigned to a specific key
        key = "user123"
        server_before = self.load_balancer._get_server_for_key(key)
        
        # Remove 10 random servers
        for i in range(10, 20):
            self.load_balancer.remove_server(f"server{i}")
        
        # Get the server assigned to the same key after removing servers
        server_after = self.load_balancer._get_server_for_key(key)
        
        # The server assigned to the key should remain the same in most cases
        # This is a probabilistic test, so it might occasionally fail
        # The probability of the key being reassigned is approximately 10/100 = 0.1
        # We will accept this test as valid most of the time
        if server_before == server_after:
            consistent = True
        else:
            # Check if the server was one of those removed
            consistent = server_before in [f"server{i}" for i in range(10, 20)]
        
        self.assertTrue(consistent)
    
    def test_thread_safety(self):
        # Add initial servers
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        self.load_balancer.add_server("server2", "192.168.1.2:8080", 1)
        
        # Define functions for threads
        def add_and_remove_servers():
            for i in range(100):
                self.load_balancer.add_server(f"thread_server{i}", f"192.168.2.{i}:8080", 1)
                time.sleep(0.001)  # Small delay to increase chance of race conditions
                self.load_balancer.remove_server(f"thread_server{i}")
        
        def perform_health_checks():
            for i in range(100):
                self.load_balancer.health_check_failed("server1")
                time.sleep(0.001)  # Small delay
                self.load_balancer.health_check_passed("server1")
        
        def get_next_server():
            for i in range(100):
                try:
                    self.load_balancer.get_next_server()
                except:
                    pass  # Ignore exceptions when no healthy servers
                time.sleep(0.001)  # Small delay
        
        # Create and start threads
        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=add_and_remove_servers))
            threads.append(threading.Thread(target=perform_health_checks))
            threads.append(threading.Thread(target=get_next_server))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # After all operations, we should still have our original servers
        self.assertIn("server1", self.load_balancer.servers)
        self.assertIn("server2", self.load_balancer.servers)
    
    def test_fault_tolerance(self):
        # Simulate a distributed setup with multiple load balancer instances
        lb1 = LoadBalancer(instance_id="lb1")
        lb2 = LoadBalancer(instance_id="lb2")
        
        # Add same servers to both load balancers
        lb1.add_server("server1", "192.168.1.1:8080", 1)
        lb1.add_server("server2", "192.168.1.2:8080", 1)
        
        lb2.add_server("server1", "192.168.1.1:8080", 1)
        lb2.add_server("server2", "192.168.1.2:8080", 1)
        
        # Simulate lb1 discovering a failed server through health check
        lb1.health_check_failed("server1")
        
        # Simulate propagation of this information to lb2
        lb2.health_check_failed("server1")
        
        # Both load balancers should now avoid the unhealthy server
        for _ in range(5):
            self.assertEqual(lb1.get_next_server(), "192.168.1.2:8080")
            self.assertEqual(lb2.get_next_server(), "192.168.1.2:8080")
    
    def test_circuit_breaker(self):
        # Add a server
        self.load_balancer.add_server("server1", "192.168.1.1:8080", 1)
        
        # Simulate multiple failed health checks
        for _ in range(5):
            self.load_balancer.health_check_failed("server1")
        
        # Circuit should be open now
        self.assertEqual(self.load_balancer.servers["server1"].circuit_state, "OPEN")
        
        # Server should be considered unhealthy when circuit is open
        self.assertFalse(self.load_balancer.servers["server1"].is_healthy())

    def test_server_expiration(self):
        # Add a server with a short time-to-live
        with patch('time.time', return_value=1000):  # Mock current time
            self.load_balancer.add_server("server1", "192.168.1.1:8080", 1, ttl=10)  # 10 second TTL
        
        # Check if server exists
        self.assertIn("server1", self.load_balancer.servers)
        
        # Jump ahead in time beyond the TTL
        with patch('time.time', return_value=1015):  # 15 seconds later
            # Remove expired servers
            self.load_balancer.remove_expired_servers()
            
            # Server should be gone now
            self.assertNotIn("server1", self.load_balancer.servers)

if __name__ == '__main__':
    unittest.main()