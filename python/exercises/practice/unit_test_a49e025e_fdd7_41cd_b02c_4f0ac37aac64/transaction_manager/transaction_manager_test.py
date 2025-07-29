import unittest
import threading
from transaction_manager import TransactionManager

class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self.tm = TransactionManager()

    def test_begin_transaction(self):
        self.assertTrue(self.tm.begin_transaction(1))
        self.assertFalse(self.tm.begin_transaction(1))  # Duplicate
        self.assertTrue(self.tm.begin_transaction(2))

    def test_register_participant(self):
        self.tm.begin_transaction(1)
        self.assertTrue(self.tm.register_participant(1, 101))
        self.assertFalse(self.tm.register_participant(1, 101))  # Duplicate
        self.assertFalse(self.tm.register_participant(2, 101))  # Non-existent tx

    def test_service_commit(self):
        self.tm.begin_transaction(1)
        self.tm.register_participant(1, 101)
        self.tm.register_participant(1, 102)
        
        self.assertTrue(self.tm.service_commit(1, 101))
        self.assertEqual(self.tm.get_transaction_status(1), "PENDING")
        
        self.assertTrue(self.tm.service_commit(1, 102))
        self.assertEqual(self.tm.get_transaction_status(1), "COMMITTED")

    def test_service_rollback(self):
        self.tm.begin_transaction(1)
        self.tm.register_participant(1, 101)
        self.tm.register_participant(1, 102)
        
        self.assertTrue(self.tm.service_rollback(1, 101))
        self.assertEqual(self.tm.get_transaction_status(1), "ROLLED_BACK")
        self.assertFalse(self.tm.service_commit(1, 102))  # Already rolled back

    def test_concurrent_operations(self):
        results = []
        
        def worker(tx_id, service_id, action):
            if action == 'begin':
                results.append(self.tm.begin_transaction(tx_id))
            elif action == 'register':
                results.append(self.tm.register_participant(tx_id, service_id))
            elif action == 'commit':
                results.append(self.tm.service_commit(tx_id, service_id))
            elif action == 'rollback':
                results.append(self.tm.service_rollback(tx_id, service_id))
        
        threads = []
        threads.append(threading.Thread(target=worker, args=(1, 101, 'begin')))
        threads.append(threading.Thread(target=worker, args=(1, 101, 'register')))
        threads.append(threading.Thread(target=worker, args=(1, 101, 'commit')))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertEqual(results, [True, True, True])
        self.assertEqual(self.tm.get_transaction_status(1), "COMMITTED")

    def test_edge_cases(self):
        # Non-existent transaction
        self.assertEqual(self.tm.get_transaction_status(999), "NON_EXISTENT")
        self.assertFalse(self.tm.service_commit(999, 101))
        self.assertFalse(self.tm.service_rollback(999, 101))
        
        # Commit before registration
        self.tm.begin_transaction(1)
        self.assertFalse(self.tm.service_commit(1, 101))
        
        # Register after commit
        self.tm.begin_transaction(2)
        self.tm.register_participant(2, 201)
        self.assertTrue(self.tm.service_commit(2, 201))
        self.assertFalse(self.tm.register_participant(2, 202))

    def test_multiple_participants(self):
        self.tm.begin_transaction(1)
        for i in range(100, 110):
            self.tm.register_participant(1, i)
        
        # Some commit, some rollback
        for i in range(100, 105):
            self.assertTrue(self.tm.service_commit(1, i))
        self.assertTrue(self.tm.service_rollback(1, 105))
        
        self.assertEqual(self.tm.get_transaction_status(1), "ROLLED_BACK")
        
        # Verify no further operations allowed
        self.assertFalse(self.tm.service_commit(1, 106))
        self.assertFalse(self.tm.register_participant(1, 111))

if __name__ == '__main__':
    unittest.main()