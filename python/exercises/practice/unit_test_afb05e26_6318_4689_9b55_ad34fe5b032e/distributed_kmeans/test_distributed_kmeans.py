import unittest
import random
import math
from distributed_kmeans import distributed_kmeans

class TestDistributedKMeans(unittest.TestCase):
    
    def test_basic_functionality(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8], [0.8, 1.2]],
            [[5.0, 5.0], [5.2, 4.8], [4.8, 5.2]]
        ]
        k = 2
        initial_centroids = [[1.0, 1.0], [5.0, 5.0]]
        
        result = distributed_kmeans(data_fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        # Check that centroids are close to expected values
        self.assertTrue(any(math.sqrt((c[0] - 1.0) ** 2 + (c[1] - 1.0) ** 2) < 0.5 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 5.0) ** 2 + (c[1] - 5.0) ** 2) < 0.5 for c in result))

    def test_three_clusters(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8], [0.8, 1.2]],
            [[5.0, 5.0], [5.2, 4.8], [4.8, 5.2]],
            [[10.0, 1.0], [9.8, 1.2], [10.2, 0.8]]
        ]
        k = 3
        initial_centroids = [[1.0, 1.0], [5.0, 5.0], [10.0, 1.0]]
        
        result = distributed_kmeans(data_fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        # Check that centroids are close to expected values
        self.assertTrue(any(math.sqrt((c[0] - 1.0) ** 2 + (c[1] - 1.0) ** 2) < 0.5 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 5.0) ** 2 + (c[1] - 5.0) ** 2) < 0.5 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 10.0) ** 2 + (c[1] - 1.0) ** 2) < 0.5 for c in result))

    def test_higher_dimensions(self):
        data_fragments = [
            [[1.0, 1.0, 1.0], [1.2, 0.8, 1.1]],
            [[5.0, 5.0, 5.0], [5.2, 4.8, 5.1]]
        ]
        k = 2
        initial_centroids = [[1.0, 1.0, 1.0], [5.0, 5.0, 5.0]]
        
        result = distributed_kmeans(data_fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        self.assertEqual(len(result[0]), 3)  # Check dimensionality

    def test_empty_data_fragments(self):
        data_fragments = []
        k = 2
        initial_centroids = [[1.0, 1.0], [5.0, 5.0]]
        
        with self.assertRaises(ValueError):
            distributed_kmeans(data_fragments, k, initial_centroids)

    def test_invalid_k(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8], [0.8, 1.2]],
            [[5.0, 5.0], [5.2, 4.8], [4.8, 5.2]]
        ]
        k = 0
        initial_centroids = []
        
        with self.assertRaises(ValueError):
            distributed_kmeans(data_fragments, k, initial_centroids)

    def test_k_too_large(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8]],
            [[5.0, 5.0]]
        ]
        k = 4  # Total data points is 3
        initial_centroids = [[1.0, 1.0], [5.0, 5.0], [10.0, 10.0], [15.0, 15.0]]
        
        with self.assertRaises(ValueError):
            distributed_kmeans(data_fragments, k, initial_centroids)

    def test_dimension_mismatch(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8]],
            [[5.0, 5.0, 5.0], [5.2, 4.8, 4.5]]  # Different dimensions
        ]
        k = 2
        initial_centroids = [[1.0, 1.0], [5.0, 5.0]]
        
        with self.assertRaises(ValueError):
            distributed_kmeans(data_fragments, k, initial_centroids)

    def test_centroid_dimension_mismatch(self):
        data_fragments = [
            [[1.0, 1.0], [1.2, 0.8]],
            [[5.0, 5.0], [5.2, 4.8]]
        ]
        k = 2
        initial_centroids = [[1.0, 1.0, 1.0], [5.0, 5.0, 5.0]]  # Different dimensions
        
        with self.assertRaises(ValueError):
            distributed_kmeans(data_fragments, k, initial_centroids)

    def test_convergence(self):
        # Generate data that should converge quickly
        data_fragments = [
            [[1.0 + random.uniform(-0.1, 0.1), 1.0 + random.uniform(-0.1, 0.1)] for _ in range(10)],
            [[5.0 + random.uniform(-0.1, 0.1), 5.0 + random.uniform(-0.1, 0.1)] for _ in range(10)]
        ]
        k = 2
        initial_centroids = [[1.0, 1.0], [5.0, 5.0]]
        
        result = distributed_kmeans(data_fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        # With tight clusters, centroids should be very close to the original centers
        self.assertTrue(any(math.sqrt((c[0] - 1.0) ** 2 + (c[1] - 1.0) ** 2) < 0.2 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 5.0) ** 2 + (c[1] - 5.0) ** 2) < 0.2 for c in result))

    def test_many_fragments(self):
        # Test with many small fragments
        fragments = []
        for i in range(20):  # 20 fragments
            if i < 10:
                fragments.append([[1.0 + random.uniform(-0.1, 0.1), 1.0 + random.uniform(-0.1, 0.1)]])
            else:
                fragments.append([[5.0 + random.uniform(-0.1, 0.1), 5.0 + random.uniform(-0.1, 0.1)]])
        
        k = 2
        initial_centroids = [[1.0, 1.0], [5.0, 5.0]]
        
        result = distributed_kmeans(fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        # With tight clusters, centroids should be very close to the original centers
        self.assertTrue(any(math.sqrt((c[0] - 1.0) ** 2 + (c[1] - 1.0) ** 2) < 0.2 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 5.0) ** 2 + (c[1] - 5.0) ** 2) < 0.2 for c in result))

    def test_large_dataset(self):
        # Generate a larger dataset with 3 distinct clusters
        fragments = []
        # Cluster 1 around (1,1)
        fragments.append([[1.0 + random.uniform(-0.5, 0.5), 1.0 + random.uniform(-0.5, 0.5)] for _ in range(50)])
        # Cluster 2 around (5,5)
        fragments.append([[5.0 + random.uniform(-0.5, 0.5), 5.0 + random.uniform(-0.5, 0.5)] for _ in range(50)])
        # Cluster 3 around (10,1)
        fragments.append([[10.0 + random.uniform(-0.5, 0.5), 1.0 + random.uniform(-0.5, 0.5)] for _ in range(50)])
        
        k = 3
        initial_centroids = [[1.0, 1.0], [5.0, 5.0], [10.0, 1.0]]
        
        result = distributed_kmeans(fragments, k, initial_centroids)
        
        self.assertEqual(len(result), k)
        # Check that final centroids are close to expected centers
        self.assertTrue(any(math.sqrt((c[0] - 1.0) ** 2 + (c[1] - 1.0) ** 2) < 1.0 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 5.0) ** 2 + (c[1] - 5.0) ** 2) < 1.0 for c in result))
        self.assertTrue(any(math.sqrt((c[0] - 10.0) ** 2 + (c[1] - 1.0) ** 2) < 1.0 for c in result))

if __name__ == '__main__':
    unittest.main()