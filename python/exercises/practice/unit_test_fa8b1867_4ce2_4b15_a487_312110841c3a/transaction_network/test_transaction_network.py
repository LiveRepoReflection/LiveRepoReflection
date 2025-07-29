import unittest
from transaction_network import is_transaction_consistent

class TestTransactionNetwork(unittest.TestCase):
    def test_simple_valid_transaction(self):
        network_size = 3
        connections = [(0, 1), (1, 2)]
        transaction_proposals = {
            0: [(0, "x", 5, 10)],
            1: [(1, "y", 20, 25)],
            2: [(2, "z", 100, 105)]
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_disconnected_network(self):
        network_size = 3
        connections = [(0, 1)]  # Node 2 is disconnected
        transaction_proposals = {
            0: [(0, "x", 5, 10)],
            1: [(1, "y", 20, 25)],
            2: [(2, "z", 100, 105)]
        }
        failed_nodes = set()
        self.assertFalse(is_transaction_consistent(network_size, connections, 
                                                 transaction_proposals, failed_nodes))

    def test_failed_nodes(self):
        network_size = 3
        connections = [(0, 1), (1, 2)]
        transaction_proposals = {
            0: [(0, "x", 5, 10)],
            1: [(1, "y", 20, 25)],
            2: [(2, "z", 100, 105)]
        }
        failed_nodes = {1}  # Node 1 has failed
        self.assertFalse(is_transaction_consistent(network_size, connections, 
                                                 transaction_proposals, failed_nodes))

    def test_empty_transaction(self):
        network_size = 3
        connections = [(0, 1), (1, 2)]
        transaction_proposals = {}
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_single_node_network(self):
        network_size = 1
        connections = []
        transaction_proposals = {
            0: [(0, "x", 5, 10)]
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_fully_connected_network(self):
        network_size = 4
        connections = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        transaction_proposals = {
            0: [(0, "w", 1, 2)],
            1: [(1, "x", 3, 4)],
            2: [(2, "y", 5, 6)],
            3: [(3, "z", 7, 8)]
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_multiple_modifications_per_node(self):
        network_size = 2
        connections = [(0, 1)]
        transaction_proposals = {
            0: [(0, "x", 1, 2), (0, "y", 3, 4)],
            1: [(1, "z", 5, 6), (1, "w", 7, 8)]
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_all_nodes_failed(self):
        network_size = 3
        connections = [(0, 1), (1, 2)]
        transaction_proposals = {
            0: [(0, "x", 5, 10)],
            1: [(1, "y", 20, 25)],
            2: [(2, "z", 100, 105)]
        }
        failed_nodes = {0, 1, 2}
        self.assertFalse(is_transaction_consistent(network_size, connections, 
                                                 transaction_proposals, failed_nodes))

    def test_cross_node_modifications(self):
        network_size = 2
        connections = [(0, 1)]
        transaction_proposals = {
            0: [(1, "x", 5, 10)],  # Node 0 trying to modify Node 1's data
            1: [(0, "y", 20, 25)]  # Node 1 trying to modify Node 0's data
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_large_network(self):
        network_size = 100
        connections = [(i, i+1) for i in range(99)]  # Ring topology
        transaction_proposals = {
            i: [(i, f"key_{i}", i, i+1)] for i in range(100)
        }
        failed_nodes = set()
        self.assertTrue(is_transaction_consistent(network_size, connections, 
                                               transaction_proposals, failed_nodes))

    def test_invalid_node_ids(self):
        network_size = 2
        connections = [(0, 1)]
        transaction_proposals = {
            0: [(3, "x", 5, 10)]  # Invalid node ID
        }
        failed_nodes = set()
        self.assertFalse(is_transaction_consistent(network_size, connections, 
                                                 transaction_proposals, failed_nodes))

if __name__ == '__main__':
    unittest.main()