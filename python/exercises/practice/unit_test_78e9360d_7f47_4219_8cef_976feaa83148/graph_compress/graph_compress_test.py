import unittest
import heapq

from graph_compress import compress_graph

def dijkstra(edges, source, target):
    # Build adjacency list
    graph = {}
    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append((v, w))
    dist = {}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        if u == target:
            return d
        for v, w in graph.get(u, []):
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return None

def compute_all_pairs_shortest(edges, nodes):
    # Compute all pairs shortest distances for given list of nodes.
    distances = {}
    for u in nodes:
        distances[u] = {}
        for v in nodes:
            if u == v:
                distances[u][v] = 0
            else:
                distances[u][v] = dijkstra(edges, u, v)
    return distances

class GraphCompressTest(unittest.TestCase):
    def assertDistancesEqual(self, original_edges, compressed_edges, important_nodes):
        orig_dist = compute_all_pairs_shortest(original_edges, important_nodes)
        comp_dist = compute_all_pairs_shortest(compressed_edges, important_nodes)
        for u in important_nodes:
            for v in important_nodes:
                self.assertEqual(orig_dist[u][v], comp_dist[u][v], 
                                 f"Distance from {u} to {v} differs between original and compressed graphs.")

    def test_simple_chain(self):
        # Graph: 0 -> 1 -> 2 -> 3
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1)
        ]
        important_nodes = {0, 3}
        compressed = compress_graph(edges, important_nodes)
        # Check that the distances are preserved
        self.assertDistancesEqual(edges, compressed, important_nodes)
        # Ensure all important nodes are present
        nodes_in_compressed = {u for u, _, _ in compressed} | {v for _, v, _ in compressed}
        for node in important_nodes:
            self.assertIn(node, nodes_in_compressed)

    def test_extra_nodes_removal(self):
        # Graph with extra nodes that are not important and should get removed if possible.
        # Graph:
        # 0 -> 1 -> 2 -> 3
        # Additional edge: 0 -> 3 with weight 3 (but still longer than path through chain)
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1),
            (0, 3, 3),
            (1, 3, 3)
        ]
        important_nodes = {0, 3}
        compressed = compress_graph(edges, important_nodes)
        self.assertDistancesEqual(edges, compressed, important_nodes)
        nodes_in_compressed = {u for u, _, _ in compressed} | {v for _, v, _ in compressed}
        for node in important_nodes:
            self.assertIn(node, nodes_in_compressed)

    def test_disconnected_graph(self):
        # Graph has two disconnected clusters. For important nodes in different clusters, no path should exist.
        edges = [
            (0, 1, 2),
            (1, 0, 2),
            (2, 3, 3),
            (3, 2, 3)
        ]
        important_nodes = {0, 3}
        compressed = compress_graph(edges, important_nodes)
        self.assertDistancesEqual(edges, compressed, important_nodes)

    def test_self_loops(self):
        # Graph with self loops: the self loop should not affect the shortest path between different nodes.
        edges = [
            (0, 0, 10),
            (0, 1, 5),
            (1, 1, 2),
            (1, 2, 5),
            (2, 2, 1),
            (2, 0, 7)
        ]
        important_nodes = {0, 2}
        compressed = compress_graph(edges, important_nodes)
        self.assertDistancesEqual(edges, compressed, important_nodes)

    def test_zero_weight_cycle(self):
        # Graph with a cycle with zero weight.
        # 0 -> 1 (weight 1), 1 -> 2 (weight 0), 2 -> 0 (weight 0), and extra edge 1 -> 3 (weight 2)
        edges = [
            (0, 1, 1),
            (1, 2, 0),
            (2, 0, 0),
            (1, 3, 2),
            (3, 1, 2)
        ]
        important_nodes = {0, 3}
        compressed = compress_graph(edges, important_nodes)
        self.assertDistancesEqual(edges, compressed, important_nodes)

    def test_multiple_important_nodes(self):
        # More complex graph with several important nodes.
        edges = [
            (0, 1, 2),
            (1, 2, 2),
            (0, 3, 4),
            (3, 2, 1),
            (2, 4, 3),
            (3, 4, 5),
            (1, 4, 10),
            (4, 5, 1),
            (2, 5, 4),
            (5, 6, 2),
            (4, 6, 2)
        ]
        important_nodes = {0, 2, 4, 6}
        compressed = compress_graph(edges, important_nodes)
        self.assertDistancesEqual(edges, compressed, important_nodes)
        nodes_in_compressed = {u for u, _, _ in compressed} | {v for _, v, _ in compressed}
        for node in important_nodes:
            self.assertIn(node, nodes_in_compressed)

if __name__ == '__main__':
    unittest.main()