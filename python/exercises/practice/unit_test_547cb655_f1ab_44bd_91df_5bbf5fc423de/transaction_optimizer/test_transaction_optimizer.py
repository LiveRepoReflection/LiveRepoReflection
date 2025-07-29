import unittest
from transaction_optimizer import optimize_transactions


class TransactionOptimizerTest(unittest.TestCase):
    def test_single_service_transaction(self):
        # When a transaction involves only one service, the order is trivial
        N = 3
        M = 1
        P = [10, 20, 30]
        C = [5, 15, 25]
        Adj = [[0, 10, 15], [10, 0, 5], [15, 5, 0]]
        T = [[1]]
        expected = [[1]]
        self.assertEqual(optimize_transactions(N, M, P, C, Adj, T), expected)

    def test_small_example(self):
        # Basic test case with a small number of services and transactions
        N = 3
        M = 2
        P = [10, 20, 30]
        C = [5, 15, 25]
        Adj = [[0, 10, 15], [10, 0, 5], [15, 5, 0]]
        T = [[0, 1, 2], [1, 0]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        # Verify the result maintains the same services in each transaction
        self.assertEqual(set(result[0]), set(T[0]))
        self.assertEqual(set(result[1]), set(T[1]))
        
        # We can't hardcode the expected order since multiple valid solutions may exist
        # Instead, we'll verify that the result is a valid permutation

    def test_fully_connected_network(self):
        # All services are directly connected with equal costs
        N = 4
        M = 2
        P = [10, 20, 30, 15]
        C = [5, 15, 25, 10]
        Adj = [
            [0, 5, 5, 5],
            [5, 0, 5, 5],
            [5, 5, 0, 5],
            [5, 5, 5, 0]
        ]
        T = [[0, 1, 2, 3], [1, 2]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        self.assertEqual(set(result[0]), set(T[0]))
        self.assertEqual(set(result[1]), set(T[1]))

    def test_disconnected_network(self):
        # Some services are not directly connected
        N = 4
        M = 1
        P = [10, 20, 30, 15]
        C = [5, 15, 25, 10]
        Adj = [
            [0, 5, 0, 5],
            [5, 0, 5, 0],
            [0, 5, 0, 5],
            [5, 0, 5, 0]
        ]
        T = [[0, 2, 3]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        self.assertEqual(set(result[0]), set(T[0]))

    def test_sparse_network(self):
        # A more realistic sparse network topology
        N = 5
        M = 3
        P = [10, 20, 30, 15, 25]
        C = [5, 15, 25, 10, 20]
        Adj = [
            [0, 10, 0, 15, 0],
            [10, 0, 20, 0, 0],
            [0, 20, 0, 5, 30],
            [15, 0, 5, 0, 25],
            [0, 0, 30, 25, 0]
        ]
        T = [[0, 1, 3], [1, 2, 4], [0, 2, 3, 4]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        for i in range(M):
            self.assertEqual(set(result[i]), set(T[i]))

    def test_linear_network(self):
        # Services are arranged in a line
        N = 5
        M = 2
        P = [10, 20, 30, 15, 25]
        C = [5, 15, 25, 10, 20]
        Adj = [
            [0, 10, 0, 0, 0],
            [10, 0, 20, 0, 0],
            [0, 20, 0, 15, 0],
            [0, 0, 15, 0, 30],
            [0, 0, 0, 30, 0]
        ]
        T = [[0, 2, 4], [1, 3]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        for i in range(M):
            self.assertEqual(set(result[i]), set(T[i]))

    def test_large_case(self):
        # A larger test case
        N = 10
        M = 5
        P = [10, 20, 30, 15, 25, 35, 20, 15, 10, 30]
        C = [5, 15, 25, 10, 20, 30, 15, 10, 5, 25]
        Adj = [
            [0, 10, 0, 0, 0, 0, 0, 0, 15, 0],
            [10, 0, 20, 0, 0, 0, 0, 0, 0, 0],
            [0, 20, 0, 15, 0, 0, 0, 0, 0, 0],
            [0, 0, 15, 0, 30, 0, 0, 0, 0, 0],
            [0, 0, 0, 30, 0, 25, 0, 0, 0, 0],
            [0, 0, 0, 0, 25, 0, 35, 0, 0, 0],
            [0, 0, 0, 0, 0, 35, 0, 20, 0, 0],
            [0, 0, 0, 0, 0, 0, 20, 0, 10, 0],
            [15, 0, 0, 0, 0, 0, 0, 10, 0, 30],
            [0, 0, 0, 0, 0, 0, 0, 0, 30, 0]
        ]
        T = [
            [0, 2, 4, 6, 8],
            [1, 3, 5, 7, 9],
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [7, 8, 9]
        ]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        for i in range(M):
            self.assertEqual(set(result[i]), set(T[i]))

    def test_equal_prepare_commit_costs(self):
        # All services have the same prepare and commit costs
        N = 4
        M = 2
        P = [20, 20, 20, 20]
        C = [10, 10, 10, 10]
        Adj = [
            [0, 10, 20, 30],
            [10, 0, 15, 25],
            [20, 15, 0, 35],
            [30, 25, 35, 0]
        ]
        T = [[0, 1, 2], [1, 2, 3]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        for i in range(M):
            self.assertEqual(set(result[i]), set(T[i]))

    def test_edge_case_high_variance(self):
        # High variance in prepare and commit costs
        N = 3
        M = 1
        P = [10, 100, 1000]
        C = [5, 50, 500]
        Adj = [
            [0, 10, 20],
            [10, 0, 30],
            [20, 30, 0]
        ]
        T = [[0, 1, 2]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        self.assertEqual(set(result[0]), set(T[0]))

    def test_consistent_output(self):
        # Test that the function returns consistent output for the same input
        N = 3
        M = 2
        P = [10, 20, 30]
        C = [5, 15, 25]
        Adj = [[0, 10, 15], [10, 0, 5], [15, 5, 0]]
        T = [[0, 1, 2], [1, 0]]
        
        result1 = optimize_transactions(N, M, P, C, Adj, T)
        result2 = optimize_transactions(N, M, P, C, Adj, T)
        
        self.assertEqual(result1, result2)

    def test_preserves_service_sets(self):
        # Test that no services are added or removed
        N = 5
        M = 3
        P = [10, 20, 30, 40, 50]
        C = [5, 15, 25, 35, 45]
        Adj = [
            [0, 10, 0, 20, 0],
            [10, 0, 15, 0, 0],
            [0, 15, 0, 25, 30],
            [20, 0, 25, 0, 35],
            [0, 0, 30, 35, 0]
        ]
        T = [[0, 2, 4], [1, 3], [0, 1, 2, 3, 4]]
        
        result = optimize_transactions(N, M, P, C, Adj, T)
        
        for i in range(M):
            self.assertEqual(set(result[i]), set(T[i]))
            self.assertEqual(len(result[i]), len(T[i]))  # No duplicates


if __name__ == "__main__":
    unittest.main()