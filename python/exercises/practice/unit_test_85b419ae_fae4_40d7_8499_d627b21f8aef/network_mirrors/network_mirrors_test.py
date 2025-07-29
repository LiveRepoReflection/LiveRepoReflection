import unittest
import itertools
from collections import deque

from network_mirrors import find_optimal_mirrors

def build_graph(N, edges):
    graph = {i: [] for i in range(N)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph

def multi_source_bfs(mirrors, graph, N):
    # Initialize all distances to N (treated as infinity)
    distances = [N] * N
    q = deque()
    
    for m in mirrors:
        distances[m] = 0
        q.append(m)
    
    while q:
        cur = q.popleft()
        for neighbor in graph[cur]:
            if distances[neighbor] > distances[cur] + 1:
                distances[neighbor] = distances[cur] + 1
                q.append(neighbor)
    return distances

def compute_avg_weighted_path(mirrors, N, edges, importance_scores):
    graph = build_graph(N, edges)
    distances = multi_source_bfs(mirrors, graph, N)
    total = sum(importance_scores[i] * distances[i] for i in range(N))
    return total / N

def brute_force_optimal_score(N, edges, importance_scores, K):
    best_score = float('inf')
    best_set = None
    for comb in itertools.combinations(range(N), K):
        score = compute_avg_weighted_path(comb, N, edges, importance_scores)
        if score < best_score:
            best_score = score
            best_set = comb
    return best_score, best_set

class NetworkMirrorsTest(unittest.TestCase):
    def test_single_node(self):
        N = 1
        edges = []
        importance_scores = [10]
        K = 1
        # Only possible mirror is 0
        result = find_optimal_mirrors(N, edges, importance_scores, K)
        self.assertEqual(result, [0])
        score = compute_avg_weighted_path(result, N, edges, importance_scores)
        self.assertEqual(score, 0)  # mirror at the only node means 0 distance

    def test_line_graph(self):
        # Graph: 0 - 1 - 2
        N = 3
        edges = [(0, 1), (1, 2)]
        importance_scores = [3, 10, 3]
        K = 1
        result = find_optimal_mirrors(N, edges, importance_scores, K)
        # In a line graph, the best mirror should be at the central node (node 1)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], range(N))
        # For this small case, the optimal mirror is clearly node 1.
        self.assertEqual(result, [1])
        score = compute_avg_weighted_path(result, N, edges, importance_scores)
        self.assertEqual(score,  (3*1 + 10*0 + 3*1) / 3)

    def test_star_graph(self):
        # Graph: star with center node 0 and leaves 1,2,3.
        N = 4
        edges = [(0, 1), (0, 2), (0, 3)]
        importance_scores = [1, 100, 100, 100]
        K = 1
        result = find_optimal_mirrors(N, edges, importance_scores, K)
        # The optimal placement should be the center (node 0)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, [0])
        score = compute_avg_weighted_path(result, N, edges, importance_scores)
        # Leaves have distance 1 and center 0, so score should be (1*0 + 100*1*3)/4
        expected_score = (0 + 100*1 + 100*1 + 100*1) / 4
        self.assertEqual(score, expected_score)

    def test_cycle_graph(self):
        # Graph: Cycle graph with 5 nodes: 0-1-2-3-4-0
        N = 5
        edges = [(0,1), (1,2), (2,3), (3,4), (4,0)]
        importance_scores = [5, 2, 8, 2, 5]
        K = 2
        result = find_optimal_mirrors(N, edges, importance_scores, K)
        self.assertEqual(len(result), 2)
        for node in result:
            self.assertIn(node, range(N))
        candidate_score = compute_avg_weighted_path(result, N, edges, importance_scores)
        # For small N, we can compare against brute-force optimal.
        optimal_score, optimal_set = brute_force_optimal_score(N, edges, importance_scores, K)
        self.assertEqual(candidate_score, optimal_score)

    def test_tree_graph(self):
        # Graph: Binary tree structure
        #         0
        #       /   \
        #      1     2
        #     / \   / 
        #    3   4 5  
        N = 6
        edges = [(0,1), (0,2), (1,3), (1,4), (2,5)]
        importance_scores = [1, 3, 3, 10, 10, 5]
        K = 2
        result = find_optimal_mirrors(N, edges, importance_scores, K)
        self.assertEqual(len(result), 2)
        for node in result:
            self.assertIn(node, range(N))
        candidate_score = compute_avg_weighted_path(result, N, edges, importance_scores)
        # For this small tree, check candidate score equals brute force optimum.
        optimal_score, optimal_set = brute_force_optimal_score(N, edges, importance_scores, K)
        self.assertEqual(candidate_score, optimal_score)

if __name__ == '__main__':
    unittest.main()