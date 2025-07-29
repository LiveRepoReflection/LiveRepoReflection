import unittest
from network_alloc import network_alloc

class TestNetworkAlloc(unittest.TestCase):
    def test_no_edges_no_requests(self):
        # Minimal graph with no edges and no requests.
        N = 2
        E = 0
        R = 0
        reduction = 5.0  # percentage reduction (won't matter)
        edges = []
        requests = []
        self.assertEqual(network_alloc(N, edges, requests, reduction), 0)

    def test_single_request_success(self):
        # Graph with simple path that can satisfy the request.
        N = 3
        E = 2
        R = 1
        reduction = 1.0
        # Edges: 0->1 with capacity 10, 1->2 with capacity 10.
        edges = [
            (0, 1, 10),
            (1, 2, 10)
        ]
        # Request: from 0 to 2 for amount 5.
        requests = [
            (0, 2, 5)
        ]
        self.assertEqual(network_alloc(N, edges, requests, reduction), 1)

    def test_single_request_failure(self):
        # Graph where the only available path does not have enough capacity.
        N = 3
        E = 2
        R = 1
        reduction = 1.0
        edges = [
            (0, 1, 3),
            (1, 2, 3)
        ]
        # Request exceeds path capacity.
        requests = [
            (0, 2, 5)
        ]
        self.assertEqual(network_alloc(N, edges, requests, reduction), 0)

    def test_sequential_requests(self):
        # Graph with two requests in sequence.
        N = 4
        E = 4
        R = 2
        # Use a high reduction rate to observe cumulative capacity reduction.
        reduction = 50.0  # 50% capacity reduction after each request
        edges = [
            (0, 1, 100),
            (1, 3, 100),
            (0, 2, 50),
            (2, 3, 50)
        ]
        # Request 1: 0->3, amount 20 (choose path 0->1->3)
        # After subtracting 20, capacities on that path become 80, then halved to 40.
        # Request 2: 0->3, amount 30 (now 0->1->3 path has capacity 40, sufficient)
        requests = [
            (0, 3, 20),
            (0, 3, 30)
        ]
        self.assertEqual(network_alloc(N, edges, requests, reduction), 2)

    def test_floating_precision_edge(self):
        # Test precision issues when remaining capacity equals required amount.
        N = 2
        E = 1
        R = 2
        reduction = 0.01  # 0.01% reduction after each request
        edges = [
            (0, 1, 100)
        ]
        # Request 1 uses 50 units, leaving exactly 50.
        # After reduction: 50 * (1 - 0.0001) = 49.995, approximately 50.
        # Request 2 requires 49.995 units.
        requests = [
            (0, 1, 50),
            (0, 1, 49.995)
        ]
        self.assertEqual(network_alloc(N, edges, requests, reduction), 2)

    def test_parallel_edges(self):
        # Test graph with multiple parallel edges.
        # Here multiple edges from 0 to 1 exist.
        # The algorithm should consider each independently.
        N = 3
        E = 3
        reduction = 10.0  # 10% reduction after each request
        edges = [
            (0, 1, 10),
            (0, 1, 5),
            (1, 2, 7)
        ]
        # Request: from 0 to 2, amount 7.
        # A possible solution: use the first edge from 0->1 (capacity 10) and 1->2 (7),
        # which satisfies the request.
        requests = [
            (0, 2, 7)
        ]
        self.assertEqual(network_alloc(N, edges, requests, reduction), 1)

if __name__ == '__main__':
    unittest.main()