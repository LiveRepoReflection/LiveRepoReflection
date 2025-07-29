import unittest
import math

from network_partitioning import min_total_cost

class NetworkPartitioningTest(unittest.TestCase):

    def test_single_node(self):
        # Single node: only one cluster possible. Intra-cluster cost = 0.
        n = 1
        k = 1
        adj_list = [[]]
        workload = [10]
        expected = 0
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

    def test_invalid_partition(self):
        # Partitioning not possible since k > n.
        n = 3
        k = 4
        adj_list = [[], [], []]
        workload = [1, 2, 3]
        expected = -1
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

    def test_example_partition(self):
        # Example from problem description:
        # n = 4, k = 2, graph: 0-1, 1-2, 2-3; workloads: [10, 5, 8, 2]
        # One optimal partition is: Cluster 1: {0, 1}, Cluster 2: {2, 3}
        # Intra-cluster costs:
        #   Cluster1: 10 * 5 = 50
        #   Cluster2: 8 * 2 = 16
        # Inter-cluster penalty between Cluster1 and Cluster2:
        #   Minimum latency = 1 (between nodes 1 and 2)
        #   Penalty = 1 * (10+5) * (8+2) = 1 * 15 * 10 = 150
        # Total expected cost = 50 + 16 + 150 = 216
        n = 4
        k = 2
        adj_list = [[1], [0, 2], [1, 3], [2]]
        workload = [10, 5, 8, 2]
        expected = 216
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

    def test_disconnected_graph_partition(self):
        # Graph with a disconnected node.
        # n = 3, k = 2.
        # Graph: 0 <-> 1; node 2 is isolated.
        # Optimal partition: Merge disconnected node with a connected one to avoid infinite penalty.
        # One optimal partition is: Cluster 1: {0, 2}, Cluster 2: {1}
        # Intra-cluster cost for Cluster 1: 5 * 5 = 25, Cluster 2: 0.
        # Inter-cluster penalty: 
        #   Calculate distances from Cluster1 to Cluster2:
        #     Distance between 0 and 1 = 1, (even though 2 to 1 is infinite, minimum latency is 1)
        #   Penalty = 1 * (5+5) * 5 = 1 * 10 * 5 = 50
        # Total expected cost = 25 + 50 = 75
        n = 3
        k = 2
        adj_list = [[1], [0], []]
        workload = [5, 5, 5]
        expected = 75
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

    def test_linear_chain_partition(self):
        # Graph: linear chain 0-1-2-3-4, workloads: [1, 2, 3, 4, 5], partition into 2 clusters.
        # One possible optimal partition is to partition as:
        #   Cluster 1: {0, 1} and Cluster 2: {2, 3, 4}
        # Intra-cluster cost for Cluster 1: 1*2 = 2.
        # Intra-cluster cost for Cluster 2: (3*4 + 3*5 + 4*5) = 12 + 15 + 20 = 47.
        # Inter-cluster penalty:
        #   Minimum latency between a node in Cluster 1 and Cluster 2 is between node 1 and 2 (distance = 1).
        #   Sum workloads in Cluster 1 = 1+2 = 3, in Cluster 2 = 3+4+5 = 12.
        #   Penalty = 1 * 3 * 12 = 36.
        # Total expected cost = 2 + 47 + 36 = 85
        n = 5
        k = 2
        adj_list = [[1], [0, 2], [1, 3], [2, 4], [3]]
        workload = [1, 2, 3, 4, 5]
        expected = 85
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

    def test_full_cluster_intra_cost(self):
        # k = 1 means the entire set is one cluster.
        # Graph: assume connectivity is irrelevant since penalty cost is 0.
        # Intra-cluster cost = sum of products of all distinct pairs.
        # For n = 4 with workloads: [2, 3, 4, 5]
        # Pairs: (2*3)+(2*4)+(2*5)+(3*4)+(3*5)+(4*5)
        # Calculation: 6 + 8 + 10 + 12 + 15 + 20 = 71
        n = 4
        k = 1
        adj_list = [[1], [0, 2], [1, 3], [2]]
        workload = [2, 3, 4, 5]
        expected = 71
        self.assertEqual(min_total_cost(n, k, adj_list, workload), expected)

if __name__ == '__main__':
    unittest.main()