import unittest
from network_zones import partition_network

class TestNetworkZones(unittest.TestCase):
    def test_basic_two_zones(self):
        graph = [[1, 2], [0, 2, 3], [0, 1, 4], [1, 4], [2, 3]]
        resilience = [5, 3, 8, 2, 7]
        K = 2
        latencies = {
            (0, 1): 10, (1, 0): 10,
            (0, 2): 5,  (2, 0): 5,
            (1, 2): 2,  (2, 1): 2,
            (1, 3): 7,  (3, 1): 7,
            (2, 4): 1,  (4, 2): 1,
            (3, 4): 3,  (4, 3): 3
        }
        result = partition_network(graph, resilience, K, latencies)
        
        # Check basic constraints
        self.assertEqual(len(result), len(graph))
        self.assertTrue(all(0 <= zone < K for zone in result))
        
        # Check connectivity within zones
        zones = [[] for _ in range(K)]
        for node, zone in enumerate(result):
            zones[zone].append(node)
            
        for zone_nodes in zones:
            self.assertTrue(self.is_connected_subgraph(graph, zone_nodes))

    def test_single_zone(self):
        graph = [[1], [0, 2], [1]]
        resilience = [1, 2, 3]
        K = 1
        latencies = {(0, 1): 1, (1, 0): 1, (1, 2): 1, (2, 1): 1}
        result = partition_network(graph, resilience, K, latencies)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(len(set(result)), 1)  # All nodes should be in the same zone

    def test_max_zones(self):
        graph = [[1], [0, 2], [1]]
        resilience = [1, 2, 3]
        K = 3
        latencies = {(0, 1): 1, (1, 0): 1, (1, 2): 1, (2, 1): 1}
        result = partition_network(graph, resilience, K, latencies)
        
        self.assertEqual(len(result), 3)
        self.assertTrue(all(0 <= zone < K for zone in result))

    def test_line_graph(self):
        graph = [[1], [0, 2], [1, 3], [2]]
        resilience = [5, 2, 3, 4]
        K = 2
        latencies = {
            (0, 1): 1, (1, 0): 1,
            (1, 2): 1, (2, 1): 1,
            (2, 3): 1, (3, 2): 1
        }
        result = partition_network(graph, resilience, K, latencies)
        
        self.assertEqual(len(result), 4)
        self.assertTrue(all(0 <= zone < K for zone in result))

    def test_star_graph(self):
        graph = [[1, 2, 3, 4], [0], [0], [0], [0]]
        resilience = [10, 5, 6, 7, 8]
        K = 3
        latencies = {
            (0, 1): 1, (1, 0): 1,
            (0, 2): 1, (2, 0): 1,
            (0, 3): 1, (3, 0): 1,
            (0, 4): 1, (4, 0): 1
        }
        result = partition_network(graph, resilience, K, latencies)
        
        self.assertEqual(len(result), 5)
        self.assertTrue(all(0 <= zone < K for zone in result))

    def test_complete_graph(self):
        graph = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        resilience = [5, 5, 5, 5]
        K = 2
        latencies = {
            (i, j): 1 for i in range(4) for j in range(4)
            if i != j
        }
        result = partition_network(graph, resilience, K, latencies)
        
        self.assertEqual(len(result), 4)
        self.assertTrue(all(0 <= zone < K for zone in result))

    def test_invalid_inputs(self):
        # Test empty graph
        with self.assertRaises(ValueError):
            partition_network([], [], 1, {})

        # Test K > N
        with self.assertRaises(ValueError):
            partition_network([[1], [0]], [1, 2], 3, {(0, 1): 1, (1, 0): 1})

        # Test negative resilience
        with self.assertRaises(ValueError):
            partition_network([[1], [0]], [-1, 2], 2, {(0, 1): 1, (1, 0): 1})

        # Test negative latency
        with self.assertRaises(ValueError):
            partition_network([[1], [0]], [1, 2], 2, {(0, 1): -1, (1, 0): -1})

    def is_connected_subgraph(self, graph, nodes):
        if not nodes:
            return True
        
        # Run BFS from first node
        visited = set()
        queue = [nodes[0]]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in graph[current]:
                if neighbor in nodes and neighbor not in visited:
                    queue.append(neighbor)
        
        # Check if all nodes in the zone are reachable
        return all(node in visited for node in nodes)

if __name__ == '__main__':
    unittest.main()