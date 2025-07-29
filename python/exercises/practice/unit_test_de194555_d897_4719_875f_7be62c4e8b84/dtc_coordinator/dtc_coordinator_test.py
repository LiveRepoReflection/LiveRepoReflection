import unittest
import threading
from dtc_coordinator import TransactionCoordinator

class SuccessfulParticipant:
    def __init__(self):
        self.prepared = False
        self.committed = False
        self.rolled_back = False

    def prepare(self):
        self.prepared = True
        return True

    def commit(self):
        if not self.prepared:
            return False
        self.committed = True
        return True

    def rollback(self):
        self.rolled_back = True
        return True

class PrepareFailureParticipant:
    def __init__(self):
        self.prepared = False
        self.committed = False
        self.rolled_back = False

    def prepare(self):
        self.prepared = True
        return False

    def commit(self):
        return False

    def rollback(self):
        self.rolled_back = True
        return True

class CommitFailureParticipant:
    def __init__(self):
        self.prepared = False
        self.committed = False
        self.rolled_back = False

    def prepare(self):
        self.prepared = True
        return True

    def commit(self):
        return False

    def rollback(self):
        self.rolled_back = True
        return True

class TransactionCoordinatorThreadSafetyTest(unittest.TestCase):
    def test_concurrent_transactions(self):
        coordinator = TransactionCoordinator()
        num_transactions = 20
        results = []
        lock = threading.Lock()

        def run_transaction():
            txid = coordinator.begin_transaction()
            participant1 = SuccessfulParticipant()
            participant2 = SuccessfulParticipant()
            coordinator.register_participant(txid, participant1)
            coordinator.register_participant(txid, participant2)
            result = coordinator.commit_transaction(txid)
            with lock:
                results.append(result)

        threads = [threading.Thread(target=run_transaction) for _ in range(num_transactions)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(results), num_transactions)
        self.assertTrue(all(results))

class TransactionCoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator()

    def test_begin_transaction_returns_unique_id(self):
        txid1 = self.coordinator.begin_transaction()
        txid2 = self.coordinator.begin_transaction()
        self.assertNotEqual(txid1, txid2)

    def test_commit_successful_transaction(self):
        txid = self.coordinator.begin_transaction()
        participant1 = SuccessfulParticipant()
        participant2 = SuccessfulParticipant()
        self.coordinator.register_participant(txid, participant1)
        self.coordinator.register_participant(txid, participant2)
        commit_result = self.coordinator.commit_transaction(txid)
        self.assertTrue(commit_result)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "COMMITTED")
        self.assertTrue(participant1.committed)
        self.assertTrue(participant2.committed)

    def test_prepare_failure_leads_to_rollback(self):
        txid = self.coordinator.begin_transaction()
        participant1 = SuccessfulParticipant()
        participant2 = PrepareFailureParticipant()
        self.coordinator.register_participant(txid, participant1)
        self.coordinator.register_participant(txid, participant2)
        commit_result = self.coordinator.commit_transaction(txid)
        self.assertFalse(commit_result)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "ABORTED")
        self.assertTrue(participant1.rolled_back)
        self.assertTrue(participant2.rolled_back)

    def test_commit_failure_leads_to_rollback(self):
        txid = self.coordinator.begin_transaction()
        participant1 = SuccessfulParticipant()
        participant2 = CommitFailureParticipant()
        self.coordinator.register_participant(txid, participant1)
        self.coordinator.register_participant(txid, participant2)
        commit_result = self.coordinator.commit_transaction(txid)
        self.assertFalse(commit_result)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "ABORTED")
        self.assertTrue(participant1.rolled_back)
        self.assertTrue(participant2.rolled_back)

    def test_manual_rollback(self):
        txid = self.coordinator.begin_transaction()
        participant1 = SuccessfulParticipant()
        participant2 = SuccessfulParticipant()
        self.coordinator.register_participant(txid, participant1)
        self.coordinator.register_participant(txid, participant2)
        rollback_result = self.coordinator.rollback_transaction(txid)
        self.assertTrue(rollback_result)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "ABORTED")
        self.assertTrue(participant1.rolled_back)
        self.assertTrue(participant2.rolled_back)

    def test_idempotency_of_commit_and_rollback(self):
        txid = self.coordinator.begin_transaction()
        participant = SuccessfulParticipant()
        self.coordinator.register_participant(txid, participant)
        first_commit = self.coordinator.commit_transaction(txid)
        second_commit = self.coordinator.commit_transaction(txid)
        self.assertTrue(first_commit)
        self.assertTrue(second_commit)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "COMMITTED")
        rollback_result = self.coordinator.rollback_transaction(txid)
        self.assertTrue(rollback_result)
        self.assertEqual(self.coordinator.get_transaction_status(txid), "ABORTED")

if __name__ == "__main__":
    unittest.main()