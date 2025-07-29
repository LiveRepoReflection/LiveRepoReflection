import unittest
import math
import sys

from network_opt import optimize_network

def is_connected(adj):
    n = len(adj)
    visited = [False] * n
    stack = [0]
    visited[0] = True
    while stack:
        node = stack.pop()
        for neighbor, bandwidth in enumerate(adj[node]):
            if bandwidth != 0 and not visited[neighbor]:
                visited[neighbor] = True
                stack.append(neighbor)
    return all(visited)

def degree_limits_satisfied(adj, max_degree):
    n = len(adj)
    for i in range(n):
        degree = sum(1 for j in range(n) if adj[i][j] != 0)
        if degree > max_degree:
            return False
    return True

def matrix_is_symmetric(adj, tol=1e-6):
    n = len(adj)
    for i in range(n):
        for j in range(n):
            if abs(adj[i][j] - adj[j][i]) > tol:
                return False
    return True

def bandwidth_in_range(adj, min_bw, max_bw):
    n = len(adj)
    for i in range(n):
        for j in range(n):
            if adj[i][j] != 0:
                if not (min_bw <= adj[i][j] <= max_bw):
                    return False
    return True

def matrix_all_zero(adj):
    n = len(adj)
    for i in range(n):
        for j in range(n):
            if adj[i][j] != 0:
                return False
    return True

class TestNetworkOpt(unittest.TestCase):
    def test_connected_graph(self):
        # A basic test where the budget is sufficient.
        n = 4
        p = [10, 20, 30, 40]
        # symmetric cost matrix. 0 for same node. costs between nodes.
        c = [
            [0,   50,  80,  90],
            [50,   0,  45,  75],
            [80,  45,   0,  60],
            [90,  75,  60,   0]
        ]
        min_bw = 5
        max_bw = 50
        B = 300
        D = 3
        data_size = 10

        adj = optimize_network(n, p, c, min_bw, max_bw, B, D, data_size)
        # Check matrix dimensions
        self.assertEqual(len(adj), n)
        for row in adj:
            self.assertEqual(len(row), n)
        # Check that the graph is connected
        self.assertTrue(is_connected(adj))
        # Check symmetry
        self.assertTrue(matrix_is_symmetric(adj))
        # Check bandwidth in allowed range for each present edge
        self.assertTrue(bandwidth_in_range(adj, min_bw, max_bw))
        # Check degree limits
        self.assertTrue(degree_limits_satisfied(adj, D))

    def test_budget_too_small(self):
        # Test when budget B is too small to allow any connection.
        n = 3
        p = [10, 10, 10]
        # Costs are high, so with a tiny budget, no edge can be established.
        c = [
            [0,  100,  100],
            [100, 0,   100],
            [100, 100,  0]
        ]
        min_bw = 1
        max_bw = 20
        B = 5  # Too small to cover any connection cost
        D = 2
        data_size = 5

        adj = optimize_network(n, p, c, min_bw, max_bw, B, D, data_size)
        # Expect an all-zero matrix (since no connected network can be built)
        self.assertTrue(matrix_all_zero(adj))

    def test_degree_constraint(self):
        # Test ensuring that no node exceeds the degree constraint.
        n = 5
        p = [15, 25, 35, 45, 55]
        c = [
            [0,   10,  20,  30,  40],
            [10,   0,  15,  25,  35],
            [20,  15,   0,  12,  22],
            [30,  25,  12,   0,  18],
            [40,  35,  22,  18,   0]
        ]
        min_bw = 10
        max_bw = 100
        B = 150
        D = 2  # restrict each node to at most 2 connections.
        data_size = 8

        adj = optimize_network(n, p, c, min_bw, max_bw, B, D, data_size)
        # Check graph connectivity if a connected graph is possible within the budget.
        self.assertTrue(is_connected(adj))
        # Check degree limits
        self.assertTrue(degree_limits_satisfied(adj, D))
        # Check symmetry
        self.assertTrue(matrix_is_symmetric(adj))

    def test_impossible_edges(self):
        # Test handling of infinite cost (impossible connections)
        n = 4
        p = [20, 30, 40, 50]
        inf = float('inf')
        c = [
            [0,   10,   inf, 40],
            [10,   0,   15,  20],
            [inf, 15,    0,  25],
            [40,   20,  25,   0]
        ]
        min_bw = 2
        max_bw = 60
        B = 100
        D = 3
        data_size = 7

        adj = optimize_network(n, p, c, min_bw, max_bw, B, D, data_size)
        # Check that the graph is connected
        self.assertTrue(is_connected(adj))
        # Edges corresponding to infinite cost in the original matrix should not be chosen.
        self.assertEqual(adj[0][2], 0)
        self.assertEqual(adj[2][0], 0)
        # Check symmetry and degree constraints.
        self.assertTrue(matrix_is_symmetric(adj))
        self.assertTrue(degree_limits_satisfied(adj, D))
        self.assertTrue(bandwidth_in_range(adj, min_bw, max_bw))

    def test_large_network(self):
        # Test a larger network within the given limits.
        n = 10
        p = [i * 10 for i in range(1, n + 1)]
        # Create a cost matrix that simulates a complete graph with increasing costs.
        c = [[0 if i == j else (abs(i - j) * 5 + 10) for j in range(n)] for i in range(n)]
        min_bw = 5
        max_bw = 100
        B = 500
        D = 4
        data_size = 10

        adj = optimize_network(n, p, c, min_bw, max_bw, B, D, data_size)
        # Check dimensions
        self.assertEqual(len(adj), n)
        for row in adj:
            self.assertEqual(len(row), n)
        # Check graph connectivity
        self.assertTrue(is_connected(adj))
        # Check degree limits
        self.assertTrue(degree_limits_satisfied(adj, D))
        # Check symmetry
        self.assertTrue(matrix_is_symmetric(adj))
        # Check bandwidth range
        self.assertTrue(bandwidth_in_range(adj, min_bw, max_bw))

if __name__ == "__main__":
    unittest.main()