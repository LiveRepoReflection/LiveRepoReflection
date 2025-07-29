import unittest
import threading
import time
from distributed_transactions import TransactionCoordinator, Node

class MockNodeSuccess(Node):
    def __init__(self, node_id, failure_rate=0.0):
        super().__init__(node_id)
        self.failure_rate = failure_rate
        self.prepared = {}
        self.committed = {}
        self.rolled_back = {}
        self.lock = threading.Lock()

    def prepare(self, transaction_id: int) -> bool:
        with self.lock:
            self.prepared[transaction_id] = True
        return True

    def commit(self, transaction_id: int) -> None:
        with self.lock:
            self.committed[transaction_id] = True

    def rollback(self, transaction_id: int) -> None:
        with self.lock:
            self.rolled_back[transaction_id] = True

class MockNodePrepareFail(Node):
    def __init__(self, node_id, failure_rate=0.0):
        super().__init__(node_id)
        self.failure_rate = failure_rate

    def prepare(self, transaction_id: int) -> bool:
        return False

    def commit(self, transaction_id: int) -> None:
        pass

    def rollback(self, transaction_id: int) -> None:
        pass

class MockNodeCommitFail(Node):
    def __init__(self, node_id, failure_rate=0.0):
        super().__init__(node_id)
        self.failure_rate = failure_rate
        self.attempts = {}
        self.lock = threading.Lock()

    def prepare(self, transaction_id: int) -> bool:
        with self.lock:
            self.attempts[transaction_id] = 0
        return True

    def commit(self, transaction_id: int) -> None:
        with self.lock:
            self.attempts[transaction_id] += 1
            if self.attempts[transaction_id] < 3:
                raise Exception("Commit failure")
            # Succeed on third attempt.

    def rollback(self, transaction_id: int) -> None:
        pass

class TestDistributedTransactions(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator(retry_count=3)

    def test_successful_transaction(self):
        nodes = [MockNodeSuccess(i) for i in range(5)]
        for node in nodes:
            self.coordinator.register_node(node)
        tx_id = self.coordinator.begin_transaction()
        result = self.coordinator.end_transaction(tx_id)
        self.assertTrue(result)
        for node in nodes:
            self.assertIn(tx_id, node.committed)
            self.assertIn(tx_id, node.prepared)

    def test_prepare_failure_transaction(self):
        nodes = [MockNodeSuccess(i) for i in range(3)]
        failing_node = MockNodePrepareFail(99)
        nodes.append(failing_node)
        for node in nodes:
            self.coordinator.register_node(node)
        tx_id = self.coordinator.begin_transaction()
        result = self.coordinator.end_transaction(tx_id)
        self.assertFalse(result)
        for node in nodes:
            if isinstance(node, MockNodeSuccess):
                self.assertIn(tx_id, node.rolled_back)

    def test_commit_failure_with_retry(self):
        nodes = [MockNodeSuccess(i) for i in range(2)]
        commit_fail_node = MockNodeCommitFail(100)
        nodes.append(commit_fail_node)
        for node in nodes:
            self.coordinator.register_node(node)
        tx_id = self.coordinator.begin_transaction()
        result = self.coordinator.end_transaction(tx_id)
        self.assertTrue(result)
        for node in nodes:
            if isinstance(node, MockNodeSuccess):
                self.assertIn(tx_id, node.committed)
            elif isinstance(node, MockNodeCommitFail):
                self.assertGreaterEqual(commit_fail_node.attempts.get(tx_id, 0), 3)

    def test_get_node_count(self):
        nodes = [MockNodeSuccess(i) for i in range(3)]
        for node in nodes:
            self.coordinator.register_node(node)
        count = self.coordinator.get_node_count()
        self.assertEqual(count, 3)

    def test_concurrent_transactions(self):
        nodes = [MockNodeSuccess(i) for i in range(10)]
        for node in nodes:
            self.coordinator.register_node(node)
        results = {}
        lock = threading.Lock()

        def run_transaction():
            tx_id = self.coordinator.begin_transaction()
            result = self.coordinator.end_transaction(tx_id)
            with lock:
                results[tx_id] = result

        threads = []
        for _ in range(20):
            t = threading.Thread(target=run_transaction)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 20)
        for tx_id, res in results.items():
            self.assertTrue(res)
            for node in nodes:
                self.assertIn(tx_id, node.committed)

if __name__ == "__main__":
    unittest.main()