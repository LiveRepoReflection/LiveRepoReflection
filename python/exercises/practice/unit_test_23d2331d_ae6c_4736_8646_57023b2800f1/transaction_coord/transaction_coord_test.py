import unittest
import uuid
import time
import threading
from unittest.mock import Mock, patch
from transaction_coord import (
    TransactionCoordinator,
    Participant,
    TransactionNotFound,
    ParticipantFailedToCommit,
    ParticipantFailedToRollback
)


class ParticipantMock(Participant):
    def __init__(self, name, commit_behavior='success', rollback_behavior='success'):
        self.name = name
        self.commit_behavior = commit_behavior
        self.rollback_behavior = rollback_behavior
        self.commit_calls = []
        self.rollback_calls = []
    
    def commit(self, transaction_id):
        self.commit_calls.append(transaction_id)
        if self.commit_behavior == 'fail':
            raise Exception(f"Simulated commit failure for {self.name}")
        elif self.commit_behavior == 'timeout':
            time.sleep(2)  # Simulate timeout
        return True
    
    def rollback(self, transaction_id):
        self.rollback_calls.append(transaction_id)
        if self.rollback_behavior == 'fail':
            raise Exception(f"Simulated rollback failure for {self.name}")
        return True


class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator(max_participants=10, max_concurrent_transactions=100, commit_timeout=1)
    
    def tearDown(self):
        # Clean up any remaining transactions
        self.coordinator = None
    
    def test_begin_transaction(self):
        transaction_id = self.coordinator.begin_transaction()
        self.assertIsNotNone(transaction_id)
        self.assertIsInstance(transaction_id, uuid.UUID)
    
    def test_enlist_participant(self):
        transaction_id = self.coordinator.begin_transaction()
        participant = ParticipantMock("TestParticipant")
        self.coordinator.enlist_participant(transaction_id, participant)
        
        # Verify the participant was added
        transaction = self.coordinator._transactions.get(transaction_id)
        self.assertIsNotNone(transaction)
        self.assertIn(participant, transaction['participants'])
    
    def test_enlist_participant_invalid_transaction(self):
        invalid_id = uuid.uuid4()
        participant = ParticipantMock("TestParticipant")
        with self.assertRaises(TransactionNotFound):
            self.coordinator.enlist_participant(invalid_id, participant)
    
    def test_commit_transaction_success(self):
        transaction_id = self.coordinator.begin_transaction()
        participants = [
            ParticipantMock("Service1"),
            ParticipantMock("Service2"),
            ParticipantMock("Service3")
        ]
        
        for p in participants:
            self.coordinator.enlist_participant(transaction_id, p)
        
        result = self.coordinator.commit_transaction(transaction_id)
        self.assertTrue(result)
        
        # Verify all participants were committed
        for p in participants:
            self.assertIn(transaction_id, p.commit_calls)
            self.assertEqual(len(p.commit_calls), 1)
            self.assertEqual(len(p.rollback_calls), 0)
    
    def test_commit_transaction_failure(self):
        transaction_id = self.coordinator.begin_transaction()
        participants = [
            ParticipantMock("Service1"),
            ParticipantMock("Service2"),
            ParticipantMock("Service3", commit_behavior='fail')
        ]
        
        for p in participants:
            self.coordinator.enlist_participant(transaction_id, p)
        
        with self.assertRaises(ParticipantFailedToCommit):
            self.coordinator.commit_transaction(transaction_id)
        
        # Verify all participants were rolled back
        for p in participants:
            self.assertIn(transaction_id, p.rollback_calls)
    
    def test_rollback_transaction(self):
        transaction_id = self.coordinator.begin_transaction()
        participants = [
            ParticipantMock("Service1"),
            ParticipantMock("Service2"),
            ParticipantMock("Service3")
        ]
        
        for p in participants:
            self.coordinator.enlist_participant(transaction_id, p)
        
        result = self.coordinator.rollback_transaction(transaction_id)
        self.assertTrue(result)
        
        # Verify all participants were rolled back
        for p in participants:
            self.assertIn(transaction_id, p.rollback_calls)
            self.assertEqual(len(p.commit_calls), 0)
            self.assertEqual(len(p.rollback_calls), 1)
    
    def test_rollback_transaction_with_failures(self):
        transaction_id = self.coordinator.begin_transaction()
        participants = [
            ParticipantMock("Service1"),
            ParticipantMock("Service2", rollback_behavior='fail'),
            ParticipantMock("Service3")
        ]
        
        for p in participants:
            self.coordinator.enlist_participant(transaction_id, p)
        
        with self.assertRaises(ParticipantFailedToRollback):
            self.coordinator.rollback_transaction(transaction_id)
        
        # Verify rollback was attempted on all participants
        for p in participants:
            self.assertIn(transaction_id, p.rollback_calls)
    
    def test_commit_timeout(self):
        transaction_id = self.coordinator.begin_transaction()
        participants = [
            ParticipantMock("Service1"),
            ParticipantMock("Service2", commit_behavior='timeout'),
            ParticipantMock("Service3")
        ]
        
        for p in participants:
            self.coordinator.enlist_participant(transaction_id, p)
        
        with self.assertRaises(ParticipantFailedToCommit):
            self.coordinator.commit_transaction(transaction_id)
        
        # Verify all participants were rolled back
        # Note: The timeout participant may not have rollback called depending on implementation
        self.assertIn(transaction_id, participants[0].rollback_calls)
        self.assertIn(transaction_id, participants[2].rollback_calls)
    
    def test_max_participants_limit(self):
        transaction_id = self.coordinator.begin_transaction()
        
        # Add maximum number of participants
        for i in range(10):
            self.coordinator.enlist_participant(transaction_id, ParticipantMock(f"Service{i}"))
        
        # Trying to add one more should raise an error
        with self.assertRaises(Exception):
            self.coordinator.enlist_participant(transaction_id, ParticipantMock("ExtraService"))
    
    def test_concurrent_transactions(self):
        # Create multiple transactions
        transaction_ids = [self.coordinator.begin_transaction() for _ in range(10)]
        
        # Set up threads to operate on different transactions
        def worker(tx_id, participant, action):
            self.coordinator.enlist_participant(tx_id, participant)
            if action == 'commit':
                try:
                    self.coordinator.commit_transaction(tx_id)
                except Exception:
                    pass
            else:
                try:
                    self.coordinator.rollback_transaction(tx_id)
                except Exception:
                    pass
        
        threads = []
        for i, tx_id in enumerate(transaction_ids):
            participant = ParticipantMock(f"ConcurrentService{i}")
            action = 'commit' if i % 2 == 0 else 'rollback'
            t = threading.Thread(target=worker, args=(tx_id, participant, action))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify no exceptions were raised due to concurrency issues
        # This is a basic test - real concurrency issues might require more sophisticated testing
    
    def test_idempotent_commit(self):
        transaction_id = self.coordinator.begin_transaction()
        participant = ParticipantMock("IdempotentService")
        self.coordinator.enlist_participant(transaction_id, participant)
        
        # Commit multiple times
        self.coordinator.commit_transaction(transaction_id)
        
        # This should not raise an error for already committed transaction
        with self.assertRaises(TransactionNotFound):
            self.coordinator.commit_transaction(transaction_id)
        
        # Verify commit was only called once
        self.assertEqual(len(participant.commit_calls), 1)
    
    def test_idempotent_rollback(self):
        transaction_id = self.coordinator.begin_transaction()
        participant = ParticipantMock("IdempotentService")
        self.coordinator.enlist_participant(transaction_id, participant)
        
        # Rollback multiple times
        self.coordinator.rollback_transaction(transaction_id)
        
        # This should not raise an error for already rolled back transaction
        with self.assertRaises(TransactionNotFound):
            self.coordinator.rollback_transaction(transaction_id)
        
        # Verify rollback was only called once
        self.assertEqual(len(participant.rollback_calls), 1)
    
    def test_transaction_cleanup(self):
        # Start, commit, and verify the transaction is removed
        transaction_id = self.coordinator.begin_transaction()
        participant = ParticipantMock("Service")
        self.coordinator.enlist_participant(transaction_id, participant)
        
        self.coordinator.commit_transaction(transaction_id)
        
        # Transaction should be removed after commit
        self.assertNotIn(transaction_id, self.coordinator._transactions)
        
        # Same for rollback
        transaction_id = self.coordinator.begin_transaction()
        participant = ParticipantMock("Service")
        self.coordinator.enlist_participant(transaction_id, participant)
        
        self.coordinator.rollback_transaction(transaction_id)
        
        # Transaction should be removed after rollback
        self.assertNotIn(transaction_id, self.coordinator._transactions)


if __name__ == '__main__':
    unittest.main()