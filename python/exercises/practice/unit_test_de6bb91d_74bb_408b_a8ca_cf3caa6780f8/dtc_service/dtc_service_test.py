import unittest
import threading
import time
import uuid
from dtc_service import TransactionCoordinator, ResourceManager

class FakeResourceManager(ResourceManager):
    def __init__(self, rm_id, fail_prepare=False, delay_prepare=0):
        super().__init__(rm_id)
        self.fail_prepare = fail_prepare
        self.delay_prepare = delay_prepare
        # For testing, we maintain a simple in-memory main store and a temp store per transaction
        self.data = {}          # committed data
        self.temp = {}          # transaction_id: {key: value}
        self.prepared = set()   # transaction_ids that have been prepared/committed/rolled back

    def prepare(self, transaction_id):
        if transaction_id in self.prepared:
            # Already processed transaction, idempotent behavior.
            return True
        if self.delay_prepare:
            time.sleep(self.delay_prepare)
        if self.fail_prepare:
            return False
        # If no failure, prepare is successful.
        if transaction_id in self.temp:
            return True
        return True

    def commit(self, transaction_id):
        if transaction_id in self.prepared:
            return
        # Move temp data to committed data store.
        if transaction_id in self.temp:
            for key, value in self.temp[transaction_id].items():
                self.data[key] = value
            del self.temp[transaction_id]
        self.prepared.add(transaction_id)

    def rollback(self, transaction_id):
        if transaction_id in self.prepared:
            return
        if transaction_id in self.temp:
            del self.temp[transaction_id]
        self.prepared.add(transaction_id)

    def write(self, transaction_id, key, value):
        # Record the write in temporary store associated with the transaction.
        if transaction_id in self.temp:
            # Prevent duplicate writes for the same key in the same transaction.
            if key in self.temp[transaction_id]:
                return False
        else:
            self.temp[transaction_id] = {}
        self.temp[transaction_id][key] = value
        return True

class TestDistributedTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        # Create a TransactionCoordinator instance.
        self.tc = TransactionCoordinator()
        # Create two resource managers that always succeed.
        self.rm1 = FakeResourceManager("rm1")
        self.rm2 = FakeResourceManager("rm2")
        self.tc.register_rm(self.rm1)
        self.tc.register_rm(self.rm2)

    def test_begin_transaction_returns_unique_id(self):
        transaction_id1 = self.tc.begin_transaction()
        transaction_id2 = self.tc.begin_transaction()
        self.assertIsNotNone(transaction_id1)
        self.assertIsNotNone(transaction_id2)
        self.assertNotEqual(transaction_id1, transaction_id2)

    def test_successful_commit(self):
        transaction_id = self.tc.begin_transaction()
        # Write to both resource managers.
        res1 = self.tc.write(transaction_id, "rm1", "key1", "value1")
        res2 = self.tc.write(transaction_id, "rm2", "key2", "value2")
        self.assertTrue(res1)
        self.assertTrue(res2)
        
        # Trigger prepare phase.
        prepare_success = self.tc.prepare_transaction(transaction_id)
        self.assertTrue(prepare_success)
        
        # Commit transaction.
        self.tc.commit_transaction(transaction_id)
        # Verify the committed data in RMs.
        self.assertEqual(self.rm1.data.get("key1"), "value1")
        self.assertEqual(self.rm2.data.get("key2"), "value2")

    def test_prepare_failure_in_transaction(self):
        # Create an RM that fails during prepare phase.
        failing_rm = FakeResourceManager("rm_fail", fail_prepare=True)
        self.tc.register_rm(failing_rm)
        
        transaction_id = self.tc.begin_transaction()
        # Successful writes for rm1 and failing_rm.
        self.assertTrue(self.tc.write(transaction_id, "rm1", "key1", "value1"))
        self.assertTrue(self.tc.write(transaction_id, "rm_fail", "key_fail", "value_fail"))
        
        # Prepare should fail due to failing_rm.
        prepare_success = self.tc.prepare_transaction(transaction_id)
        self.assertFalse(prepare_success)
        
        # TC should rollback after failed prepare.
        self.tc.rollback_transaction(transaction_id)
        self.assertNotIn("key1", self.rm1.data)
        self.assertNotIn("key_fail", failing_rm.data)

    def test_idempotent_commit(self):
        transaction_id = self.tc.begin_transaction()
        self.tc.write(transaction_id, "rm1", "key1", "value1")
        self.tc.write(transaction_id, "rm2", "key2", "value2")
        
        prepare_success = self.tc.prepare_transaction(transaction_id)
        self.assertTrue(prepare_success)
        
        # First commit.
        self.tc.commit_transaction(transaction_id)
        data_rm1_first = self.rm1.data.get("key1")
        data_rm2_first = self.rm2.data.get("key2")
        
        # Second commit (should be idempotent, no change or error).
        self.tc.commit_transaction(transaction_id)
        data_rm1_second = self.rm1.data.get("key1")
        data_rm2_second = self.rm2.data.get("key2")

        self.assertEqual(data_rm1_first, "value1")
        self.assertEqual(data_rm2_first, "value2")
        self.assertEqual(data_rm1_second, "value1")
        self.assertEqual(data_rm2_second, "value2")

    def test_idempotent_rollback(self):
        transaction_id = self.tc.begin_transaction()
        self.tc.write(transaction_id, "rm1", "key1", "value1")
        self.tc.write(transaction_id, "rm2", "key2", "value2")
        
        # Suppose prepare fails, leading to rollback.
        self.tc.rollback_transaction(transaction_id)
        # First rollback.
        self.assertNotIn("key1", self.rm1.data)
        self.assertNotIn("key2", self.rm2.data)
        # Second rollback (should be idempotent).
        self.tc.rollback_transaction(transaction_id)
        self.assertNotIn("key1", self.rm1.data)
        self.assertNotIn("key2", self.rm2.data)

    def test_concurrent_transactions(self):
        def transaction_worker(tc, rm_id, key, value, results, index):
            tid = tc.begin_transaction()
            result_write = tc.write(tid, rm_id, key, value)
            prepare_success = tc.prepare_transaction(tid)
            if prepare_success:
                tc.commit_transaction(tid)
                results[index] = True
            else:
                tc.rollback_transaction(tid)
                results[index] = False
        
        num_threads = 10
        results = [None] * num_threads
        threads = []
        keys = [f"key_{i}" for i in range(num_threads)]
        values = [f"value_{i}" for i in range(num_threads)]
        for i in range(num_threads):
            t = threading.Thread(target=transaction_worker, args=(self.tc, "rm1", keys[i], values[i], results, i))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All transactions should have succeeded.
        self.assertTrue(all(results))
        # Verify committed data.
        for i in range(num_threads):
            self.assertEqual(self.rm1.data.get(keys[i]), values[i])

    def test_resource_manager_timeout(self):
        # Create an RM that delays its prepare beyond timeout.
        slow_rm = FakeResourceManager("rm_slow", delay_prepare=1.5)
        self.tc.register_rm(slow_rm)
        
        transaction_id = self.tc.begin_transaction()
        self.tc.write(transaction_id, "rm1", "key1", "value1")
        self.tc.write(transaction_id, "rm_slow", "slow_key", "slow_value")
        
        # Prepare phase should timeout and thus fail.
        prepare_success = self.tc.prepare_transaction(transaction_id)
        self.assertFalse(prepare_success)
        # Rollback
        self.tc.rollback_transaction(transaction_id)
        # Ensure no data has been committed.
        self.assertNotIn("key1", self.rm1.data)
        self.assertNotIn("slow_key", slow_rm.data)

if __name__ == '__main__':
    unittest.main()