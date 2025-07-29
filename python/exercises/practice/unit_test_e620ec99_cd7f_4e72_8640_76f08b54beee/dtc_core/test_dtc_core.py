import unittest
from unittest.mock import Mock, patch
from threading import Thread
import time

class TestDTC(unittest.TestCase):
    def setUp(self):
        from dtc_core import DistributedTransactionCoordinator
        self.dtc = DistributedTransactionCoordinator()

    def test_begin_transaction_returns_unique_txid(self):
        txid1 = self.dtc.begin_transaction()
        txid2 = self.dtc.begin_transaction()
        self.assertNotEqual(txid1, txid2)
        self.assertTrue(isinstance(txid1, str))
        self.assertTrue(isinstance(txid2, str))

    def test_register_participant(self):
        txid = self.dtc.begin_transaction()
        prepare_mock = Mock()
        commit_rollback_mock = Mock()
        
        self.dtc.register_participant(txid, prepare_mock, commit_rollback_mock)
        self.assertEqual(len(self.dtc.get_participants(txid)), 1)

    def test_invalid_txid_registration(self):
        prepare_mock = Mock()
        commit_rollback_mock = Mock()
        
        with self.assertRaises(ValueError):
            self.dtc.register_participant("invalid_txid", prepare_mock, commit_rollback_mock)

    def test_successful_commit(self):
        txid = self.dtc.begin_transaction()
        
        prepare_mock = Mock(return_value=True)
        commit_mock = Mock(return_value=True)
        
        self.dtc.register_participant(txid, prepare_mock, commit_mock)
        result = self.dtc.commit_transaction(txid)
        
        self.assertEqual(result, "committed")
        prepare_mock.assert_called_once()
        commit_mock.assert_called_once_with("commit")

    def test_failed_prepare_causes_rollback(self):
        txid = self.dtc.begin_transaction()
        
        prepare_mock = Mock(return_value=False)
        commit_rollback_mock = Mock()
        
        self.dtc.register_participant(txid, prepare_mock, commit_rollback_mock)
        result = self.dtc.commit_transaction(txid)
        
        self.assertEqual(result, "rolled_back")
        prepare_mock.assert_called_once()
        commit_rollback_mock.assert_called_once_with("rollback")

    def test_prepare_timeout_causes_rollback(self):
        txid = self.dtc.begin_transaction()
        
        def slow_prepare():
            time.sleep(2)
            return True
            
        prepare_mock = Mock(side_effect=slow_prepare)
        commit_rollback_mock = Mock()
        
        self.dtc.register_participant(txid, prepare_mock, commit_rollback_mock)
        result = self.dtc.commit_transaction(txid)
        
        self.assertEqual(result, "rolled_back")
        commit_rollback_mock.assert_called_once_with("rollback")

    def test_concurrent_transactions(self):
        txid1 = self.dtc.begin_transaction()
        txid2 = self.dtc.begin_transaction()
        
        prepare_mock1 = Mock(return_value=True)
        commit_mock1 = Mock(return_value=True)
        prepare_mock2 = Mock(return_value=True)
        commit_mock2 = Mock(return_value=True)
        
        self.dtc.register_participant(txid1, prepare_mock1, commit_mock1)
        self.dtc.register_participant(txid2, prepare_mock2, commit_mock2)
        
        def commit_transaction1():
            result = self.dtc.commit_transaction(txid1)
            self.assertEqual(result, "committed")
            
        def commit_transaction2():
            result = self.dtc.commit_transaction(txid2)
            self.assertEqual(result, "committed")
            
        thread1 = Thread(target=commit_transaction1)
        thread2 = Thread(target=commit_transaction2)
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        prepare_mock1.assert_called_once()
        commit_mock1.assert_called_once_with("commit")
        prepare_mock2.assert_called_once()
        commit_mock2.assert_called_once_with("commit")

    def test_idempotency(self):
        txid = self.dtc.begin_transaction()
        
        prepare_mock = Mock(return_value=True)
        commit_mock = Mock(return_value=True)
        
        self.dtc.register_participant(txid, prepare_mock, commit_mock)
        
        # First commit
        result1 = self.dtc.commit_transaction(txid)
        self.assertEqual(result1, "committed")
        
        # Second commit of same transaction
        result2 = self.dtc.commit_transaction(txid)
        self.assertEqual(result2, "committed")
        
        # Prepare and commit should only be called once
        prepare_mock.assert_called_once()
        self.assertEqual(commit_mock.call_count, 1)

    def test_participant_exception_handling(self):
        txid = self.dtc.begin_transaction()
        
        prepare_mock = Mock(side_effect=Exception("Prepare failed"))
        commit_rollback_mock = Mock()
        
        self.dtc.register_participant(txid, prepare_mock, commit_rollback_mock)
        result = self.dtc.commit_transaction(txid)
        
        self.assertEqual(result, "rolled_back")
        prepare_mock.assert_called_once()
        commit_rollback_mock.assert_called_once_with("rollback")

    def test_multiple_participants(self):
        txid = self.dtc.begin_transaction()
        
        prepare_mock1 = Mock(return_value=True)
        commit_mock1 = Mock(return_value=True)
        prepare_mock2 = Mock(return_value=True)
        commit_mock2 = Mock(return_value=True)
        prepare_mock3 = Mock(return_value=True)
        commit_mock3 = Mock(return_value=True)
        
        self.dtc.register_participant(txid, prepare_mock1, commit_mock1)
        self.dtc.register_participant(txid, prepare_mock2, commit_mock2)
        self.dtc.register_participant(txid, prepare_mock3, commit_mock3)
        
        result = self.dtc.commit_transaction(txid)
        
        self.assertEqual(result, "committed")
        prepare_mock1.assert_called_once()
        prepare_mock2.assert_called_once()
        prepare_mock3.assert_called_once()
        commit_mock1.assert_called_once_with("commit")
        commit_mock2.assert_called_once_with("commit")
        commit_mock3.assert_called_once_with("commit")

if __name__ == '__main__':
    unittest.main()