import unittest
from multi_source_tree import multi_source_tree


class MultiSourceTreeTest(unittest.TestCase):
    def test_simple_graph(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [(1, 2, 1), (1, 3, 5), (2, 3, 2), (2, 4, 2), (3, 4, 1), (3, 5, 3), (4, 5, 2), (5, 1, 1)]
        sources = [1, 2]
        
        result = multi_source_tree(nodes, edges, sources)
        
        # Check if the result is valid
        self._validate_tree(nodes, result, sources)
        
        # Check if distances are shortest
        self._check_shortest_distances(nodes, edges, result, sources)
        
        # We expect the minimum-weight tree to have specific edges
        # Different solutions could be valid, so check weight rather than exact edges
        total_weight = sum(edge[2] for edge in result)
        self.assertEqual(total_weight, 7)  # Weight of optimal tree for this example

    def test_disconnected_graph(self):
        nodes = [1, 2, 3, 4, 5, 6]
        edges = [(1, 2, 1), (2, 3, 2), (4, 5, 3), (5, 6, 1)]
        sources = [1, 4]
        
        result = multi_source_tree(nodes, edges, sources)
        
        self._validate_tree(nodes, result, sources)
        self._check_shortest_distances(nodes, edges, result, sources)
        
        # Two disconnected components, each with its own source
        total_weight = sum(edge[2] for edge in result)
        self.assertEqual(total_weight, 7)  # 1+2 for component 1, 3+1 for component 2

    def test_single_source(self):
        nodes = [1, 2, 3, 4]
        edges = [(1, 2, 1), (2, 3, 2), (1, 4, 10), (3, 4, 3)]
        sources = [1]
        
        result = multi_source_tree(nodes, edges, sources)
        
        self._validate_tree(nodes, result, sources)
        self._check_shortest_distances(nodes, edges, result, sources)
        
        # Classic single-source shortest path tree
        total_weight = sum(edge[2] for edge in result)
        self.assertEqual(total_weight, 6)  # 1+2+3 = 6

    def test_multiple_sources(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [(1, 2, 10), (2, 3, 1), (3, 4, 1), (5, 4, 1), (5, 1, 5)]
        sources = [1, 5]
        
        result = multi_source_tree(nodes, edges, sources)
        
        self._validate_tree(nodes, result, sources)
        self._check_shortest_distances(nodes, edges, result, sources)
        
        # Each source should connect to nearest nodes
        total_weight = sum(edge[2] for edge in result)
        self.assertLessEqual(total_weight, 13)  # Upper bound

    def test_complex_graph(self):
        nodes = list(range(1, 11))
        edges = [(1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4), 
                 (6, 7, 5), (7, 8, 6), (8, 9, 7), (9, 10, 8),
                 (1, 6, 10), (3, 8, 12), (5, 10, 15)]
        sources = [1, 6]
        
        result = multi_source_tree(nodes, edges, sources)
        
        self._validate_tree(nodes, result, sources)
        self._check_shortest_distances(nodes, edges, result, sources)

    def test_cyclic_graph(self):
        nodes = [1, 2, 3, 4, 5]
        edges = [(1, 2, 1), (2, 3, 2), (3, 1, 4), (3, 4, 1), (4, 5, 2), (5, 3, 3)]
        sources = [1]
        
        result = multi_source_tree(nodes, edges, sources)
        
        self._validate_tree(nodes, result, sources)
        self._check_shortest_distances(nodes, edges, result, sources)
        
        # Check that the tree doesn't contain cycles
        self._check_no_cycles(result)

    def test_large_graph(self):
        # Create a larger graph to test efficiency
        nodes = list(range(1, 101))
        edges = []
        
        # Create a dense graph
        for i in range(1, 100):
            for j in range(i+1, min(i+6, 101)):
                edges.append((i, j, j-i))
        
        sources = [1, 50, 100]
        
        result = multi_source_tree(nodes, edges, sources)
        
        # Just basic validation for large graph
        for edge in result:
            self.assertIn(edge[0], nodes)
            self.assertIn(edge[1], nodes)
            self.assertTrue(edge[2] > 0)

    def test_edge_case_empty_edges(self):
        nodes = [1, 2, 3]
        edges = []
        sources = [1]
        
        result = multi_source_tree(nodes, edges, sources)
        
        # Should return empty tree as no nodes are reachable from source
        self.assertEqual(result, [])

    def test_edge_case_all_nodes_as_sources(self):
        nodes = [1, 2, 3]
        edges = [(1, 2, 1), (2, 3, 2)]
        sources = [1, 2, 3]
        
        result = multi_source_tree(nodes, edges, sources)
        
        # Since all nodes are sources, no edges are needed
        self.assertEqual(result, [])

    def _validate_tree(self, nodes, result, sources):
        """Validate that the result forms a valid tree with reachability properties."""
        # Check that all edges in result are in the original graph
        for edge in result:
            self.assertIn(edge[0], nodes)
            self.assertIn(edge[1], nodes)
            self.assertTrue(edge[2] > 0)
        
        # Check that the result doesn't contain duplicate edges
        edge_tuples = [(edge[0], edge[1]) for edge in result]
        self.assertEqual(len(edge_tuples), len(set(edge_tuples)))
        
        # Check if the result is a tree (no cycles)
        self._check_no_cycles(result)
        
        # Check reachability (if not empty)
        if result:
            reachable_nodes = self._get_reachable_nodes(nodes, result, sources)
            source_set = set(sources)
            for node in nodes:
                if node in reachable_nodes and node not in source_set:
                    # At least one path should exist from some source to this node
                    path_exists = False
                    for source in sources:
                        if self._path_exists(result, source, node):
                            path_exists = True
                            break
                    self.assertTrue(path_exists, f"Node {node} should be reachable from sources")

    def _check_no_cycles(self, edges):
        """Check that the undirected version of the graph contains no cycles."""
        if not edges:
            return
        
        # Build an undirected adjacency list
        adjacency_list = {}
        for u, v, _ in edges:
            if u not in adjacency_list:
                adjacency_list[u] = []
            if v not in adjacency_list:
                adjacency_list[v] = []
            adjacency_list[u].append(v)
            adjacency_list[v].append(u)  # Undirected
        
        # DFS to find cycles
        visited = set()
        
        def has_cycle(node, parent):
            visited.add(node)
            if node in adjacency_list:
                for neighbor in adjacency_list[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor, node):
                            return True
                    elif neighbor != parent:
                        return True
            return False
        
        # Check each connected component
        all_nodes = set()
        for u, v, _ in edges:
            all_nodes.add(u)
            all_nodes.add(v)
        
        for node in all_nodes:
            if node not in visited and node in adjacency_list:
                if has_cycle(node, None):
                    self.fail("Tree contains a cycle")

    def _check_shortest_distances(self, nodes, original_edges, tree_edges, sources):
        """Check that the distances in the tree match shortest distances in original graph."""
        # Build adjacency lists for both graphs
        original_adj = {}
        for u, v, w in original_edges:
            if u not in original_adj:
                original_adj[u] = []
            original_adj[u].append((v, w))
        
        tree_adj = {}
        for u, v, w in tree_edges:
            if u not in tree_adj:
                tree_adj[u] = []
            tree_adj[u].append((v, w))
        
        # Calculate distances in original graph using Dijkstra from each source
        original_distances = {node: float('inf') for node in nodes}
        for source in sources:
            original_distances[source] = 0
            # Run simple Dijkstra for testing
            self._dijkstra(original_adj, original_distances, source)
        
        # Calculate distances in tree graph using BFS (since it's a tree)
        tree_distances = {node: float('inf') for node in nodes}
        for source in sources:
            tree_distances[source] = 0
            if source in tree_adj:
                self._dijkstra(tree_adj, tree_distances, source)
        
        # Check that distances match for all reachable nodes
        for node in nodes:
            if original_distances[node] < float('inf'):
                self.assertEqual(tree_distances[node], original_distances[node], 
                                f"Distance to node {node} in tree doesn't match shortest distance")

    def _dijkstra(self, adj_list, distances, start):
        """Simple Dijkstra implementation for testing."""
        import heapq
        
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist, node = heapq.heappop(pq)
            if node in visited:
                continue
                
            visited.add(node)
            
            if node not in adj_list:
                continue
                
            for neighbor, weight in adj_list[node]:
                if neighbor not in visited:
                    new_dist = dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

    def _get_reachable_nodes(self, nodes, edges, sources):
        """Get all nodes reachable from sources in the tree."""
        adj_list = {}
        for u, v, _ in edges:
            if u not in adj_list:
                adj_list[u] = []
            adj_list[u].append(v)
        
        reachable = set(sources)
        queue = list(sources)
        
        while queue:
            node = queue.pop(0)
            if node in adj_list:
                for neighbor in adj_list[node]:
                    if neighbor not in reachable:
                        reachable.add(neighbor)
                        queue.append(neighbor)
        
        return reachable

    def _path_exists(self, edges, source, target):
        """Check if a path exists from source to target in the tree."""
        adj_list = {}
        for u, v, _ in edges:
            if u not in adj_list:
                adj_list[u] = []
            adj_list[u].append(v)
        
        visited = set()
        queue = [source]
        
        while queue:
            node = queue.pop(0)
            if node == target:
                return True
            
            visited.add(node)
            if node in adj_list:
                for neighbor in adj_list[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return False


if __name__ == "__main__":
    unittest.main()