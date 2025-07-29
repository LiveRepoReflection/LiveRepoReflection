import unittest
from cdn_optimizer import optimize_network

class TestCDNOptimizer(unittest.TestCase):
    def test_basic_assignment(self):
        data_centers = [(1, 1.0, 10.0)]  # id, capacity_gbps, cost_per_gbps
        user_requests = [(101, (37.7749, -122.4194), 200, 50),  # id, location, bandwidth_mbps, latency_req
                        (102, (34.0522, -118.2437), 300, 100)]
        latency_matrix = {
            ((37.7749, -122.4194), 1): 30,
            ((34.0522, -118.2437), 1): 60
        }
        result = optimize_network(data_centers, user_requests, latency_matrix)
        self.assertEqual(set(result[1]), {101, 102})
        
    def test_capacity_constraint(self):
        data_centers = [(1, 0.4, 10.0)]  # Only 400Mbps capacity
        user_requests = [(101, (37.7749, -122.4194), 200, 50),
                        (102, (34.0522, -118.2437), 300, 100)]
        latency_matrix = {
            ((37.7749, -122.4194), 1): 30,
            ((34.0522, -118.2437), 1): 60
        }
        result = optimize_network(data_centers, user_requests, latency_matrix)
        self.assertEqual(len(result[1]), 1)  # Should only assign one request

    def test_latency_constraint(self):
        data_centers = [(1, 1.0, 10.0)]
        user_requests = [(101, (37.7749, -122.4194), 200, 20)]  # 20ms latency requirement
        latency_matrix = {((37.7749, -122.4194), 1): 30}  # 30ms actual latency
        result = optimize_network(data_centers, user_requests, latency_matrix)
        self.assertEqual(len(result), 0)  # Should not assign any requests

    def test_multiple_data_centers(self):
        data_centers = [
            (1, 0.5, 10.0),
            (2, 0.5, 8.0)
        ]
        user_requests = [
            (101, (37.7749, -122.4194), 400, 50),
            (102, (34.0522, -118.2437), 300, 50)
        ]
        latency_matrix = {
            ((37.7749, -122.4194), 1): 30,
            ((37.7749, -122.4194), 2): 40,
            ((34.0522, -118.2437), 1): 35,
            ((34.0522, -118.2437), 2): 25
        }
        result = optimize_network(data_centers, user_requests, latency_matrix)
        self.assertEqual(len(result), 2)
        total_requests = sum(len(reqs) for reqs in result.values())
        self.assertEqual(total_requests, 2)

    def test_empty_inputs(self):
        result = optimize_network([], [], {})
        self.assertEqual(result, {})

    def test_large_scale(self):
        # Generate large test case
        import random
        random.seed(42)
        
        n_centers = 100
        n_requests = 1000
        
        data_centers = [
            (i, random.uniform(0.5, 2.0), random.uniform(5.0, 15.0))
            for i in range(1, n_centers + 1)
        ]
        
        user_requests = [
            (i, 
             (random.uniform(-90, 90), random.uniform(-180, 180)),
             random.randint(50, 500),
             random.randint(50, 200))
            for i in range(1, n_requests + 1)
        ]
        
        latency_matrix = {
            (req[1], dc[0]): random.randint(10, 250)
            for req in user_requests
            for dc in data_centers
        }
        
        result = optimize_network(data_centers, user_requests, latency_matrix)
        # Verify basic properties of the solution
        self.assertIsInstance(result, dict)
        for dc_id, requests in result.items():
            self.assertIsInstance(requests, list)
            self.assertTrue(all(isinstance(req_id, int) for req_id in requests))

    def test_cost_optimization(self):
        data_centers = [
            (1, 1.0, 10.0),  # expensive
            (2, 1.0, 5.0)    # cheaper
        ]
        user_requests = [(101, (0, 0), 500, 100)]  # Single request that could go to either
        latency_matrix = {
            ((0, 0), 1): 50,
            ((0, 0), 2): 50
        }
        result = optimize_network(data_centers, user_requests, latency_matrix)
        self.assertIn(101, result[2])  # Should prefer cheaper data center

if __name__ == '__main__':
    unittest.main()