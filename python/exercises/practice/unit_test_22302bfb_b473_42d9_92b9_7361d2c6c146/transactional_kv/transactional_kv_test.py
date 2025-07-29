import unittest
from transactional_kv import begin_transaction, read, write, commit_transaction, rollback_transaction

class TestTransactionalKVStore(unittest.TestCase):
    def setUp(self):
        # Reset state before each test if needed.
        # This assumes that the module provides a way to clear the store.
        # If not provided, you might need to simulate by creating independent instances.
        # For this test, we assume the store is reset at the start of testing.
        pass

    def test_single_transaction_commit(self):
        # Start a transaction and commit a write; then start a new transaction to see the committed value.
        tx1 = begin_transaction()
        write(tx1, "key1", "value1")
        self.assertTrue(commit_transaction(tx1))
        
        tx2 = begin_transaction()
        # Read should see the committed value from tx1
        self.assertEqual(read(tx2, "key1"), "value1")
        # No changes in tx2 if not modified
        commit_transaction(tx2)

    def test_single_transaction_rollback(self):
        # Start a transaction, write a value, then rollback.
        tx1 = begin_transaction()
        write(tx1, "key2", "value2")
        rollback_transaction(tx1)
        
        tx2 = begin_transaction()
        # Since tx1 rolled back, key2 should not be found.
        self.assertIsNone(read(tx2, "key2"))
        commit_transaction(tx2)

    def test_snapshot_isolation(self):
        # Transaction T1 begins then T2 commits an update.
        tx1 = begin_transaction()
        # Initially, key3 doesn't exist, tx1 sees None.
        self.assertIsNone(read(tx1, "key3"))
        
        # Start another transaction to update key3.
        tx2 = begin_transaction()
        write(tx2, "key3", "value3")
        self.assertTrue(commit_transaction(tx2))
        
        # T1, operating on its snapshot, should still see None.
        self.assertIsNone(read(tx1, "key3"))
        commit_transaction(tx1)

        # New transaction should see the updated value.
        tx3 = begin_transaction()
        self.assertEqual(read(tx3, "key3"), "value3")
        commit_transaction(tx3)

    def test_multiple_writes_in_single_transaction(self):
        tx1 = begin_transaction()
        write(tx1, "key4", "init")
        self.assertEqual(read(tx1, "key4"), "init")
        write(tx1, "key4", "updated")
        self.assertEqual(read(tx1, "key4"), "updated")
        self.assertTrue(commit_transaction(tx1))
        
        tx2 = begin_transaction()
        self.assertEqual(read(tx2, "key4"), "updated")
        commit_transaction(tx2)

    def test_conflicting_writes(self):
        # Two transactions try to write to the same key concurrently.
        # The store should detect conflicts at commit.
        tx1 = begin_transaction()
        tx2 = begin_transaction()
        
        # Both transactions read initial value of key5 (which is None).
        self.assertIsNone(read(tx1, "key5"))
        self.assertIsNone(read(tx2, "key5"))
        
        # Both perform their writes.
        write(tx1, "key5", "value_tx1")
        write(tx2, "key5", "value_tx2")
        
        # Commit tx1 first should succeed.
        self.assertTrue(commit_transaction(tx1))
        # Now commit tx2 should detect conflict and fail.
        self.assertFalse(commit_transaction(tx2))
        
        # New transaction should reflect tx1's committed value.
        tx3 = begin_transaction()
        self.assertEqual(read(tx3, "key5"), "value_tx1")
        commit_transaction(tx3)

    def test_sequential_conflicts(self):
        # Test that a transaction started after another's commit sees the committed value.
        tx1 = begin_transaction()
        write(tx1, "key6", "first")
        self.assertTrue(commit_transaction(tx1))
        
        tx2 = begin_transaction()
        # tx2 sees value from tx1.
        self.assertEqual(read(tx2, "key6"), "first")
        write(tx2, "key6", "second")
        self.assertTrue(commit_transaction(tx2))
        
        tx3 = begin_transaction()
        self.assertEqual(read(tx3, "key6"), "second")
        commit_transaction(tx3)

    def test_write_without_read(self):
        # Test that writing to a non-existent key and committing works as expected.
        tx1 = begin_transaction()
        write(tx1, "key7", "value7")
        self.assertIsNone(read(tx1, "non_existent"))
        self.assertTrue(commit_transaction(tx1))
        
        tx2 = begin_transaction()
        self.assertEqual(read(tx2, "key7"), "value7")
        commit_transaction(tx2)

    def test_rollback_after_multiple_operations(self):
        # Test that a rollback undoes multiple writes in the same transaction.
        tx1 = begin_transaction()
        write(tx1, "key8", "first")
        write(tx1, "key9", "second")
        self.assertEqual(read(tx1, "key8"), "first")
        self.assertEqual(read(tx1, "key9"), "second")
        rollback_transaction(tx1)
        
        tx2 = begin_transaction()
        self.assertIsNone(read(tx2, "key8"))
        self.assertIsNone(read(tx2, "key9"))
        commit_transaction(tx2)

if __name__ == '__main__':
    unittest.main()