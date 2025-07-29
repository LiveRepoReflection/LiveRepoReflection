import unittest
from adaptive_load_balancer import assign_requests

class AdaptiveLoadBalancerTest(unittest.TestCase):
    def test_no_requests(self):
        # Test when there are no requests.
        N = 3
        requests = []
        capacities = [1, 2, 3]
        latencies = [
            [10, 20],
            [15, 5],
            [7, 30]
        ]
        request_data_sources = []
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        for worker_requests in result:
            self.assertEqual(worker_requests, [])

    def test_single_worker_single_request(self):
        # Single worker with one request.
        N = 1
        requests = ["req1"]
        capacities = [5]
        latencies = [[10, 20]]
        request_data_sources = [1]
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        self.assertEqual(result[0], ["req1"])

    def test_simple_optimal_assignment(self):
        # Two workers, clear optimal latency based routing.
        N = 2
        requests = ["req1", "req2", "req3", "req4"]
        capacities = [3, 3]
        latencies = [
            [10, 20],
            [15, 5]
        ]
        request_data_sources = [0, 0, 1, 1]
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        # Optimal assignment: worker0 gets requests needing data source 0, worker1 gets those needing data source 1.
        expected = [
            ["req1", "req2"],
            ["req3", "req4"]
        ]
        self.assertEqual(result, expected)

    def test_capacity_constraints(self):
        # Ensure that if the total requests equal the sum of the capacities,
        # no worker is assigned more requests than its capacity.
        N = 3
        requests = ["req1", "req2", "req3", "req4", "req5", "req6"]
        capacities = [1, 2, 3]
        latencies = [
            [5, 10],
            [10, 5],
            [7, 7]
        ]
        request_data_sources = [0, 0, 1, 1, 0, 1]
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        # Check that every worker has no more requests than its capacity.
        for i in range(N):
            self.assertLessEqual(len(result[i]), capacities[i])
        # Check that all requests are assigned exactly once.
        assigned = [req for worker in result for req in worker]
        self.assertCountEqual(assigned, requests)

    def test_order_preservation(self):
        # Check that the relative order of requests assigned to the same worker is preserved.
        N = 2
        requests = ["a", "b", "c", "d", "e"]
        capacities = [5, 5]
        latencies = [
            [1, 100],
            [100, 1]
        ]
        request_data_sources = [0, 1, 0, 1, 0]
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        # Expecting worker 0 to get requests for data source 0 and worker 1 for data source 1.
        worker0 = result[0]
        worker1 = result[1]
        # Check order preservation: the requests should appear in the same order they are in the original list.
        expected_worker0 = [req for req, ds in zip(requests, request_data_sources) if ds == 0]
        expected_worker1 = [req for req, ds in zip(requests, request_data_sources) if ds == 1]
        self.assertEqual(worker0, expected_worker0)
        self.assertEqual(worker1, expected_worker1)

    def test_large_input(self):
        # Simulate a larger input to ensure performance and structure adherence.
        N = 5
        M = 3
        num_requests = 100
        requests = [f"req{i}" for i in range(num_requests)]
        capacities = [30, 30, 30, 30, 30]  # total capacity = 150, which is > 100.
        latencies = [
            [1, 50, 100],
            [2, 40, 90],
            [3, 30, 80],
            [4, 20, 70],
            [5, 10, 60]
        ]
        # Cycle through data sources for requests.
        request_data_sources = [i % M for i in range(num_requests)]
        result = assign_requests(N, requests, capacities, latencies, request_data_sources)
        self.assertEqual(len(result), N)
        # Check that all requests are assigned exactly once.
        assigned = [req for worker in result for req in worker]
        self.assertCountEqual(assigned, requests)
        # Verify that within each worker, the order is preserved based on their original occurrence.
        positions = {req: idx for idx, req in enumerate(requests)}
        for worker in result:
            for i in range(1, len(worker)):
                self.assertLess(positions[worker[i-1]], positions[worker[i]])

if __name__ == '__main__':
    unittest.main()