import unittest
from critical_nodes import critical_nodes

def build_graph(N, links):
    # helper function to check connectivity after removal
    graph = {i: set() for i in range(N)}
    for u, v in links:
        graph[u].add(v)
        graph[v].add(u)
    return graph

def count_components(N, links, removed):
    # Count connected components in graph after removing nodes in 'removed'
    removed = set(removed)
    graph = build_graph(N, links)
    visited = [False] * N
    def dfs(node):
        stack = [node]
        while stack:
            cur = stack.pop()
            for neigh in graph[cur]:
                if neigh not in removed and not visited[neigh]:
                    visited[neigh] = True
                    stack.append(neigh)
    components = 0
    for i in range(N):
        if i in removed or visited[i]:
            continue
        visited[i] = True
        dfs(i)
        components += 1
    return components

class CriticalNodesTest(unittest.TestCase):

    def test_single_node_no_removal(self):
        # Only one node and already in one component. K=1.
        N = 1
        links = []
        K = 1
        result = critical_nodes(N, links, K)
        # Minimum set is empty set.
        self.assertEqual(result, [])
        self.assertEqual(count_components(N, links, result), 1)

    def test_single_node_impossible(self):
        # One node, but want more than 1 connected component.
        N = 1
        links = []
        K = 2
        result = critical_nodes(N, links, K)
        # No removal possible, so expect empty list.
        self.assertEqual(result, [])
        self.assertEqual(count_components(N, links, result), 1)

    def test_already_disconnected(self):
        # Graph with no edges is already totally disconnected.
        N = 5
        links = []
        K = 3
        result = critical_nodes(N, links, K)
        # No removal needed because graph already has 5 components.
        self.assertEqual(result, [])
        self.assertGreaterEqual(count_components(N, links, result), K)

    def test_chain_graph(self):
        # Chain: 0-1-2-3-4, K=3 should remove minimal nodes.
        N = 5
        links = [(0,1), (1,2), (2,3), (3,4)]
        K = 3
        expected = [1, 3]
        result = critical_nodes(N, links, K)
        # The returned result should be sorted.
        self.assertEqual(result, sorted(result))
        self.assertEqual(result, expected)
        self.assertGreaterEqual(count_components(N, links, result), K)

    def test_star_graph(self):
        # Star graph: center node 0 connects to others.
        # Removing node 0 disconnects the graph into (N-1) isolated nodes.
        N = 5
        links = [(0,1), (0,2), (0,3), (0,4)]
        K = 3
        expected = [0]
        result = critical_nodes(N, links, K)
        self.assertEqual(result, sorted(result))
        self.assertEqual(result, expected)
        self.assertGreaterEqual(count_components(N, links, result), K)

    def test_complete_graph_no_solution(self):
        # In a complete graph, removal of any subset (that is not all nodes)
        # leaves the remaining nodes fully connected.
        # Hence, if K > 1, no valid removal exists.
        N = 4
        links = []
        for i in range(N):
            for j in range(i+1, N):
                links.append((i, j))
        K = 2
        result = critical_nodes(N, links, K)
        self.assertEqual(result, [])
        self.assertEqual(count_components(N, links, result), 1)

    def test_cycle_graph_two_removals(self):
        # Cycle graph: 0-1-2-3-0.
        # The graph is 2-connected; minimum removal to get at least 2 components is 2.
        # There are multiple valid pairs, but lexicographically smallest is expected.
        N = 4
        links = [(0,1), (1,2), (2,3), (3,0)]
        K = 2
        # Possible removals that work include [0,2] and [1,3]. Lex smallest is [0,2].
        expected = [0, 2]
        result = critical_nodes(N, links, K)
        self.assertEqual(result, sorted(result))
        self.assertEqual(result, expected)
        self.assertGreaterEqual(count_components(N, links, result), K)

    def test_complex_graph(self):
        # A slightly more complex graph
        N = 8
        links = [
            (0,1), (1,2), (2,3), (3,0),  # cycle component
            (2,4),  # connection from cycle to tail
            (4,5), (5,6), (6,7)  # tail chain
        ]
        # Initially the graph is connected.
        # Removing node 2 disconnects cycle and tail.
        K = 2
        expected = [2]
        result = critical_nodes(N, links, K)
        self.assertEqual(result, sorted(result))
        self.assertEqual(result, expected)
        self.assertGreaterEqual(count_components(N, links, result), K)

if __name__ == '__main__':
    unittest.main()