import unittest
import threading
import time

from txn_shard import (
    begin_transaction,
    read,
    write,
    delete,
    commit_transaction,
    abort_transaction,
    update_shard_mapping
)

class TestTxnShard(unittest.TestCase):
    def setUp(self):
        # Initialize with an initial shard mapping.
        initial_mapping = {'shard1': 'node1', 'shard2': 'node2'}
        update_shard_mapping(initial_mapping)

    def test_single_transaction_commit(self):
        txn_id = begin_transaction()
        write(txn_id, "key1", 100)
        self.assertEqual(read(txn_id, "key1"), 100)
        commit_success = commit_transaction(txn_id)
        self.assertTrue(commit_success, "Transaction should commit successfully")

        # Start a new transaction to verify the committed value.
        txn_id2 = begin_transaction()
        self.assertEqual(read(txn_id2, "key1"), 100)
        commit_transaction(txn_id2)

    def test_abort_transaction(self):
        txn_id = begin_transaction()
        write(txn_id, "key2", 200)
        # Instead of commit, abort the transaction.
        abort_transaction(txn_id)

        # New transaction should not see the aborted change.
        txn_id2 = begin_transaction()
        self.assertIsNone(read(txn_id2, "key2"))
        commit_transaction(txn_id2)

    def test_delete_operation(self):
        # Write and commit a key.
        txn_id = begin_transaction()
        write(txn_id, "key3", 300)
        commit_transaction(txn_id)

        # Delete the key in a new transaction.
        txn_id2 = begin_transaction()
        self.assertEqual(read(txn_id2, "key3"), 300)
        delete(txn_id2, "key3")
        commit_transaction(txn_id2)

        # Verify that the key is deleted.
        txn_id3 = begin_transaction()
        self.assertIsNone(read(txn_id3, "key3"))
        commit_transaction(txn_id3)

    def test_concurrent_transactions_isolation(self):
        # Initialize key with a known value.
        txn_init = begin_transaction()
        write(txn_init, "key4", 400)
        commit_transaction(txn_init)

        results = []

        def txn_worker(write_value, delay, result_list):
            txn = begin_transaction()
            # Read current value before making changes.
            initial_value = read(txn, "key4")
            time.sleep(delay)
            write(txn, "key4", write_value)
            commit_success = commit_transaction(txn)
            result_list.append((initial_value, write_value, commit_success))

        thread1 = threading.Thread(target=txn_worker, args=(401, 0.2, results))
        thread2 = threading.Thread(target=txn_worker, args=(402, 0.1, results))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Final check: the value should be updated to one of the committed write values.
        txn_final = begin_transaction()
        final_value = read(txn_final, "key4")
        commit_transaction(txn_final)
        self.assertIn(final_value, [401, 402])

    def test_update_shard_mapping(self):
        # Update the shard mapping and process a new transaction.
        new_mapping = {'shard1': 'node2', 'shard3': 'node3'}
        update_shard_mapping(new_mapping)

        txn_id = begin_transaction()
        write(txn_id, "key5", 500)
        commit_transaction(txn_id)

        txn_id2 = begin_transaction()
        self.assertEqual(read(txn_id2, "key5"), 500)
        commit_transaction(txn_id2)

if __name__ == '__main__':
    unittest.main()