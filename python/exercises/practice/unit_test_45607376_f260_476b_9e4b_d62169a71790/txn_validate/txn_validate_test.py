import unittest
from txn_validate import validate_transaction


class TransactionValidateTest(unittest.TestCase):

    def test_simple_successful_transaction(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        timeout = 50
        transaction = [(1, "x", 10), (2, "y", 20)]
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))

    def test_simple_unsuccessful_transaction_due_to_timeout(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 100, 150], [100, 0, 200], [150, 200, 0]]
        timeout = 50  # Too short for the latency
        transaction = [(1, "x", 10), (2, "y", 20)]
        self.assertFalse(validate_transaction(N, graph, latency, timeout, transaction))

    def test_transaction_with_key_conflict(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        timeout = 100
        # Simulating a conflict by having a predefined state where key "x" is already being modified
        # This test assumes your implementation can handle this case
        transaction = [(1, "x", 10)]  # Assume "x" is already being modified
        self.assertFalse(validate_transaction(N, graph, latency, timeout, transaction, 
                                           conflicting_keys={1: ["x"]}))

    def test_complex_network_topology(self):
        N = 5
        # Database 0 can communicate with 1 and 2
        # Database 1 can communicate with 0 and 3
        # Database 2 can communicate with 0 and 4
        # Database 3 can communicate with 1
        # Database 4 can communicate with 2
        graph = [[1, 2], [0, 3], [0, 4], [1], [2]]
        latency = [
            [0, 10, 15, -1, -1],  # Database 0
            [10, 0, -1, 20, -1],  # Database 1
            [15, -1, 0, -1, 25],  # Database 2
            [-1, 20, -1, 0, -1],  # Database 3
            [-1, -1, 25, -1, 0]   # Database 4
        ]
        timeout = 100
        transaction = [(1, "x", 10), (3, "y", 20), (4, "z", 30)]
        # This test should pass if your implementation correctly handles complex topologies
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))

    def test_disconnected_network(self):
        N = 4
        # Database 0 can communicate with 1
        # Database 2 can communicate with 3
        # No connection between (0,1) and (2,3)
        graph = [[1], [0], [3], [2]]
        latency = [
            [0, 10, -1, -1],
            [10, 0, -1, -1],
            [-1, -1, 0, 15],
            [-1, -1, 15, 0]
        ]
        timeout = 100
        transaction = [(1, "x", 10), (3, "y", 20)]
        # Should fail because coordinator (0) cannot reach database 3
        self.assertFalse(validate_transaction(N, graph, latency, timeout, transaction))

    def test_single_database_transaction(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        timeout = 50
        transaction = [(0, "x", 10)]  # Only coordinator involved
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))

    def test_no_participating_databases(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        timeout = 50
        transaction = []  # Empty transaction
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))

    def test_large_network(self):
        # Create a larger network to test scaling
        N = 10
        graph = [[] for _ in range(N)]
        latency = [[-1 for _ in range(N)] for _ in range(N)]
        
        # Create a ring topology
        for i in range(N):
            graph[i].append((i+1) % N)
            graph[i].append((i-1) % N)
            latency[i][(i+1) % N] = 10
            latency[i][(i-1) % N] = 10
            latency[i][i] = 0
        
        timeout = 200
        transaction = [(i, f"key_{i}", i*10) for i in range(1, 5)]  # Use databases 1-4
        
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))

    def test_high_latency_failure(self):
        N = 5
        graph = [[i for i in range(1, N)], [0], [0], [0], [0]]  # Star topology
        latency = [[-1 for _ in range(N)] for _ in range(N)]
        
        # Set latencies
        for i in range(1, N):
            latency[0][i] = 60  # High latency from coordinator to other nodes
            latency[i][0] = 60
            latency[i][i] = 0
        latency[0][0] = 0
        
        timeout = 50  # Timeout less than round-trip time
        transaction = [(1, "x", 10), (2, "y", 20)]
        
        self.assertFalse(validate_transaction(N, graph, latency, timeout, transaction))

    def test_multiple_keys_per_database(self):
        N = 3
        graph = [[1, 2], [0, 2], [0, 1]]
        latency = [[0, 10, 15], [10, 0, 20], [15, 20, 0]]
        timeout = 100
        transaction = [(1, "x", 10), (1, "y", 20), (2, "z", 30)]  # Database 1 has two keys
        
        self.assertTrue(validate_transaction(N, graph, latency, timeout, transaction))


if __name__ == "__main__":
    unittest.main()