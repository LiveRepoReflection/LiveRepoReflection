import unittest
import heapq

from shortest_path_tree import shortest_path_tree

def multi_source_dijkstra(n, edges, sources):
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))
    dist = [float('inf')] * n
    parent = [None] * n  # store (parent, weight) that gives the optimal distance
    pq = []
    for s in sources:
        dist[s] = 0
        heapq.heappush(pq, (0, s))
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                parent[v] = (u, w)
                heapq.heappush(pq, (dist[v], v))
    return dist, parent 

def build_tree_dict(tree_edges):
    # Return a mapping of child -> (parent, weight)
    tree = {}
    for u, v, w in tree_edges:
        tree[v] = (u, w)
    return tree

def compute_tree_distance(v, tree_dict, sources):
    # Compute the distance from a source to node v by walking up the tree_dict.
    distance = 0
    source_set = set(sources)
    current = v
    while current not in source_set:
        if current not in tree_dict:
            return None
        parent, weight = tree_dict[current]
        distance += weight
        current = parent
    return distance

class TestShortestPathTree(unittest.TestCase):
    def validate_tree(self, n, edges, sources, tree_edges):
        # Validate that the tree_edges forms a valid forest (possibly multiple trees),
        # which covers all nodes reachable from any of the source nodes in the original graph.
        graph_dict = {}
        for u, v, w in edges:
            # If there are multiple edges between u and v, only consider the smallest weight.
            if (u, v) not in graph_dict or w < graph_dict[(u, v)]:
                graph_dict[(u, v)] = w

        expected_dist, _ = multi_source_dijkstra(n, edges, sources)
        tree_dict = build_tree_dict(tree_edges)

        # Check that sources do not appear as keys in tree_dict (no incoming edge for sources)
        for s in sources:
            self.assertNotIn(s, tree_dict, f"Source node {s} should not have an incoming edge.")

        # Check every edge in the tree exists in the original graph.
        for u, v, w in tree_edges:
            self.assertIn((u, v), graph_dict, f"Edge ({u}, {v}) not present in the original graph.")
            self.assertEqual(w, graph_dict[(u, v)], f"Edge weight mismatch for edge ({u}, {v}).")

        # Validate distances for every reachable node
        for v in range(n):
            if expected_dist[v] < float('inf'):
                if v in sources:
                    continue
                self.assertIn(v, tree_dict, f"Reachable node {v} missing in the tree.")
                calc_dist = compute_tree_distance(v, tree_dict, sources)
                self.assertIsNotNone(calc_dist, f"Could not compute distance for node {v}.")
                self.assertEqual(calc_dist, expected_dist[v],
                                 f"Distance for node {v} incorrect: expected {expected_dist[v]}, got {calc_dist}.")
            else:
                # Node should not appear in the tree if unreachable.
                self.assertNotIn(v, tree_dict, f"Unreachable node {v} should not be in the tree.")

    def test_trivial(self):
        n = 1
        edges = []
        sources = [0]
        tree_edges = shortest_path_tree(n, edges, sources)
        # For a trivial graph, the tree should be empty.
        self.assertEqual(tree_edges, [])

    def test_example(self):
        n = 5
        edges = [
            (0, 1, 2),
            (0, 2, 4),
            (1, 2, 1),
            (1, 3, 5),
            (2, 3, 2),
            (4, 0, 3)
        ]
        sources = [0, 4]
        tree_edges = shortest_path_tree(n, edges, sources)
        self.validate_tree(n, edges, sources, tree_edges)

    def test_cycle_and_multiple_sources(self):
        n = 6
        edges = [
            (0, 1, 2), (1, 2, 2), (2, 0, 2),  # a cycle among 0, 1, 2
            (1, 3, 3), (2, 3, 1),
            (3, 4, 4), (4, 5, 1),
            (2, 5, 10),
            (0, 5, 15)
        ]
        sources = [0, 2]
        tree_edges = shortest_path_tree(n, edges, sources)
        self.validate_tree(n, edges, sources, tree_edges)

    def test_disconnected(self):
        n = 6
        edges = [
            (0, 1, 1), 
            (1, 2, 2),
            (3, 4, 3)
        ]
        sources = [0, 3]
        tree_edges = shortest_path_tree(n, edges, sources)
        self.validate_tree(n, edges, sources, tree_edges)

    def test_self_loop(self):
        n = 4
        edges = [
            (0, 0, 5),  # self-loop
            (0, 1, 1),
            (1, 2, 2),
            (2, 3, 3),
            (3, 3, 1)   # self-loop at node 3
        ]
        sources = [0]
        tree_edges = shortest_path_tree(n, edges, sources)
        self.validate_tree(n, edges, sources, tree_edges)

    def test_multiple_edges(self):
        n = 4
        edges = [
            (0, 1, 10), (0, 1, 5),  # multiple edges between 0 and 1
            (1, 2, 3), 
            (0, 2, 20),
            (2, 3, 2), 
            (1, 3, 15)
        ]
        sources = [0]
        tree_edges = shortest_path_tree(n, edges, sources)
        self.validate_tree(n, edges, sources, tree_edges)

if __name__ == '__main__':
    unittest.main()