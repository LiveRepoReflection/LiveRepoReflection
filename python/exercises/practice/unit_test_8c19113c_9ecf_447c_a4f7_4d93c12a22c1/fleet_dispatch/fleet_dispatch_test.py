import unittest
from fleet_dispatch import dispatch_fleet

class FleetDispatchTest(unittest.TestCase):
    def test_empty_requests(self):
        # Even if some edges exist, no requests means reward is zero.
        edges = [(0, 1, 10), (1, 2, 10)]
        requests = []
        num_avs = 3
        depot = 0
        T = 100
        result = dispatch_fleet(edges, requests, num_avs, depot, T)
        self.assertEqual(result, 0)

    def test_single_request_fulfillable(self):
        # Graph: 0->1 and 1->2. Request from 1 to 2, request_time=0.
        edges = [(0, 1, 10), (1, 2, 5)]
        requests = [
            (1, 2, 0, 100, 15)  # Must be reached within 15 seconds.
        ]
        num_avs = 1
        depot = 0
        T = 50
        result = dispatch_fleet(edges, requests, num_avs, depot, T)
        # AV can reach node 1 in 10 seconds which is within the 15-second max waiting.
        self.assertEqual(result, 100)

    def test_request_expired(self):
        # Graph where travel from depot to pickup takes longer than allowed max waiting time.
        edges = [(0, 1, 30), (1, 2, 5)]
        requests = [
            (1, 2, 0, 100, 10)  # Cannot reach node 1 from 0 within 10 seconds.
        ]
        num_avs = 1
        depot = 0
        T = 50
        result = dispatch_fleet(edges, requests, num_avs, depot, T)
        self.assertEqual(result, 0)

    def test_multiple_requests(self):
        # A small city graph is defined.
        # Graph edges:
        # 0->1: 5, 1->2: 5, 0->2: 12, 2->3: 5, 1->3: 10
        edges = [(0, 1, 5), (1, 2, 5), (0, 2, 12), (2, 3, 5), (1, 3, 10)]
        # Three ride requests:
        # Request 1: pickup at 1, dropoff at 2, request at t=0, reward=50, max_wait=10.
        # Request 2: pickup at 2, dropoff at 3, request at t=12, reward=70, max_wait=10.
        # Request 3: pickup at 1, dropoff at 3, request at t=5, reward=60, max_wait=10.
        requests = [
            (1, 2, 0, 50, 10),
            (2, 3, 12, 70, 10),
            (1, 3, 5, 60, 10)
        ]
        num_avs = 2
        depot = 0
        T = 50
        # One optimal strategy:
        # AV1: Request 1 (arrives at 1 in 5 sec, ride to 2 in 5 sec, available at t=10) then Request 2 (pickup at 2 available on time).
        # AV2: Request 3 (arrives at 1 in 5 sec from depot, ride to 3 in 10 sec, available at t=15).
        # Total reward = 50 + 70 + 60 = 180.
        result = dispatch_fleet(edges, requests, num_avs, depot, T)
        self.assertEqual(result, 180)

    def test_time_limit_exceeded(self):
        # Generate a linear graph with 50 intersections.
        n = 50
        edges = []
        for i in range(n - 1):
            edges.append((i, i + 1, 1))
        # Generate requests that hop from one node to the next.
        requests = []
        for i in range(n - 2):
            # Request from node i+1 to node i+2, request time=i, reward=10, max_wait=5.
            requests.append((i + 1, i + 2, i, 10, 5))
        num_avs = 3
        depot = 0
        T = 100
        result = dispatch_fleet(edges, requests, num_avs, depot, T)
        # If all requests are completed, total reward = number of requests * 10.
        expected_reward = len(requests) * 10
        self.assertEqual(result, expected_reward)

if __name__ == '__main__':
    unittest.main()