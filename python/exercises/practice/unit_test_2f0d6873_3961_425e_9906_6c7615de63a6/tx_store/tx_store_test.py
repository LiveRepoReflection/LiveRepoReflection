import unittest
from tx_store import KeyValueStore

class KeyValueStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()

    def test_basic_transaction(self):
        tx_id = self.store.begin_transaction("client1")
        self.store.put(tx_id, "key1", "value1")
        self.assertEqual(self.store.get(tx_id, "key1"), "value1")
        self.store.commit_transaction(tx_id)
        
        tx_id2 = self.store.begin_transaction("client1")
        self.assertEqual(self.store.get(tx_id2, "key1"), "value1")
        self.store.rollback_transaction(tx_id2)

    def test_transaction_isolation(self):
        tx1_id = self.store.begin_transaction("client1")
        tx2_id = self.store.begin_transaction("client2")
        
        self.store.put(tx1_id, "x", "1")
        self.store.put(tx2_id, "x", "2")
        
        # Each transaction should see its own changes
        self.assertEqual(self.store.get(tx1_id, "x"), "1")
        self.assertEqual(self.store.get(tx2_id, "x"), "2")
        
        # Commit first transaction
        self.store.commit_transaction(tx1_id)
        
        # Second transaction should still see its own version
        self.assertEqual(self.store.get(tx2_id, "x"), "2")
        
        # Commit second transaction
        self.store.commit_transaction(tx2_id)
        
        # New transaction should see the latest committed value
        tx3_id = self.store.begin_transaction("client3")
        self.assertEqual(self.store.get(tx3_id, "x"), "2")
        self.store.rollback_transaction(tx3_id)

    def test_rollback(self):
        tx_id = self.store.begin_transaction("client1")
        self.store.put(tx_id, "key1", "value1")
        self.assertEqual(self.store.get(tx_id, "key1"), "value1")
        self.store.rollback_transaction(tx_id)
        
        # After rollback, new transaction should not see the changes
        tx_id2 = self.store.begin_transaction("client1")
        self.assertIsNone(self.store.get(tx_id2, "key1"))
        self.store.rollback_transaction(tx_id2)

    def test_non_existent_key(self):
        tx_id = self.store.begin_transaction("client1")
        self.assertIsNone(self.store.get(tx_id, "non_existent_key"))
        self.store.rollback_transaction(tx_id)

    def test_multiple_operations_within_transaction(self):
        tx_id = self.store.begin_transaction("client1")
        
        # Perform multiple operations
        self.store.put(tx_id, "key1", "value1")
        self.store.put(tx_id, "key2", "value2")
        self.store.put(tx_id, "key1", "updated_value1")  # Update existing key
        
        # Verify all operations within the transaction
        self.assertEqual(self.store.get(tx_id, "key1"), "updated_value1")
        self.assertEqual(self.store.get(tx_id, "key2"), "value2")
        
        self.store.commit_transaction(tx_id)
        
        # New transaction should see committed changes
        tx_id2 = self.store.begin_transaction("client1")
        self.assertEqual(self.store.get(tx_id2, "key1"), "updated_value1")
        self.assertEqual(self.store.get(tx_id2, "key2"), "value2")
        self.store.rollback_transaction(tx_id2)

    def test_client_with_multiple_sequential_transactions(self):
        # First transaction
        tx1_id = self.store.begin_transaction("client1")
        self.store.put(tx1_id, "key1", "value1")
        self.store.commit_transaction(tx1_id)
        
        # Second transaction by the same client
        tx2_id = self.store.begin_transaction("client1")
        self.assertEqual(self.store.get(tx2_id, "key1"), "value1")
        self.store.put(tx2_id, "key1", "updated_by_tx2")
        self.store.commit_transaction(tx2_id)
        
        # Third transaction by the same client
        tx3_id = self.store.begin_transaction("client1")
        self.assertEqual(self.store.get(tx3_id, "key1"), "updated_by_tx2")
        self.store.rollback_transaction(tx3_id)

    def test_client_cannot_have_multiple_active_transactions(self):
        tx1_id = self.store.begin_transaction("client1")
        with self.assertRaises(Exception):
            self.store.begin_transaction("client1")
        self.store.rollback_transaction(tx1_id)

    def test_invalid_transaction_operations(self):
        # Try to use a non-existent transaction ID
        with self.assertRaises(Exception):
            self.store.get("invalid_tx_id", "key1")
        
        with self.assertRaises(Exception):
            self.store.put("invalid_tx_id", "key1", "value1")
        
        with self.assertRaises(Exception):
            self.store.commit_transaction("invalid_tx_id")
        
        with self.assertRaises(Exception):
            self.store.rollback_transaction("invalid_tx_id")

    def test_commit_or_rollback_same_transaction_twice(self):
        tx_id = self.store.begin_transaction("client1")
        self.store.commit_transaction(tx_id)
        
        # Cannot commit an already committed transaction
        with self.assertRaises(Exception):
            self.store.commit_transaction(tx_id)
        
        tx_id = self.store.begin_transaction("client2")
        self.store.rollback_transaction(tx_id)
        
        # Cannot rollback an already rolled back transaction
        with self.assertRaises(Exception):
            self.store.rollback_transaction(tx_id)

    def test_complex_scenario(self):
        # Client 1 starts a transaction
        tx1_id = self.store.begin_transaction("client1")
        self.store.put(tx1_id, "shared_key", "client1_value")
        
        # Client 2 starts a transaction
        tx2_id = self.store.begin_transaction("client2")
        self.store.put(tx2_id, "shared_key", "client2_value")
        
        # Client 3 starts a transaction
        tx3_id = self.store.begin_transaction("client3")
        self.store.put(tx3_id, "unique_key", "client3_value")
        
        # Each client sees their own changes
        self.assertEqual(self.store.get(tx1_id, "shared_key"), "client1_value")
        self.assertEqual(self.store.get(tx2_id, "shared_key"), "client2_value")
        self.assertIsNone(self.store.get(tx3_id, "shared_key"))  # Not set in tx3
        self.assertEqual(self.store.get(tx3_id, "unique_key"), "client3_value")
        
        # Client 1 commits
        self.store.commit_transaction(tx1_id)
        
        # Client 3 now sees Client 1's committed value for shared_key
        self.assertEqual(self.store.get(tx3_id, "shared_key"), "client1_value")
        
        # Client 2 still sees its own uncommitted value
        self.assertEqual(self.store.get(tx2_id, "shared_key"), "client2_value")
        
        # Client 2 commits
        self.store.commit_transaction(tx2_id)
        
        # Client 3 now sees Client 2's value (latest commit)
        self.assertEqual(self.store.get(tx3_id, "shared_key"), "client2_value")
        
        # Client 3 commits
        self.store.commit_transaction(tx3_id)
        
        # New transaction should see the merged state
        tx4_id = self.store.begin_transaction("client4")
        self.assertEqual(self.store.get(tx4_id, "shared_key"), "client2_value")
        self.assertEqual(self.store.get(tx4_id, "unique_key"), "client3_value")
        self.store.rollback_transaction(tx4_id)

if __name__ == '__main__':
    unittest.main()