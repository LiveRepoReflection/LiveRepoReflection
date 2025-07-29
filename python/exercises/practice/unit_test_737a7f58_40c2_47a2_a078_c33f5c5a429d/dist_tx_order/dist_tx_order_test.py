import unittest
from dist_tx_order import build_dependency_graph, order_transactions, commit_protocol

class TestDistTxOrder(unittest.TestCase):
    def setUp(self):
        # Define sample transactions using a dictionary structure.
        # Each transaction has an 'id', a list of 'operations', and a list of 'dependencies'.
        self.tx1 = {
            "id": "T1",
            "operations": [
                {"node": "N1", "operation": "write", "data": "A"}
            ],
            "dependencies": []
        }
        self.tx2 = {
            "id": "T2",
            "operations": [
                {"node": "N2", "operation": "read", "data": "A"}
            ],
            "dependencies": ["T1"]
        }
        self.tx3 = {
            "id": "T3",
            "operations": [
                {"node": "N1", "operation": "write", "data": "B"},
                {"node": "N2", "operation": "write", "data": "C"}
            ],
            "dependencies": ["T1"]
        }
        self.tx4 = {
            "id": "T4",
            "operations": [
                {"node": "N3", "operation": "read", "data": "B"}
            ],
            "dependencies": ["T3"]
        }
        self.sample_transactions = [self.tx1, self.tx2, self.tx3, self.tx4]

    def test_build_dependency_graph(self):
        # Test that the dependency graph is built correctly.
        # Expected graph is a dictionary mapping a transaction id to a list of transactions that depend on it.
        graph = build_dependency_graph(self.sample_transactions)
        expected_graph = {
            "T1": ["T2", "T3"],
            "T2": [],
            "T3": ["T4"],
            "T4": []
        }
        self.assertEqual(graph, expected_graph)

    def test_order_transactions(self):
        # Test that the transaction ordering respects the dependencies.
        order = order_transactions(self.sample_transactions)
        # T1 must come before T2 and T3, and T3 must come before T4.
        self.assertTrue(order.index("T1") < order.index("T2"))
        self.assertTrue(order.index("T1") < order.index("T3"))
        self.assertTrue(order.index("T3") < order.index("T4"))
        # Ensure all transaction ids are present.
        self.assertEqual(set(order), {"T1", "T2", "T3", "T4"})

    def dummy_vote_func_success(self, transaction):
        # Dummy voting function that always returns True (all nodes vote for commit).
        return True

    def dummy_vote_func_failure(self, transaction):
        # Dummy voting function that returns False if any operation is performed on node "N2".
        for op in transaction["operations"]:
            if op["node"] == "N2":
                return False
        return True

    def test_commit_protocol_success(self):
        # Test commit protocol when all nodes vote for commit.
        result = commit_protocol(self.sample_transactions, self.dummy_vote_func_success)
        # Expect all transactions to be committed.
        expected = {
            "T1": "committed",
            "T2": "committed",
            "T3": "committed",
            "T4": "committed"
        }
        self.assertEqual(result, expected)

    def test_commit_protocol_failure(self):
        # Test commit protocol when nodes vote to abort (e.g. any transaction with an operation on "N2" fails).
        result = commit_protocol(self.sample_transactions, self.dummy_vote_func_failure)
        # Transaction T1 should commit (no operation on N2), others should abort.
        expected = {
            "T1": "committed",
            "T2": "aborted",
            "T3": "aborted",
            "T4": "aborted"
        }
        self.assertEqual(result, expected)

    def test_concurrent_transaction_order(self):
        # Test ordering where transactions have no dependencies; order may be arbitrary.
        txA = {"id": "A", "operations": [{"node": "N1", "operation": "write", "data": "X"}], "dependencies": []}
        txB = {"id": "B", "operations": [{"node": "N2", "operation": "read", "data": "X"}], "dependencies": []}
        txC = {"id": "C", "operations": [{"node": "N1", "operation": "read", "data": "X"}], "dependencies": []}
        transactions = [txA, txB, txC]
        order = order_transactions(transactions)
        # All transaction ids should be present regardless of order.
        self.assertEqual(set(order), {"A", "B", "C"})

    def test_node_locality_priority(self):
        # Test that transactions with operations on fewer nodes are prioritized.
        tx_small = {
            "id": "T_small",
            "operations": [{"node": "N1", "operation": "write", "data": "X"}],
            "dependencies": []
        }
        tx_large = {
            "id": "T_large",
            "operations": [
                {"node": "N1", "operation": "write", "data": "Y"},
                {"node": "N2", "operation": "write", "data": "Z"}
            ],
            "dependencies": []
        }
        transactions = [tx_large, tx_small]
        order = order_transactions(transactions)
        # Expect the transaction with operations at a single node to come first.
        self.assertEqual(order[0], "T_small")

if __name__ == "__main__":
    unittest.main()