import unittest
from threading import Thread
from time import sleep

from kv_transactional import KVStore, TransactionError

class TestKVTransactional(unittest.TestCase):
    def setUp(self):
        # Initialize the KVStore with 5 nodes and a replication factor of 3.
        self.store = KVStore(num_nodes=5, replication_factor=3)

    def test_basic_put_get(self):
        # Test simple put and get operations.
        self.store.put('key1', 'value1')
        value = self.store.get('key1')
        self.assertEqual(value, 'value1')

    def test_transaction_commit(self):
        # Test that a transaction successfully commits changes.
        txn = self.store.begin_transaction()
        txn.put('key2', 'value2')
        txn.put('key3', 123)
        txn.commit()
        self.assertEqual(self.store.get('key2'), 'value2')
        self.assertEqual(self.store.get('key3'), 123)

    def test_transaction_rollback(self):
        # Test that a transaction rollback discards changes.
        txn = self.store.begin_transaction()
        txn.put('key4', 'initial')
        txn.commit()
        txn2 = self.store.begin_transaction()
        txn2.put('key4', 'changed')
        txn2.rollback()
        self.assertEqual(self.store.get('key4'), 'initial')

    def test_conflict_resolution(self):
        # Simulate concurrent transactions updating the same key using vector clocks.
        txn1 = self.store.begin_transaction()
        txn1.put('conflict_key', 'first_value')
        txn1.commit()

        # Simulate an outdated transaction attempting to update the same key.
        txn2 = self.store.begin_transaction()
        # Intentional delay to simulate the vector clock lag.
        sleep(0.1)
        txn2.put('conflict_key', 'second_value')
        try:
            txn2.commit()
        except TransactionError:
            txn2.rollback()
            result = self.store.get('conflict_key')
            # Expect conflict resolution to preserve the initial value if second update fails.
            self.assertEqual(result, 'first_value')
        else:
            # If conflict resolution merges or uses last-write-wins, the value should be one of the two.
            result = self.store.get('conflict_key')
            self.assertIn(result, ['first_value', 'second_value'])

    def test_concurrent_transactions(self):
        # Test multiple concurrent transactions making isolated updates.
        results = {}

        def transaction_worker(key, value):
            txn = self.store.begin_transaction()
            txn.put(key, value)
            txn.commit()
            results[key] = self.store.get(key)

        threads = []
        for i in range(10):
            key = f'concurrent_{i}'
            thread = Thread(target=transaction_worker, args=(key, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for i in range(10):
            self.assertEqual(results[f'concurrent_{i}'], i)

    def test_node_failure_and_replication(self):
        # Insert data and simulate a node failure to test replication and failover.
        self.store.put('fail_key', 'stable_value')
        # Simulate failure of the primary node responsible for 'fail_key'.
        self.store.simulate_node_failure('fail_key')
        sleep(0.1)  # Allow time for failover.
        value = self.store.get('fail_key')
        self.assertEqual(value, 'stable_value')

    def test_max_transaction_size(self):
        # Test the behavior when the transaction exceeds the maximum allowed operations.
        txn = self.store.begin_transaction()
        max_ops = self.store.max_transaction_size()
        for i in range(max_ops):
            txn.put(f'key{i}', i)
        # An extra operation should trigger a TransactionError.
        with self.assertRaises(TransactionError):
            txn.put('excess_key', 'excess')
        txn.rollback()

if __name__ == '__main__':
    unittest.main()