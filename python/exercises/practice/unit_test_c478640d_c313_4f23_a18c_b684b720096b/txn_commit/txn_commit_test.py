import unittest
import time
from threading import Thread

# For the purpose of testing, we assume that the txn_commit module provides a class named TransactionProcessor
# with the following methods:
# - process_transaction(transaction): processes a transaction and returns a dictionary mapping node IDs to outcomes ("COMMIT" or "ABORT")
# - simulate_failure(node_id): simulates failure on the given node.
# - recover_node(node_id): recovers the given node after failure.
# - simulate_delay(node_id, delay): simulates a network delay for a specific node's response.
#
# The TransactionProcessor is assumed to handle the asynchronous message passing, failure recovery,
# and timeout mechanisms as required by the two-phase commit protocol.

from txn_commit import TransactionProcessor

class TestTransactionCommitProtocol(unittest.TestCase):
    def setUp(self):
        # Create a new TransactionProcessor instance for each test
        self.tp = TransactionProcessor()

    def test_successful_commit(self):
        transaction = {
            "coordinator": 1,
            "participants": [2, 3, 4],
            "txn_id": "txn_001",
            "data": {"update": "value"}
        }
        result = self.tp.process_transaction(transaction)
        # Verify that all involved nodes report a COMMIT outcome.
        for node in [1, 2, 3, 4]:
            self.assertEqual(result.get(node), "COMMIT", f"Node {node} did not commit successfully.")

    def test_abort_on_node_failure(self):
        # Simulate a failure in one participant node causing the transaction to abort.
        transaction = {
            "coordinator": 10,
            "participants": [20, 30, 40],
            "txn_id": "txn_002",
            "data": {"update": "data"}
        }
        # Introduce a failure on node 30 before processing the transaction.
        self.tp.simulate_failure(30)
        result = self.tp.process_transaction(transaction)
        # All nodes should reflect an ABORT outcome.
        for node in [10, 20, 30, 40]:
            self.assertEqual(result.get(node), "ABORT", f"Node {node} did not abort as expected due to failure.")
        # Recover the failed node after the test.
        self.tp.recover_node(30)

    def test_timeout_during_commit(self):
        # Simulate a delay that causes a timeout for one participant, leading to an ABORT.
        transaction = {
            "coordinator": 100,
            "participants": [200, 300],
            "txn_id": "txn_003",
            "data": {"change": "new"}
        }
        # Simulate a network delay on participant 200 that exceeds the timeout threshold.
        self.tp.simulate_delay(200, delay=5)
        result = self.tp.process_transaction(transaction)
        for node in [100, 200, 300]:
            self.assertEqual(result.get(node), "ABORT", f"Node {node} outcome should be ABORT due to timeout delay.")

    def test_concurrent_transactions(self):
        # Process multiple transactions concurrently and check for consistent outcomes.
        transactions = [
            {
                "coordinator": 1,
                "participants": [2, 3],
                "txn_id": "txn_004",
                "data": {"value": "a"}
            },
            {
                "coordinator": 4,
                "participants": [5, 6],
                "txn_id": "txn_005",
                "data": {"value": "b"}
            },
            {
                "coordinator": 7,
                "participants": [8, 9],
                "txn_id": "txn_006",
                "data": {"value": "c"}
            }
        ]
        results = {}

        def process(txn):
            txn_result = self.tp.process_transaction(txn)
            results[txn["txn_id"]] = txn_result

        threads = []
        for txn in transactions:
            t = Thread(target=process, args=(txn,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for txn in transactions:
            involved_nodes = [txn["coordinator"]] + txn["participants"]
            for node in involved_nodes:
                self.assertEqual(results[txn["txn_id"]].get(node), "COMMIT",
                                 f"Transaction {txn['txn_id']} on node {node} did not commit successfully.")

if __name__ == '__main__':
    unittest.main()