import unittest
from packet_router import optimize_routing

class PacketRouterTest(unittest.TestCase):
    def test_simple_path(self):
        """Test a simple path with one possible route."""
        N = 3
        edges = [(0, 1, 10, 5), (1, 2, 10, 5)]
        S = 0
        D = 2
        packets = [1, 2]
        
        expected_paths = [[0, 1, 2], [0, 1, 2]]
        actual_paths = optimize_routing(N, edges, S, D, packets)
        
        self._assert_valid_paths(actual_paths, expected_paths, S, D, packets, edges)

    def test_multiple_paths(self):
        """Test with multiple possible paths between source and destination."""
        N = 4
        edges = [
            (0, 1, 10, 2), 
            (0, 2, 20, 3),
            (1, 3, 10, 2),
            (2, 3, 15, 3)
        ]
        S = 0
        D = 3
        packets = [1, 2, 1]
        
        # Expected: packets distributed to minimize maximum latency
        # Shortest path (0->1->3) has latency 20, but capacity 2
        # Longer path (0->2->3) has latency 35, but capacity 3
        # Optimal solution: route packet 1 & 3 via shorter path, packet 2 via longer path
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        
        # We can't predict exact paths due to multiple valid solutions,
        # so we'll validate the solution meets constraints
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def test_insufficient_capacity(self):
        """Test when there's not enough capacity to route all packets."""
        N = 3
        edges = [(0, 1, 10, 2), (1, 2, 10, 1)]
        S = 0
        D = 2
        packets = [1, 1, 1]  # Total of 3 packets, but bottleneck capacity is 1
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self.assertEqual([], actual_paths, "Should return empty list when routing impossible")

    def test_no_path(self):
        """Test when there's no path from source to destination."""
        N = 3
        edges = [(0, 1, 10, 5)]  # No path to node 2
        S = 0
        D = 2
        packets = [1]
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self.assertEqual([], actual_paths, "Should return empty list when no path exists")

    def test_complex_network(self):
        """Test with a more complex network topology."""
        N = 6
        edges = [
            (0, 1, 10, 5), (0, 2, 15, 7), 
            (1, 3, 20, 4), (1, 4, 30, 3),
            (2, 3, 10, 2), (2, 4, 15, 6),
            (3, 5, 10, 3), (4, 5, 5, 5)
        ]
        S = 0
        D = 5
        packets = [2, 3, 2, 1, 1]
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def test_cyclic_graph(self):
        """Test with a graph containing cycles."""
        N = 4
        edges = [
            (0, 1, 10, 5), (1, 2, 15, 5), 
            (2, 0, 20, 5), (1, 3, 30, 5),
            (2, 3, 10, 5)
        ]
        S = 0
        D = 3
        packets = [1, 2, 1]
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def test_large_network(self):
        """Test with a larger network to check efficiency."""
        N = 15
        edges = []
        # Create a mesh network where each node i connects to nodes i+1 through i+5 (wrapping around)
        for i in range(N):
            for j in range(1, 6):
                dest = (i + j) % N
                edges.append((i, dest, (i*j) % 20 + 1, (i+j) % 10 + 1))
        
        S = 0
        D = N // 2
        packets = [1] * 10  # 10 unit-sized packets
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def test_edge_case_single_node(self):
        """Test with a single node (source = destination)."""
        N = 1
        edges = []
        S = 0
        D = 0
        packets = [1, 2]
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        expected_paths = [[0], [0]]  # Each packet stays at node 0
        self._assert_valid_paths(actual_paths, expected_paths, S, D, packets, edges)

    def test_bottleneck_identification(self):
        """Test if algorithm correctly identifies and handles bottlenecks."""
        N = 5
        edges = [
            (0, 1, 10, 5), (0, 2, 15, 5),
            (1, 3, 10, 2), (2, 3, 20, 5),  # Bottleneck at (1, 3)
            (3, 4, 10, 10)
        ]
        S = 0
        D = 4
        packets = [1, 1, 2]  # Total of 4 packets, bottleneck capacity is 2
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def test_identical_latency_paths(self):
        """Test with multiple paths having identical total latency."""
        N = 4
        edges = [
            (0, 1, 10, 2), (0, 2, 10, 2),
            (1, 3, 10, 2), (2, 3, 10, 2)
        ]
        S = 0
        D = 3
        packets = [1, 1, 1, 1]
        
        actual_paths = optimize_routing(N, edges, S, D, packets)
        self._assert_valid_solution(actual_paths, N, edges, S, D, packets)

    def _assert_valid_paths(self, actual_paths, expected_paths, S, D, packets, edges):
        """Validate that all paths are valid and meet expectations."""
        self.assertEqual(len(actual_paths), len(expected_paths), 
                        f"Expected {len(expected_paths)} paths, got {len(actual_paths)}")
        
        for i, path in enumerate(actual_paths):
            self.assertEqual(path, expected_paths[i], 
                            f"Path {i} differs: expected {expected_paths[i]}, got {path}")
            self._validate_single_path(path, S, D)

    def _validate_single_path(self, path, S, D):
        """Validate a single path from S to D."""
        self.assertGreaterEqual(len(path), 1, "Path must contain at least one node")
        self.assertEqual(path[0], S, f"Path must start at source node {S}")
        self.assertEqual(path[-1], D, f"Path must end at destination node {D}")
        
        # Check consecutive nodes
        for i in range(len(path) - 1):
            self.assertNotEqual(path[i], path[i+1], "Adjacent nodes in path must be different")

    def _assert_valid_solution(self, paths, N, edges, S, D, packets):
        """Validate that the solution meets all constraints."""
        if not paths:
            # If empty solution, verify that routing is indeed impossible
            self._verify_no_solution_possible(N, edges, S, D, packets)
            return
        
        # Check number of paths matches number of packets
        self.assertEqual(len(paths), len(packets), 
                        f"Number of paths ({len(paths)}) must match number of packets ({len(packets)})")
        
        # Create an adjacency list and capacity/latency maps for easier lookup
        adj_list = [[] for _ in range(N)]
        capacities = {}
        latencies = {}
        
        for u, v, lat, cap in edges:
            adj_list[u].append(v)
            capacities[(u, v)] = cap
            latencies[(u, v)] = lat
        
        # Check each path
        for i, path in enumerate(paths):
            self._validate_single_path(path, S, D)
            
            # Check each edge in the path exists
            for j in range(len(path) - 1):
                u, v = path[j], path[j+1]
                self.assertIn(v, adj_list[u], f"Edge ({u}, {v}) does not exist in the network")
        
        # Check capacity constraints
        link_usage = {}
        for i, path in enumerate(paths):
            packet_size = packets[i]
            for j in range(len(path) - 1):
                u, v = path[j], path[j+1]
                link_usage[(u, v)] = link_usage.get((u, v), 0) + packet_size
        
        for (u, v), usage in link_usage.items():
            self.assertLessEqual(usage, capacities[(u, v)], 
                               f"Capacity constraint violated for edge ({u}, {v}): usage {usage}, capacity {capacities[(u, v)]}")

    def _verify_no_solution_possible(self, N, edges, S, D, packets):
        """Verify that no valid routing solution is possible."""
        # This is complex to verify completely, but we can check basic conditions
        
        # Create an adjacency list to check if D is reachable from S
        adj_list = [[] for _ in range(N)]
        for u, v, _, _ in edges:
            adj_list[u].append(v)
        
        # Check if D is reachable from S using BFS
        visited = [False] * N
        queue = [S]
        visited[S] = True
        
        while queue:
            node = queue.pop(0)
            if node == D:
                # D is reachable, so the issue might be insufficient capacity
                # This is a simplified check and doesn't guarantee no solution exists
                return
            
            for neighbor in adj_list[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        # If we get here, D is definitely not reachable from S
        self.assertFalse(visited[D], "Destination is not reachable from source, so empty result is correct")

if __name__ == '__main__':
    unittest.main()