import time
import threading
import unittest
from adaptive_lb import LoadBalancer, BackendServer

class TestAdaptiveLoadBalancer(unittest.TestCase):
    def setUp(self):
        # Initialize load balancer and two backend servers
        self.lb = LoadBalancer(heartbeat_timeout=2)  # heartbeat timeout in seconds
        self.server1 = BackendServer(id=1, capacity=5, latency=50)
        self.server2 = BackendServer(id=2, capacity=5, latency=30)  # lower latency, should be favored initially
        self.lb.add_server(self.server1)
        self.lb.add_server(self.server2)

    def test_server_selection_based_on_latency(self):
        # With both servers available and under capacity, server2 should be selected (lower latency)
        selected = self.lb.select_server()
        self.assertEqual(selected.id, self.server2.id)

    def test_overloaded_server_not_selected(self):
        # Simulate server2 being at full capacity
        for _ in range(self.server2.capacity):
            self.server2.current_load += 1
        selected = self.lb.select_server()
        # Should select server1 because server2 is overloaded
        self.assertEqual(selected.id, self.server1.id)
        # Reset server2 load for subsequent tests
        self.server2.current_load = 0

    def test_failure_detection(self):
        # Simulate heartbeat timeout for server1
        self.server1.last_heartbeat = time.time() - (self.lb.heartbeat_timeout + 1)
        self.lb.update_server_statuses()
        selected = self.lb.select_server()
        # Only server2 should be available
        self.assertEqual(selected.id, self.server2.id)

    def test_recovery_of_failed_server(self):
        # Fail server1 then recover it with a fresh heartbeat
        self.server1.last_heartbeat = time.time() - (self.lb.heartbeat_timeout + 1)
        self.lb.update_server_statuses()
        # Now simulate a new heartbeat for server1 with updated parameters
        self.server1.report_heartbeat(load=self.server1.current_load, latency=50)
        self.lb.update_server_statuses()
        selected = self.lb.select_server()
        # With both available, server2 still preferred because of lower latency.
        self.assertEqual(selected.id, self.server2.id)

    def test_new_server_addition(self):
        # Add a new server with best latency and higher capacity
        new_server = BackendServer(id=3, capacity=10, latency=20)
        self.lb.add_server(new_server)
        selected = self.lb.select_server()
        self.assertEqual(selected.id, new_server.id)

    def test_distributed_state_consistency(self):
        # Simulate a secondary load balancer sharing the same backend server state
        lb2 = LoadBalancer(heartbeat_timeout=2)
        lb2.add_server(self.server1)
        lb2.add_server(self.server2)
        # Update heartbeats with modified latencies via reports
        self.server1.report_heartbeat(load=self.server1.current_load, latency=40)
        self.server2.report_heartbeat(load=self.server2.current_load, latency=35)
        self.lb.update_server_statuses()
        lb2.update_server_statuses()
        selected1 = self.lb.select_server()
        selected2 = lb2.select_server()
        # Both load balancers should choose the same server based on the state updates
        self.assertEqual(selected1.id, selected2.id)

    def test_concurrent_request_distribution(self):
        # Simulate multiple threads sending requests concurrently
        results = []

        def send_request():
            server = self.lb.select_server()
            results.append(server.id)
            # Simulate processing by increasing the load, then decreasing it
            server.current_load += 1
            time.sleep(0.1)
            server.current_load -= 1

        threads = []
        for _ in range(10):
            t = threading.Thread(target=send_request)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        valid_ids = {self.server1.id, self.server2.id}
        for sid in results:
            self.assertIn(sid, valid_ids)

if __name__ == '__main__':
    unittest.main()