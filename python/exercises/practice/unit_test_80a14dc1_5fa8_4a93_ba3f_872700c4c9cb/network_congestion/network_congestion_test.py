import unittest
from network_congestion import assign_users

class NetworkCongestionTest(unittest.TestCase):

    def _validate_assignment(self, N, M, C, D, K, assignment):
        # Verify that assignment is not None and has correct length
        self.assertIsNotNone(assignment, "Assignment should not be None when a valid assignment exists.")
        self.assertEqual(len(assignment), M, "Assignment list length should match number of users.")
        # Verify each assignment is a valid server index.
        for server in assignment:
            self.assertIsInstance(server, int, "Server index should be an integer.")
            self.assertGreaterEqual(server, 0, "Server index cannot be negative.")
            self.assertLess(server, N, "Server index cannot exceed the total number of servers.")

        # Verify capacity constraints: sum of assigned user data must not exceed server capacity.
        server_loads = [0] * N
        for user, server in enumerate(assignment):
            server_loads[server] += D[user]
        for idx in range(N):
            self.assertLessEqual(server_loads[idx], C[idx],
                                 f"Total load on server {idx} exceeds its capacity.")

    def test_single_server_single_user(self):
        N = 1
        M = 1
        C = [100]
        D = [50]
        K = 2
        assignment = assign_users(N, M, C, D, K)
        self._validate_assignment(N, M, C, D, K, assignment)
        self.assertEqual(assignment, [0], "Only one server available so user must be assigned to server 0.")

    def test_multiple_servers_valid_assignment(self):
        N = 2
        M = 3
        C = [100, 100]
        D = [30, 40, 50]
        K = 2
        assignment = assign_users(N, M, C, D, K)
        self._validate_assignment(N, M, C, D, K, assignment)
        
    def test_no_possible_assignment_due_to_capacity(self):
        N = 2
        M = 3
        # The third user's data is 100, which exceeds any server capacity in this setup.
        C = [50, 60]
        D = [30, 40, 100]
        K = 1
        assignment = assign_users(N, M, C, D, K)
        self.assertIsNone(assignment, "Assignment should be None if no valid assignment is possible.")

    def test_assignment_with_non_integer_exponent(self):
        N = 3
        M = 5
        C = [80, 100, 60]
        D = [20, 30, 40, 10, 20]
        K = 2.5
        assignment = assign_users(N, M, C, D, K)
        self._validate_assignment(N, M, C, D, K, assignment)

    def test_complex_case(self):
        N = 4
        M = 8
        C = [100, 150, 120, 90]
        D = [20, 50, 30, 40, 10, 60, 30, 20]
        K = 3
        assignment = assign_users(N, M, C, D, K)
        self._validate_assignment(N, M, C, D, K, assignment)
        # Additionally, compute latency for each server:
        server_loads = [0] * N
        for user, server in enumerate(assignment):
            server_loads[server] += D[user]
        
        def latency(load, capacity, k):
            return (load / capacity) ** k
        
        latencies = [latency(load, C[i], K) for i, load in enumerate(server_loads)]
        max_latency = max(latencies)
        # Check that maximum latency is a float and non-negative.
        self.assertIsInstance(max_latency, float, "Latency should be a float value.")
        self.assertGreaterEqual(max_latency, 0.0, "Latency should be non-negative.")

if __name__ == '__main__':
    unittest.main()