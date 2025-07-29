import unittest
from collections import deque
from router_placement import optimize_router_placement

def build_graph(N, edges):
    graph = {i: set() for i in range(N)}
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)
    return graph

def is_covered(N, graph, placements, R):
    # For each router placement, do a BFS up to depth R and mark nodes as covered.
    covered = set()
    for start in placements:
        visited = set([start])
        queue = deque([(start, 0)])
        while queue:
            node, dist = queue.popleft()
            if dist > R:
                continue
            covered.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
    return len(covered) == N

class RouterPlacementTest(unittest.TestCase):
    def test_single_node_with_critical(self):
        N = 1
        edges = []
        R = 1
        C = 0
        K = 1
        critical_buildings = [0]
        result = optimize_router_placement(N, edges, R, C, K, critical_buildings)
        # Expect one router placed in node 0.
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        min_routers, placements, served_users = result
        self.assertEqual(min_routers, 1)
        self.assertEqual(placements, [0])
        self.assertTrue(isinstance(served_users, int))
        self.assertTrue(0 <= served_users <= C * K)
    
    def test_chain_graph_no_critical(self):
        # Create a chain: 0-1-2-3-4
        N = 5
        edges = [(0,1), (1,2), (2,3), (3,4)]
        R = 1
        C = 1
        K = 2
        critical_buildings = []
        result = optimize_router_placement(N, edges, R, C, K, critical_buildings)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        min_routers, placements, served_users = result
        # The number of routers should be equal to the number placed
        self.assertEqual(min_routers, len(placements))
        # All placements must be valid nodes.
        for node in placements:
            self.assertTrue(0 <= node < N)
        graph = build_graph(N, edges)
        self.assertTrue(is_covered(N, graph, placements, R))
        self.assertTrue(isinstance(served_users, int))
        self.assertTrue(0 <= served_users <= C * K)
        
    def test_with_critical_and_sample(self):
        # Sample example from the description
        N = 7
        edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 5), (4, 5), (4, 6), (5, 6)]
        R = 1
        C = 2
        K = 3
        critical_buildings = [0, 6]
        result = optimize_router_placement(N, edges, R, C, K, critical_buildings)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        min_routers, placements, served_users = result
        # Check that critical buildings are included
        for cb in critical_buildings:
            self.assertIn(cb, placements)
        self.assertEqual(min_routers, len(placements))
        # Check that placements are valid node indices.
        for node in placements:
            self.assertTrue(0 <= node < N)
        graph = build_graph(N, edges)
        self.assertTrue(is_covered(N, graph, placements, R))
        self.assertTrue(isinstance(served_users, int))
        self.assertTrue(0 <= served_users <= C * K)
        
    def test_dense_graph(self):
        # Create a complete graph with 4 nodes
        N = 4
        edges = [(i, j) for i in range(N) for j in range(i+1, N)]
        R = 1
        C = 2
        K = 2
        critical_buildings = [1]
        result = optimize_router_placement(N, edges, R, C, K, critical_buildings)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        min_routers, placements, served_users = result
        # Critical building check
        for cb in critical_buildings:
            self.assertIn(cb, placements)
        self.assertEqual(min_routers, len(placements))
        # Check valid nodes
        for node in placements:
            self.assertTrue(0 <= node < N)
        graph = build_graph(N, edges)
        self.assertTrue(is_covered(N, graph, placements, R))
        self.assertTrue(isinstance(served_users, int))
        self.assertTrue(0 <= served_users <= C * K)
        
    def test_complex_graph(self):
        # Create a more complex graph combining several components.
        N = 10
        edges = [(0,1), (0,2), (1,3), (2,3), (3,4), (4,5), (5,6), (5,7), (6,7), (7,8), (8,9), (1,9), (2,8)]
        R = 2
        C = 3
        K = 2
        critical_buildings = [0, 9]
        result = optimize_router_placement(N, edges, R, C, K, critical_buildings)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        min_routers, placements, served_users = result
        # Critical buildings must be included.
        for cb in critical_buildings:
            self.assertIn(cb, placements)
        self.assertEqual(min_routers, len(placements))
        # Validate placements.
        for node in placements:
            self.assertTrue(0 <= node < N)
        graph = build_graph(N, edges)
        self.assertTrue(is_covered(N, graph, placements, R))
        self.assertTrue(isinstance(served_users, int))
        self.assertTrue(0 <= served_users <= C * K)

if __name__ == '__main__':
    unittest.main()