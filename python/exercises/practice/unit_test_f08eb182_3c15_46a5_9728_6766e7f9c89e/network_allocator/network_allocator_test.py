import unittest
from network_allocator import allocate

class NetworkAllocatorTest(unittest.TestCase):

    def validate_allocation(self, n, k, demands, capacities, allocation):
        # Check that allocation length equals n
        self.assertEqual(len(allocation), n, "Allocation length does not match number of nodes.")
        # Check that each allocation is in the valid range [0, k-1]
        for a in allocation:
            self.assertTrue(0 <= a < k, "Allocation value out of range.")
        # Check that resource usage in each cluster does not exceed its capacity
        cluster_usage = [0] * k
        for idx, cluster in enumerate(allocation):
            cluster_usage[cluster] += demands[idx]
        for i in range(k):
            self.assertLessEqual(cluster_usage[i], capacities[i], 
                                 f"Cluster {i} exceeds capacity: {cluster_usage[i]} > {capacities[i]}.")

    def test_single_node(self):
        # Single node, single cluster, no edges.
        n = 1
        k = 1
        demands = [50]
        capacities = [100]
        edges = []  # Single node graph is trivially connected
        allocation = allocate(n, k, demands, capacities, edges)
        self.validate_allocation(n, k, demands, capacities, allocation)

    def test_two_nodes(self):
        # Two nodes, two clusters, simple edge
        n = 2
        k = 2
        demands = [30, 70]
        capacities = [50, 70]
        edges = [
            (0, 1, 10)
        ]
        allocation = allocate(n, k, demands, capacities, edges)
        self.validate_allocation(n, k, demands, capacities, allocation)

    def test_star_network(self):
        # Five nodes arranged in a star structure
        n = 5
        k = 2
        demands = [10, 20, 30, 40, 50]
        capacities = [60, 90]
        # Node 0 is the center connected to all other nodes
        edges = [
            (0, 1, 5),
            (0, 2, 5),
            (0, 3, 5),
            (0, 4, 5)
        ]
        allocation = allocate(n, k, demands, capacities, edges)
        self.validate_allocation(n, k, demands, capacities, allocation)

    def test_complex_graph(self):
        # Six nodes with more complex connectivity and 3 clusters
        n = 6
        k = 3
        demands = [10, 15, 20, 25, 30, 35]
        capacities = [50, 50, 50]
        edges = [
            (0, 1, 5),
            (1, 2, 5),
            (2, 3, 10),
            (3, 4, 2),
            (4, 5, 2),
            (0, 5, 20),
            (1, 4, 3)
        ]
        allocation = allocate(n, k, demands, capacities, edges)
        self.validate_allocation(n, k, demands, capacities, allocation)

    def test_full_mesh(self):
        # Test with a fully connected graph with 4 nodes and 2 clusters.
        n = 4
        k = 2
        demands = [25, 25, 25, 25]
        capacities = [50, 50]
        # Create a full mesh: every pair of nodes is connected.
        edges = []
        weights = {
            (0,1): 3, (0,2): 4, (0,3): 5,
            (1,2): 6, (1,3): 7,
            (2,3): 2
        }
        for (u, v), w in weights.items():
            edges.append((u, v, w))
        allocation = allocate(n, k, demands, capacities, edges)
        self.validate_allocation(n, k, demands, capacities, allocation)

if __name__ == '__main__':
    unittest.main()