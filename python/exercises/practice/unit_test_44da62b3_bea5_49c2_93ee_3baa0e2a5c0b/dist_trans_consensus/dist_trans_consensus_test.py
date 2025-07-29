import unittest
from dist_trans_consensus import process_transaction

class DistTransConsensusTest(unittest.TestCase):
    def test_all_nodes_commit(self):
        # Simulate a transaction with 3 nodes, all well-connected.
        tx_id = 101
        participants = [1, 2, 3]
        bandwidth_matrix = [
            [10, 10, 10],
            [10, 10, 10],
            [10, 10, 10],
        ]
        capacities = [50, 30, 20]
        message_size = 1
        result = process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size)
        self.assertEqual(result['decision'], 'commit')
        self.assertIn(result['leader'], participants)
        self.assertIsInstance(result['messages_sent'], int)

    def test_node_failure(self):
        # Simulate a transaction in a 5-node system where one node is nonfunctional.
        # Node 3 is failed (bandwidth zero to/from node 3, capacity 0).
        tx_id = 102
        participants = [1, 2, 3, 4, 5]
        bandwidth_matrix = [
            [10, 10, 0, 10, 10],
            [10, 10, 0, 10, 10],
            [0,  0,  0,  0,  0],
            [10, 10, 0, 10, 10],
            [10, 10, 0, 10, 10],
        ]
        capacities = [40, 35, 0, 20, 15]
        message_size = 1
        result = process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size)
        # Even though one node has failed, consensus can be reached if a majority is functional.
        self.assertEqual(result['decision'], 'commit')
        self.assertNotEqual(result['leader'], 3)

    def test_insufficient_bandwidth(self):
        # Simulate a transaction where nodes lack the communication links needed.
        tx_id = 103
        participants = [1, 2, 3]
        bandwidth_matrix = [
            [10,  0,  0],
            [0,  10,  0],
            [0,   0, 10],
        ]
        capacities = [30, 30, 30]
        message_size = 5
        # With no inter-node communication available, consensus should abort.
        result = process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size)
        self.assertEqual(result['decision'], 'abort')

    def test_large_scale_consensus(self):
        # Test scalability and efficiency in a larger network.
        tx_id = 104
        n = 10
        participants = list(range(1, n + 1))
        bandwidth_matrix = []
        # Generate a uniform high-bandwidth network for simplicity.
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(10)
                else:
                    row.append(8)
            bandwidth_matrix.append(row)
        capacities = [i * 5 for i in range(1, n + 1)]
        message_size = 2
        result = process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size)
        self.assertEqual(result['decision'], 'commit')
        self.assertIn(result['leader'], participants)

    def test_zero_bandwidth_edge_case(self):
        # Test the edge-case where there is zero bandwidth between nodes, preventing any consensus.
        tx_id = 105
        participants = [1, 2]
        bandwidth_matrix = [
            [10, 0],
            [0, 10],
        ]
        capacities = [20, 20]
        message_size = 3
        result = process_transaction(tx_id, participants, bandwidth_matrix, capacities, message_size)
        self.assertEqual(result['decision'], 'abort')
        # Communication is only local; consensus must fail.

if __name__ == '__main__':
    unittest.main()