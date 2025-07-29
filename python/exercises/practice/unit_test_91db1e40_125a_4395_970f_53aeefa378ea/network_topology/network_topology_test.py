import unittest
from collections import defaultdict, deque

from network_topology import optimal_network_topology

def is_connected(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    # Start BFS/DFS from node 0
    queue = deque([0])
    visited.add(0)
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited) == n

def degrees(n, edges):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return deg

class TestNetworkTopology(unittest.TestCase):
    def test_valid_topology_basic(self):
        # Test a basic valid configuration
        n = 5
        m = 7
        k = [4, 4, 4, 4, 4]
        
        edges = optimal_network_topology(n, m, k)
        
        # Check that the number of edges is less than or equal to m and at least n-1 for connectivity.
        self.assertTrue(n - 1 <= len(edges) <= m, "Edge count is not within allowed limits.")
        
        # Check connectivity
        self.assertTrue(is_connected(n, edges), "Graph is not fully connected.")
        
        # Check node degree limits according to k
        node_degrees = degrees(n, edges)
        for i in range(n):
            self.assertTrue(node_degrees[i] <= k[i], f"Node {i} exceeds its capacity.")
        
        # Check lexicographic order of edges
        sorted_edges = sorted(edges)
        self.assertEqual(edges, sorted_edges, "Edges are not sorted lexicographically.")
        
        # Check that there are no duplicate edges and no self-loops
        seen = set()
        for u, v in edges:
            self.assertNotEqual(u, v, "Self loop detected.")
            self.assertTrue((u, v) not in seen, "Duplicate edge detected.")
            seen.add((u, v))
    
    def test_valid_topology_dense(self):
        # Test with a denser connectivity requirement.
        n = 8
        m = 15
        k = [3, 4, 3, 4, 3, 4, 3, 4]
        
        edges = optimal_network_topology(n, m, k)
        
        # Should form a connected graph
        self.assertTrue(is_connected(n, edges), "Graph is not fully connected.")
        
        # Check edge count between n-1 and m.
        self.assertTrue(n - 1 <= len(edges) <= m, "Edge count is not within allowed limits.")
        
        # Degree constraints
        node_degrees = degrees(n, edges)
        for i in range(n):
            self.assertTrue(node_degrees[i] <= k[i], f"Node {i} exceeds its capacity.")

        # Lexicographic order check
        self.assertEqual(edges, sorted(edges), "Edges are not sorted lexicographically.")

    def test_invalid_topology_due_to_node_capacity(self):
        # Test a configuration that cannot be satisfied because node capacities are too low.
        n = 4
        m = 6
        # For a connected graph, at least one node must have capacity >= 3 (for a star configuration).
        k = [1, 1, 1, 1]
        
        edges = optimal_network_topology(n, m, k)
        
        # Since it's impossible to build a connected graph, the function should return an empty list.
        self.assertEqual(edges, [], "Expected an empty list for unsatisfiable node capacities.")

    def test_minimum_edges(self):
        # Test a configuration which returns exactly n-1 edges.
        n = 6
        m = 5  # Minimum number of edges required to connect 6 nodes is 5.
        k = [2, 2, 2, 2, 2, 2]
        
        edges = optimal_network_topology(n, m, k)
        self.assertEqual(len(edges), n - 1, "Expected exactly n-1 edges for a minimal spanning tree topology.")
        self.assertTrue(is_connected(n, edges), "Graph is not fully connected in minimal topology.")
        
    def test_exceeding_m_constraint(self):
        # Test where m is larger than necessary, the solution should not use more than m edges.
        n = 7
        m = 12
        k = [5, 5, 5, 5, 5, 5, 5]
        
        edges = optimal_network_topology(n, m, k)
        self.assertTrue(len(edges) <= m, "Number of edges exceeds m.")
        self.assertTrue(is_connected(n, edges), "Graph is not fully connected.")
        
    def test_sorted_edges_output(self):
        # Test that the output edges are in lexicographically sorted order.
        n = 6
        m = 10
        k = [3, 3, 3, 3, 3, 3]
        
        edges = optimal_network_topology(n, m, k)
        self.assertEqual(edges, sorted(edges), "Edges are not sorted in lexicographical order.")

if __name__ == '__main__':
    unittest.main()