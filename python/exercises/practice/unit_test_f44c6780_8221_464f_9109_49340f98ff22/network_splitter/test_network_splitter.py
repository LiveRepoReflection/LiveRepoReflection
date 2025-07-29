import unittest
from network_splitter import network_splitter
import networkx as nx

class TestNetworkSplitter(unittest.TestCase):
    def setUp(self):
        # Simple 4-node graph
        self.simple_graph = nx.Graph()
        self.simple_graph.add_weighted_edges_from([
            ('A', 'B', 1),
            ('B', 'C', 1),
            ('C', 'D', 1),
            ('A', 'D', 5)
        ])
        
        # Larger test graph
        self.larger_graph = nx.Graph()
        self.larger_graph.add_weighted_edges_from([
            (1, 2, 3), (1, 3, 2), (2, 4, 5),
            (3, 4, 1), (3, 5, 4), (4, 6, 2),
            (5, 6, 3), (5, 7, 1), (6, 8, 4),
            (7, 8, 2), (7, 9, 3), (8, 10, 1)
        ])

    def test_basic_functionality(self):
        clusters = network_splitter(self.simple_graph, k=2, alpha=0.5)
        self.assertEqual(len(clusters), 4)  # 4 nodes
        self.assertEqual(len(set(clusters.values())), 2)  # 2 clusters

    def test_cluster_size_constraint(self):
        clusters = network_splitter(self.simple_graph, k=2, alpha=0.5)
        cluster_counts = {}
        for node, cluster in clusters.items():
            cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
        self.assertTrue(all(count >= 1 for count in cluster_counts.values()))

    def test_alpha_variation(self):
        # Test that different alpha values produce different results
        clusters1 = network_splitter(self.simple_graph, k=2, alpha=0.1)
        clusters2 = network_splitter(self.simple_graph, k=2, alpha=0.9)
        self.assertNotEqual(clusters1, clusters2)

    def test_larger_graph(self):
        clusters = network_splitter(self.larger_graph, k=3, alpha=0.5)
        self.assertEqual(len(clusters), 10)  # 10 nodes
        self.assertEqual(len(set(clusters.values())), 3)  # 3 clusters

    def test_single_cluster(self):
        clusters = network_splitter(self.simple_graph, k=1, alpha=0.5)
        self.assertEqual(len(set(clusters.values())), 1)

    def test_max_clusters(self):
        clusters = network_splitter(self.simple_graph, k=4, alpha=0.5)
        self.assertEqual(len(set(clusters.values())), 4)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            network_splitter(self.simple_graph, k=0, alpha=0.5)
        with self.assertRaises(ValueError):
            network_splitter(self.simple_graph, k=5, alpha=0.5)

    def test_invalid_alpha(self):
        with self.assertRaises(ValueError):
            network_splitter(self.simple_graph, k=2, alpha=-0.1)
        with self.assertRaises(ValueError):
            network_splitter(self.simple_graph, k=2, alpha=1.1)

if __name__ == '__main__':
    unittest.main()