import unittest
from social_pagerank import distributed_pagerank

class SocialPageRankTest(unittest.TestCase):
    def assertSumAlmostOne(self, result, delta=1e-5):
        total = sum(result.values())
        self.assertAlmostEqual(total, 1.0, delta=delta)

    def test_basic_network(self):
        K = 2
        nodes = [
            {'users': [0, 1], 'edges': {0: [1], 1: [2]}},
            {'users': [2, 3], 'edges': {2: [3], 3: [0]}}
        ]
        N = 4
        iterations = 20
        result = distributed_pagerank(K, nodes, N, iterations)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), N)
        self.assertSumAlmostOne(result)
        for pr in result.values():
            self.assertGreaterEqual(pr, 0)

    def test_single_node_network(self):
        K = 1
        nodes = [
            {'users': [0, 1, 2], 'edges': {0: [1], 1: [2], 2: [0]}}
        ]
        N = 3
        iterations = 30
        result = distributed_pagerank(K, nodes, N, iterations)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), N)
        self.assertSumAlmostOne(result)
        for pr in result.values():
            self.assertGreaterEqual(pr, 0)

    def test_dangling_nodes(self):
        K = 2
        nodes = [
            {'users': [0, 1], 'edges': {0: [2]}},  # User 1 is dangling.
            {'users': [2, 3], 'edges': {2: [0]}}     # User 3 is dangling.
        ]
        N = 4
        iterations = 25
        result = distributed_pagerank(K, nodes, N, iterations)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), N)
        self.assertSumAlmostOne(result)
        for pr in result.values():
            self.assertGreaterEqual(pr, 0)

    def test_disconnected_graph(self):
        K = 2
        nodes = [
            {'users': [0, 1], 'edges': {0: [1], 1: []}},
            {'users': [2, 3], 'edges': {2: [3], 3: []}}
        ]
        N = 4
        iterations = 20
        result = distributed_pagerank(K, nodes, N, iterations)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), N)
        self.assertSumAlmostOne(result)
        subgraph1_total = result[0] + result[1]
        subgraph2_total = result[2] + result[3]
        self.assertAlmostEqual(subgraph1_total, subgraph2_total, delta=0.1)

    def test_complex_network(self):
        K = 3
        nodes = [
            {
                'users': [0, 1, 2],
                'edges': {0: [1, 2], 1: [2], 2: [0]}
            },
            {
                'users': [3, 4],
                'edges': {3: [4], 4: [3, 2]}
            },
            {
                'users': [5, 6],
                'edges': {5: [6], 6: []}  # Dangling node.
            }
        ]
        N = 7
        iterations = 30
        result = distributed_pagerank(K, nodes, N, iterations)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), N)
        self.assertSumAlmostOne(result)
        for pr in result.values():
            self.assertGreaterEqual(pr, 0)
        # Verify that node with multiple incoming edges gets relatively higher PageRank.
        self.assertGreater(result[2], result[5])
        self.assertGreater(result[2], result[6])

if __name__ == '__main__':
    unittest.main()