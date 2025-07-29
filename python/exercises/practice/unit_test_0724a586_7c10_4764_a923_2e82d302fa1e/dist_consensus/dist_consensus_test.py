import unittest
import random
from dist_consensus.dist_consensus import simulate_consensus

class TestDistributedConsensus(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for determinism in tests
        random.seed(42)

    def test_fully_connected_no_loss(self):
        # Fully connected network: every node is connected to every other node
        N = 5
        neighbors = []
        for i in range(N):
            # Every node has all other nodes as neighbors.
            neighbors.append([j for j in range(N) if j != i])
        initial_values = ['node' + str(i) for i in range(N)]
        max_rounds = 10
        message_loss_probability = 0.0
        
        final_values = simulate_consensus(N, neighbors, initial_values, max_rounds, message_loss_probability)
        self.assertEqual(len(final_values), N)
        # In a fully connected network with no message loss, consensus should be achieved:
        self.assertEqual(len(set(final_values)), 1)

    def test_disconnected_clusters(self):
        # Two separate clusters: one with nodes 0,1,2; another with nodes 3,4.
        N = 5
        neighbors = [
            [1, 2],  # Cluster 1
            [0, 2],
            [0, 1],
            [4],     # Cluster 2
            [3]
        ]
        # Distinct initial values per cluster
        initial_values = ["A", "A", "A", "B", "B"]
        max_rounds = 10
        message_loss_probability = 0.0
        
        final_values = simulate_consensus(N, neighbors, initial_values, max_rounds, message_loss_probability)
        self.assertEqual(len(final_values), N)
        # Check that nodes in cluster 1 reached consensus
        cluster1 = {final_values[0], final_values[1], final_values[2]}
        self.assertEqual(len(cluster1), 1)
        # Check that nodes in cluster 2 reached consensus
        cluster2 = {final_values[3], final_values[4]}
        self.assertEqual(len(cluster2), 1)
        # The clusters may have reached different consensus values between each other

    def test_isolated_node(self):
        # One node is completely isolated and should retain its initial value.
        N = 5
        neighbors = [
            [1],    # Node 0 connected to Node 1
            [0],    # Node 1 connected to Node 0
            [3],    # Node 2 connected to Node 3
            [2],    # Node 3 connected to Node 2
            []      # Node 4 is isolated
        ]
        initial_values = [10, 20, 30, 40, 50]
        max_rounds = 10
        message_loss_probability = 0.0
        
        final_values = simulate_consensus(N, neighbors, initial_values, max_rounds, message_loss_probability)
        self.assertEqual(len(final_values), N)
        # The isolated node (node 4) should not change its value.
        self.assertEqual(final_values[4], 50)

    def test_with_message_loss(self):
        # Network with potential message loss: linear chain of 6 nodes
        N = 6
        neighbors = [
            [1],        # Node 0
            [0, 2],     # Node 1
            [1, 3],     # Node 2
            [2, 4],     # Node 3
            [3, 5],     # Node 4
            [4]         # Node 5
        ]
        initial_values = [100, 200, 300, 400, 500, 600]
        max_rounds = 20
        message_loss_probability = 0.5
        
        final_values = simulate_consensus(N, neighbors, initial_values, max_rounds, message_loss_probability)
        self.assertEqual(len(final_values), N)
        # With message loss, full consensus is not guaranteed.
        # Check that each final value is one of the initial values.
        for value in final_values:
            self.assertIn(value, initial_values)

if __name__ == '__main__':
    unittest.main()