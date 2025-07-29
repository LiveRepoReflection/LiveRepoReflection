import unittest
import math

from qkd_network import optimize_network

class TestQKDNetwork(unittest.TestCase):

    def compute_effective_rate(self, network, path, amp_factor):
        # Compute the effective key rate along the given path.
        # Start with 1 bit/s at source.
        rate = 1.0
        # For each edge, multiply by (1 - loss) and then, if it's a relay (not the final hop), apply amp_factor.
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            loss = network[u][v]
            rate *= (1 - loss)
            # If not the last edge, apply amplification at the relay node.
            if i < len(path) - 2:
                rate *= amp_factor
        return rate

    def test_single_request_valid(self):
        # Simple network with one valid path.
        network = {
            0: {1: 0.2},
            1: {0: 0.2, 2: 0.1},
            2: {1: 0.1}
        }
        requests = [(0, 2, 500)]
        min_key_rate = 0.5
        node_capacity = 1000
        amp_factor = 0.8

        result = optimize_network(network, requests, min_key_rate, node_capacity, amp_factor)
        self.assertIsNotNone(result, "Expected a valid solution for single request")
        
        total_time, path_assignments = result
        # There should be one request with index 0.
        self.assertIn(0, path_assignments)
        path = path_assignments[0]
        # Verify that the path starts at source and ends at destination.
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 2)
        # Verify that each consecutive pair is connected in the network.
        for i in range(len(path)-1):
            self.assertIn(path[i+1], network[path[i]], f"Edge from {path[i]} to {path[i+1]} does not exist")
        effective_rate = self.compute_effective_rate(network, path, amp_factor)
        self.assertGreaterEqual(effective_rate, min_key_rate, "Effective key rate is below the minimum threshold")
        # Check that time is calculated approximately: time = key_size / effective_rate
        expected_time = 500 / effective_rate
        self.assertAlmostEqual(total_time, expected_time, places=5, 
                               msg="Total time does not match expected distribution time")

    def test_multiple_requests_valid(self):
        # Network with multiple requests.
        network = {
            0: {1: 0.1, 2: 0.2},
            1: {0: 0.1, 3: 0.3},
            2: {0: 0.2, 3: 0.4},
            3: {1: 0.3, 2: 0.4}
        }
        requests = [(0, 3, 1024), (1, 2, 2048)]
        min_key_rate = 0.1
        node_capacity = 1000
        amp_factor = 0.9

        result = optimize_network(network, requests, min_key_rate, node_capacity, amp_factor)
        self.assertIsNotNone(result, "Expected a valid solution for multiple requests")
        total_time, path_assignments = result
        
        # Ensure all request indices are assigned paths.
        self.assertEqual(set(path_assignments.keys()), {0, 1})
        
        total_computed_time = 0.0
        for idx, req in enumerate(requests):
            src, dest, key_size = req
            path = path_assignments[idx]
            # Check source and destination.
            self.assertEqual(path[0], src, f"Request {idx} does not start at the correct source")
            self.assertEqual(path[-1], dest, f"Request {idx} does not end at the correct destination")
            # Check connectivity.
            for i in range(len(path)-1):
                self.assertIn(path[i+1], network[path[i]], f"Edge from {path[i]} to {path[i+1]} does not exist in request {idx}")
            effective_rate = self.compute_effective_rate(network, path, amp_factor)
            self.assertGreaterEqual(effective_rate, min_key_rate, f"Effective key rate below threshold for request {idx}")
            request_time = key_size / effective_rate
            total_computed_time += request_time

        self.assertAlmostEqual(total_time, total_computed_time, places=5, 
                               msg="Total time does not equal the sum of individual request times")

    def test_invalid_due_to_threshold(self):
        # Network where loss rates are too high and effective rate falls below min_key_rate.
        network = {
            0: {1: 0.9},
            1: {0: 0.9, 2: 0.9},
            2: {1: 0.9}
        }
        requests = [(0, 2, 500)]
        min_key_rate = 0.2
        node_capacity = 1000
        amp_factor = 0.8

        result = optimize_network(network, requests, min_key_rate, node_capacity, amp_factor)
        self.assertIsNone(result, "Expected no valid solution due to effective key rate below threshold")

    def test_invalid_due_to_capacity(self):
        # Network where node capacity is insufficient.
        # In this test, we simulate insufficient capacity by setting a very low node capacity.
        network = {
            0: {1: 0.1},
            1: {0: 0.1, 2: 0.1},
            2: {1: 0.1}
        }
        requests = [(0, 2, 1500)]
        min_key_rate = 0.5
        node_capacity = 0.5  # Insufficient capacity (even if effective rate is high, capacity is too low)
        amp_factor = 0.8

        result = optimize_network(network, requests, min_key_rate, node_capacity, amp_factor)
        self.assertIsNone(result, "Expected no valid solution due to node capacity violation")

if __name__ == '__main__':
    unittest.main()