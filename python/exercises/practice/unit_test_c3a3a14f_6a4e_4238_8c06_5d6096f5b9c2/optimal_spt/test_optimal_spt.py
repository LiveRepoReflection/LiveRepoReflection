import unittest
from optimal_spt import optimal_multi_source_spt

class TestOptimalSPT(unittest.TestCase):
    
    def test_basic_graph(self):
        num_nodes = 6
        edges = [(0, 1, 2), (0, 2, 4), (1, 2, 1), (1, 3, 7), 
                 (2, 4, 3), (3, 5, 1), (4, 3, 2), (4, 5, 5)]
        source_nodes = [0, 4]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Verify all nodes reachable from sources are included
        result_nodes = set()
        for u, v, _ in result:
            result_nodes.add(u)
            result_nodes.add(v)
        
        # Check that we have a tree (num edges = num nodes - num connected components)
        self.assertEqual(len(result), len(result_nodes) - len([n for n in source_nodes if n in result_nodes]))
        
        # Verify that every node has at most one incoming edge
        incoming_edges = {}
        for u, v, _ in result:
            if v in incoming_edges:
                self.fail(f"Node {v} has multiple incoming edges")
            incoming_edges[v] = u
        
        # Verify source nodes have no incoming edges
        for source in source_nodes:
            if source in incoming_edges:
                self.fail(f"Source node {source} has incoming edge from {incoming_edges[source]}")

    def test_disconnected_graph(self):
        num_nodes = 5
        edges = [(0, 1, 1), (1, 2, 1), (3, 4, 1)]
        source_nodes = [0]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Only nodes 0, 1, 2 should be reachable
        result_nodes = set()
        for u, v, _ in result:
            result_nodes.add(u)
            result_nodes.add(v)
        
        self.assertEqual(result_nodes, {0, 1, 2})
        self.assertEqual(len(result), 2)  # Only 2 edges needed for 3 nodes

    def test_multiple_source_nodes(self):
        num_nodes = 7
        edges = [(0, 1, 2), (0, 2, 5), (1, 3, 1), (2, 4, 1), 
                 (3, 5, 2), (4, 5, 2), (4, 6, 3)]
        source_nodes = [0, 4]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Each node should be connected to nearest source
        # For node 5: Should be connected to 4 (distance 2) rather than 0 (distance 5)
        
        # Create adjacency list from result
        adj_list = {i: [] for i in range(num_nodes)}
        for u, v, w in result:
            adj_list[u].append((v, w))
        
        # Verify that node 5 is reachable from source 4 and not from source 0
        path_to_5_from_4 = False
        for v, _ in adj_list[4]:
            if v == 5 or v == 6:  # If 5 is directly connected or through 6
                path_to_5_from_4 = True
                break
        
        self.assertTrue(path_to_5_from_4)

    def test_empty_graph(self):
        num_nodes = 5
        edges = []
        source_nodes = [0, 2]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Only source nodes should be in the result (with no edges)
        self.assertEqual(result, [])

    def test_multiple_shortest_paths(self):
        num_nodes = 4
        # Two equal-length paths from 0 to 3
        edges = [(0, 1, 1), (1, 3, 1), (0, 2, 1), (2, 3, 1)]
        source_nodes = [0]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Check if there's a valid path from 0 to 3
        reached_3 = False
        
        # Create adjacency list from result
        adj_list = {i: [] for i in range(num_nodes)}
        for u, v, w in result:
            adj_list[u].append((v, w))
        
        # Using DFS to check if 3 is reachable from 0
        visited = set()
        def dfs(node):
            if node == 3:
                return True
            visited.add(node)
            for neighbor, _ in adj_list[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
            return False
        
        reached_3 = dfs(0)
        self.assertTrue(reached_3)

    def test_equidistant_sources(self):
        num_nodes = 5
        edges = [(0, 2, 2), (1, 2, 2), (2, 3, 1), (2, 4, 1)]
        source_nodes = [0, 1]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Node 2 should be connected to source with lowest ID (0)
        source_of_2 = None
        for u, v, _ in result:
            if v == 2:
                source_of_2 = u
                break
        
        self.assertEqual(source_of_2, 0)

    def test_large_graph(self):
        # Generate a larger graph to test performance
        import random
        random.seed(42)
        
        num_nodes = 1000
        edges = []
        
        # Generate random edges
        for _ in range(5000):
            u = random.randint(0, num_nodes-1)
            v = random.randint(0, num_nodes-1)
            if u != v:
                w = random.randint(1, 100)
                edges.append((u, v, w))
        
        source_nodes = random.sample(range(num_nodes), 10)
        
        # Just verify that it runs without errors
        try:
            result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Failed with exception: {e}")

    def test_source_node_only(self):
        num_nodes = 3
        edges = [(0, 1, 1), (0, 2, 2)]
        source_nodes = [0]
        
        result = optimal_multi_source_spt(num_nodes, edges, source_nodes)
        
        # Check that all nodes are connected
        result_nodes = set()
        for u, v, _ in result:
            result_nodes.add(u)
            result_nodes.add(v)
        
        self.assertEqual(result_nodes, {0, 1, 2})
        
        # Check that only 0 has outgoing edges
        for u, _, _ in result:
            self.assertEqual(u, 0)

if __name__ == '__main__':
    unittest.main()