import unittest
from network_partition import solve

def compute_shortest_paths(num_networks, links, latency_matrix):
    # Initialize distance matrix
    dist = [[float('inf')] * num_networks for _ in range(num_networks)]
    for i in range(num_networks):
        dist[i][i] = 0
    for u, v in links:
        # Use latency from latency_matrix provided for direct redundant link
        d = latency_matrix[u][v]
        if d < dist[u][v]:
            dist[u][v] = d
            dist[v][u] = d
    # Floyd Warshall
    for k in range(num_networks):
        for i in range(num_networks):
            for j in range(num_networks):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

class NetworkPartitionTest(unittest.TestCase):
    def check_solution(self, n, edges, k, max_redundant_links, critical_servers, latency_matrix):
        result = solve(n, edges, k, max_redundant_links, critical_servers, latency_matrix)
        # Verify result is a tuple with two elements
        self.assertIsInstance(result, tuple, "Result should be a tuple")
        self.assertEqual(len(result), 2, "Result tuple must have 2 elements")
        
        network_assignments, redundant_links = result
        
        # Check network_assignments length
        self.assertIsInstance(network_assignments, list, "network_assignments should be a list")
        self.assertEqual(len(network_assignments), n, "Length of network_assignments must equal n")
        
        # Check each assignment is an integer and within range 0 .. k-1
        for network in network_assignments:
            self.assertIsInstance(network, int, "Each network assignment must be integer")
            self.assertGreaterEqual(network, 0, "Network id must be non-negative")
            self.assertLess(network, k, "Network id must be less than k")
        
        # Critical servers must be in separate networks
        critical_networks = set()
        for server in critical_servers:
            self.assertTrue(0 <= server < n, "Critical server index out of range")
            critical_networks.add(network_assignments[server])
        self.assertEqual(len(critical_networks), len(critical_servers),
                         "Each critical server must be in a unique network")
        
        # Check redundant_links is a list
        self.assertIsInstance(redundant_links, list, "redundant_links should be a list")
        # Check count does not exceed allowed maximum
        self.assertLessEqual(len(redundant_links), max_redundant_links,
                             "Number of redundant links exceeds allowed maximum")
        
        # Check structure of each redundant link: tuple of two distinct ints within 0 and k-1
        for link in redundant_links:
            self.assertIsInstance(link, tuple, "Each redundant link should be a tuple")
            self.assertEqual(len(link), 2, "Each redundant link tuple must have two elements")
            u, v = link
            self.assertIsInstance(u, int, "Network id in redundant link must be integer")
            self.assertIsInstance(v, int, "Network id in redundant link must be integer")
            self.assertNotEqual(u, v, "Redundant link must connect two distinct networks")
            self.assertGreaterEqual(u, 0, "Network id must be non-negative")
            self.assertGreaterEqual(v, 0, "Network id must be non-negative")
            self.assertLess(u, k, "Network id in redundant link must be less than k")
            self.assertLess(v, k, "Network id in redundant link must be less than k")
        
        # Optionally compute maximum latency between critical servers using the redundant links
        # Build set of networks that are assigned to critical servers
        crit_networks = sorted(list(critical_networks))
        if crit_networks:
            dist = compute_shortest_paths(k, redundant_links, latency_matrix)
            max_latency = 0
            for i in range(len(crit_networks)):
                for j in range(i+1, len(crit_networks)):
                    u, v = crit_networks[i], crit_networks[j]
                    # if networks are disconnected, latency is infinite
                    latency = dist[u][v]
                    # For servers in the same network the latency is 0 (should never happen for criticals)
                    max_latency = max(max_latency, latency)
            # We do not assert a particular maximum latency value,
            # but if a path exists, it should be a non-negative number.
            self.assertTrue(max_latency >= 0, "Computed maximum latency should be non-negative")
    
    def test_simple_case(self):
        # Simple test with 4 servers, no edges, and 3 networks allowed.
        n = 4
        edges = []
        k = 3
        max_redundant_links = 2
        critical_servers = {0, 3}
        latency_matrix = [
            [0, 3, 7],
            [3, 0, 2],
            [7, 2, 0]
        ]
        self.check_solution(n, edges, k, max_redundant_links, critical_servers, latency_matrix)
    
    def test_linear_graph(self):
        # Test with servers in a line graph. Critical servers at the ends.
        n = 6
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        k = 3
        max_redundant_links = 1
        critical_servers = {0, 5}
        latency_matrix = [
            [0, 5, 10],
            [5, 0, 3],
            [10, 3, 0]
        ]
        self.check_solution(n, edges, k, max_redundant_links, critical_servers, latency_matrix)
    
    def test_dense_graph(self):
        # Dense graph test with more edges
        n = 8
        edges = [(i, j) for i in range(n) for j in range(i+1, n)]
        k = 4
        max_redundant_links = 3
        critical_servers = {1, 4, 7}
        latency_matrix = [
            [0, 1, 4, 7],
            [1, 0, 2, 5],
            [4, 2, 0, 3],
            [7, 5, 3, 0]
        ]
        self.check_solution(n, edges, k, max_redundant_links, critical_servers, latency_matrix)
    
    def test_no_redundant_links(self):
        # Test where no redundant links are allowed, forcing networks to be isolated.
        n = 5
        edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        k = 5
        max_redundant_links = 0
        critical_servers = {0, 4}
        latency_matrix = [
            [0, 2, 4, 6, 8],
            [2, 0, 2, 4, 6],
            [4, 2, 0, 2, 4],
            [6, 4, 2, 0, 2],
            [8, 6, 4, 2, 0]
        ]
        self.check_solution(n, edges, k, max_redundant_links, critical_servers, latency_matrix)
    
    def test_multiple_critical_servers(self):
        # Test with multiple critical servers to validate separation constraints.
        n = 10
        edges = [(i, i+1) for i in range(n-1)]
        k = 5
        max_redundant_links = 2
        critical_servers = {0, 3, 9}
        latency_matrix = [
            [0, 4, 8, 12, 16],
            [4, 0, 4, 8, 12],
            [8, 4, 0, 4, 8],
            [12, 8, 4, 0, 4],
            [16, 12, 8, 4, 0]
        ]
        self.check_solution(n, edges, k, max_redundant_links, critical_servers, latency_matrix)

if __name__ == '__main__':
    unittest.main()