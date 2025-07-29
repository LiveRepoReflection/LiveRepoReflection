import unittest
from threading import Thread
import time

# Import the coordinator from decentralized_tx module.
from decentralized_tx import DistributedTxCoordinator

class MockDataNode:
    def __init__(self, node_id, fail_on_prepare=False, fail_on_commit=False, delay=0):
        self.node_id = node_id
        self.prepared = False
        self.fail_on_prepare = fail_on_prepare
        self.fail_on_commit = fail_on_commit
        self.delay = delay  # simulate network or processing delay

    def prepare(self, transaction_id, operations):
        if self.delay:
            time.sleep(self.delay)
        if self.fail_on_prepare:
            return False, "Prepare failed on node {}".format(self.node_id)
        self.prepared = True
        return True, ""

    def commit(self, transaction_id):
        if self.delay:
            time.sleep(self.delay)
        if not self.prepared:
            return False, "Transaction {} not prepared on node {}".format(transaction_id, self.node_id)
        if self.fail_on_commit:
            return False, "Commit failed on node {}".format(self.node_id)
        return True, ""

    def rollback(self, transaction_id):
        # Simulate rollback delay if specified.
        if self.delay:
            time.sleep(self.delay)
        self.prepared = False
        return True, ""


class TestDistributedTxCoordinator(unittest.TestCase):

    def test_successful_transaction(self):
        # All nodes succeed in prepare and commit.
        node1 = MockDataNode("node1")
        node2 = MockDataNode("node2")
        nodes = [node1, node2]
        # transactions: mapping of node id to its list of operations.
        transactions = {
            "node1": [("key1", "value1", "write")],
            "node2": [("key2", "value2", "write")]
        }
        coordinator = DistributedTxCoordinator()
        result = coordinator.run_transaction("tx1", nodes, transactions)
        self.assertEqual(result["status"], "committed")
        self.assertNotIn("failed_node", result)

    def test_prepare_failure(self):
        # One node fails during prepare, so transaction should rollback.
        node1 = MockDataNode("node1", fail_on_prepare=True)
        node2 = MockDataNode("node2")
        nodes = [node1, node2]
        transactions = {
            "node1": [("key1", "value1", "write")],
            "node2": [("key2", "value2", "write")]
        }
        coordinator = DistributedTxCoordinator()
        result = coordinator.run_transaction("tx2", nodes, transactions)
        self.assertEqual(result["status"], "rolledback")
        self.assertEqual(result["failed_node"], "node1")

    def test_commit_failure(self):
        # Prepare succeeds in all nodes but one fails during commit.
        node1 = MockDataNode("node1")
        node2 = MockDataNode("node2", fail_on_commit=True)
        nodes = [node1, node2]
        transactions = {
            "node1": [("keyA", "valueA", "update")],
            "node2": [("keyB", "valueB", "delete")]
        }
        coordinator = DistributedTxCoordinator()
        result = coordinator.run_transaction("tx3", nodes, transactions)
        self.assertEqual(result["status"], "rolledback")
        self.assertEqual(result["failed_node"], "node2")

    def test_concurrent_transactions(self):
        # Run two transactions concurrently to test isolation and concurrency.
        node1 = MockDataNode("node1")
        node2 = MockDataNode("node2")
        coordinator = DistributedTxCoordinator()
        
        def run_tx(tx_id, operations, results):
            res = coordinator.run_transaction(tx_id, [node1, node2], operations)
            results[tx_id] = res

        transactions_tx4 = {
            "node1": [("key1", "val1", "write")],
            "node2": [("key2", "val2", "write")]
        }
        transactions_tx5 = {
            "node1": [("key3", "val3", "write")],
            "node2": [("key4", "val4", "write")]
        }

        results = {}
        thread1 = Thread(target=run_tx, args=("tx4", transactions_tx4, results))
        thread2 = Thread(target=run_tx, args=("tx5", transactions_tx5, results))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Both transactions should commit successfully.
        self.assertEqual(results["tx4"]["status"], "committed")
        self.assertEqual(results["tx5"]["status"], "committed")

    def test_network_delay_handling(self):
        # Simulate nodes with delays to test timeout and recovery.
        node1 = MockDataNode("node1", delay=0.5)
        node2 = MockDataNode("node2", delay=0.5)
        nodes = [node1, node2]
        transactions = {
            "node1": [("key1", "valueDelayed", "write")],
            "node2": [("key2", "valueDelayed", "write")]
        }
        coordinator = DistributedTxCoordinator(timeout=2)  # set a timeout parameter if supported
        result = coordinator.run_transaction("tx6", nodes, transactions)
        self.assertEqual(result["status"], "committed")

    def test_deadlock_simulation(self):
        # Simulate a scenario that might lead to deadlock. For this unit test,
        # we assume that the coordinator implements a deadlock prevention or detection mechanism.
        # We simulate two nodes and two transactions that attempt to lock resources in opposite order.
        node1 = MockDataNode("node1")
        node2 = MockDataNode("node2")
        coordinator = DistributedTxCoordinator()
        
        transactions_tx7 = {
            "node1": [("keyX", "valueX", "write")],
            "node2": [("keyY", "valueY", "write")]
        }
        transactions_tx8 = {
            "node2": [("keyX", "valueX2", "write")],
            "node1": [("keyY", "valueY2", "write")]
        }
        
        results = {}
        def run_tx(tx_id, ops, res_dict):
            outcome = coordinator.run_transaction(tx_id, [node1, node2], ops)
            res_dict[tx_id] = outcome

        thread1 = Thread(target=run_tx, args=("tx7", transactions_tx7, results))
        thread2 = Thread(target=run_tx, args=("tx8", transactions_tx8, results))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        # At least one transaction should commit, and the other might be rolled back to resolve deadlock.
        statuses = {results["tx7"]["status"], results["tx8"]["status"]}
        self.assertTrue("committed" in statuses)
        self.assertTrue("rolledback" in statuses or statuses == {"committed"})

    def test_node_failure_recovery(self):
        # Simulate recovery: a node fails during commit and then recovers.
        # The coordinator should eventually mark the transaction as rolled back on failure.
        node1 = MockDataNode("node1", fail_on_commit=True)
        node2 = MockDataNode("node2")
        nodes = [node1, node2]
        transactions = {
            "node1": [("keyRecover", "valueBefore", "update")],
            "node2": [("keyRecover", "valueBefore", "update")]
        }
        coordinator = DistributedTxCoordinator()
        result = coordinator.run_transaction("tx9", nodes, transactions)
        self.assertEqual(result["status"], "rolledback")
        self.assertEqual(result["failed_node"], "node1")
        
        # Simulate node1 recovery by resetting its failure condition.
        node1.fail_on_commit = False
        # Retry the transaction.
        result_retry = coordinator.run_transaction("tx10", nodes, transactions)
        self.assertEqual(result_retry["status"], "committed")

if __name__ == '__main__':
    unittest.main()