import unittest
from optimal_balancer import balance_load

class OptimalBalancerTest(unittest.TestCase):
    def test_basic_case(self):
        servers = [
            (1, 100, 0.9),  # server_id, capacity, health_score
            (2, 50, 0.7),
            (3, 75, 0.5)
        ]
        requests = [20, 30, 40, 15, 25, 35, 20, 10, 5, 10]
        time_window = 1000
        alpha = 0.6
        
        result = balance_load(servers, requests, time_window, alpha)
        
        # Check if result length matches requests length
        self.assertEqual(len(result), len(requests))
        
        # Check if all assignments are valid server IDs
        valid_server_ids = {s[0] for s in servers}
        self.assertTrue(all(sid in valid_server_ids for sid in result))
        
        # Check capacity constraints
        server_loads = {sid: 0 for sid, _, _ in servers}
        for req_idx, server_id in enumerate(result):
            server_loads[server_id] += requests[req_idx]
        
        for (sid, capacity, _) in servers:
            self.assertLessEqual(server_loads[sid], capacity)

    def test_empty_requests(self):
        servers = [(1, 100, 0.9)]
        requests = []
        time_window = 1000
        alpha = 0.5
        
        result = balance_load(servers, requests, time_window, alpha)
        self.assertEqual(result, [])

    def test_empty_servers(self):
        servers = []
        requests = [10, 20]
        time_window = 1000
        alpha = 0.5
        
        with self.assertRaises(ValueError):
            balance_load(servers, requests, time_window, alpha)

    def test_insufficient_capacity(self):
        servers = [
            (1, 10, 0.9),
            (2, 15, 0.8)
        ]
        requests = [20, 30, 40]  # Total: 90, exceeds total capacity of 25
        time_window = 1000
        alpha = 0.5
        
        with self.assertRaises(ValueError):
            balance_load(servers, requests, time_window, alpha)

    def test_zero_health_score(self):
        servers = [
            (1, 100, 0.0),
            (2, 100, 0.9)
        ]
        requests = [10, 20, 30]
        time_window = 1000
        alpha = 0.5
        
        result = balance_load(servers, requests, time_window, alpha)
        # All requests should be assigned to server 2 due to server 1's zero health score
        self.assertTrue(all(sid == 2 for sid in result))

    def test_single_server(self):
        servers = [(1, 1000, 1.0)]
        requests = [10, 20, 30, 40, 50]
        time_window = 1000
        alpha = 0.5
        
        result = balance_load(servers, requests, time_window, alpha)
        self.assertTrue(all(sid == 1 for sid in result))

    def test_equal_health_scores(self):
        servers = [
            (1, 100, 0.8),
            (2, 100, 0.8),
            (3, 100, 0.8)
        ]
        requests = [10, 20, 30, 40]
        time_window = 1000
        alpha = 1.0  # Focus only on latency
        
        result = balance_load(servers, requests, time_window, alpha)
        self.assertEqual(len(result), len(requests))

    def test_alpha_extremes(self):
        servers = [
            (1, 100, 0.9),
            (2, 100, 0.1)
        ]
        requests = [10, 20, 30]
        time_window = 1000
        
        # Test alpha = 0 (focus only on availability)
        result_availability = balance_load(servers, requests, time_window, 0.0)
        # All requests should go to the healthier server (1)
        self.assertTrue(all(sid == 1 for sid in result_availability))
        
        # Test alpha = 1 (focus only on latency)
        result_latency = balance_load(servers, requests, time_window, 1.0)
        self.assertEqual(len(result_latency), len(requests))

    def test_invalid_inputs(self):
        # Test invalid health score
        with self.assertRaises(ValueError):
            balance_load([(1, 100, 1.1)], [10], 1000, 0.5)
        
        # Test invalid capacity
        with self.assertRaises(ValueError):
            balance_load([(1, -10, 0.9)], [10], 1000, 0.5)
        
        # Test invalid alpha
        with self.assertRaises(ValueError):
            balance_load([(1, 100, 0.9)], [10], 1000, 1.5)
        
        # Test invalid time window
        with self.assertRaises(ValueError):
            balance_load([(1, 100, 0.9)], [10], -1000, 0.5)
        
        # Test negative request time
        with self.assertRaises(ValueError):
            balance_load([(1, 100, 0.9)], [-10], 1000, 0.5)

if __name__ == '__main__':
    unittest.main()