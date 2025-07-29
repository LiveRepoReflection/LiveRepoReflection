use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use txn_manager::{TransactionCoordinator, Participant, PreparedResult, TransactionState};

struct SuccessfulParticipant {
    name: String,
}
impl Participant for SuccessfulParticipant {
    fn prepare(&self, _transaction_id: u64) -> PreparedResult {
        PreparedResult::Ready
    }
    fn commit(&self, _transaction_id: u64) {}
    fn rollback(&self, _transaction_id: u64) {}
}

struct FailingParticipant {
    name: String,
}
impl Participant for FailingParticipant {
    fn prepare(&self, _transaction_id: u64) -> PreparedResult {
        PreparedResult::Aborted(format!("{} failed to prepare", self.name))
    }
    fn commit(&self, _transaction_id: u64) {}
    fn rollback(&self, _transaction_id: u64) {}
}

struct ReadOnlyParticipant {
    name: String,
}
impl Participant for ReadOnlyParticipant {
    fn prepare(&self, _transaction_id: u64) -> PreparedResult {
        PreparedResult::ReadOnly
    }
    fn commit(&self, _transaction_id: u64) {}
    fn rollback(&self, _transaction_id: u64) {}
}

struct SlowParticipant {
    name: String,
    delay_ms: u64,
}
impl Participant for SlowParticipant {
    fn prepare(&self, _transaction_id: u64) -> PreparedResult {
        thread::sleep(Duration::from_millis(self.delay_ms));
        PreparedResult::Ready
    }
    fn commit(&self, _transaction_id: u64) {
        thread::sleep(Duration::from_millis(self.delay_ms));
    }
    fn rollback(&self, _transaction_id: u64) {
        thread::sleep(Duration::from_millis(self.delay_ms));
    }
}

#[test]
fn test_commit_transaction_success() {
    let coordinator = TransactionCoordinator::new();
    let txn_id = coordinator.begin_transaction();
    let participant1 = Arc::new(SuccessfulParticipant { name: String::from("Participant1") });
    let participant2 = Arc::new(ReadOnlyParticipant { name: String::from("Participant2") });
    
    coordinator.register_participant(txn_id, participant1.clone());
    coordinator.register_participant(txn_id, participant2.clone());
    
    // Attempt to prepare the transaction.
    let _ = coordinator.prepare_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Prepared);
    
    // Commit the transaction.
    let _ = coordinator.commit_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Committed);
}

#[test]
fn test_rollback_transaction_due_to_failure() {
    let coordinator = TransactionCoordinator::new();
    let txn_id = coordinator.begin_transaction();
    let participant1 = Arc::new(SuccessfulParticipant { name: String::from("Participant1") });
    let failing_participant = Arc::new(FailingParticipant { name: String::from("FailingParticipant") });
    
    coordinator.register_participant(txn_id, participant1.clone());
    coordinator.register_participant(txn_id, failing_participant.clone());
    
    let _ = coordinator.prepare_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Aborted);
    
    // Even if commit is attempted after a failure, state remains aborted.
    let _ = coordinator.commit_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Aborted);
}

#[test]
fn test_duplicate_registration() {
    let coordinator = TransactionCoordinator::new();
    let txn_id = coordinator.begin_transaction();
    let participant = Arc::new(SuccessfulParticipant { name: String::from("DuplicateParticipant") });
    
    coordinator.register_participant(txn_id, participant.clone());
    coordinator.register_participant(txn_id, participant.clone());
    
    let _ = coordinator.prepare_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Prepared);
    
    coordinator.commit_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Committed);
}

#[test]
fn test_nonexistent_transaction() {
    let coordinator = TransactionCoordinator::new();
    let invalid_txn_id = 9999; // assuming this ID does not exist
    
    // Check that getting the state of a non-existent transaction is handled.
    assert_eq!(coordinator.get_transaction_state(invalid_txn_id), TransactionState::NotFound);
    
    // Prepare, commit, and rollback operations should be gracefully handled for a nonexistent transaction.
    let _ = coordinator.prepare_transaction(invalid_txn_id);
    assert_eq!(coordinator.get_transaction_state(invalid_txn_id), TransactionState::NotFound);
    
    let _ = coordinator.commit_transaction(invalid_txn_id);
    assert_eq!(coordinator.get_transaction_state(invalid_txn_id), TransactionState::NotFound);
    
    let _ = coordinator.rollback_transaction(invalid_txn_id);
    assert_eq!(coordinator.get_transaction_state(invalid_txn_id), TransactionState::NotFound);
}

#[test]
fn test_concurrent_transactions() {
    use std::thread;
    let coordinator = Arc::new(TransactionCoordinator::new());
    let mut handles = vec![];
    
    for i in 0..10 {
        let coord_clone = coordinator.clone();
        let handle = thread::spawn(move || {
            let txn_id = coord_clone.begin_transaction();
            let participant = Arc::new(SuccessfulParticipant { name: format!("Participant_{}", i) });
            coord_clone.register_participant(txn_id, participant);
            let _ = coord_clone.prepare_transaction(txn_id);
            coord_clone.commit_transaction(txn_id);
            assert_eq!(coord_clone.get_transaction_state(txn_id), TransactionState::Committed);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_slow_participant() {
    let coordinator = TransactionCoordinator::new();
    let txn_id = coordinator.begin_transaction();
    let slow_participant = Arc::new(SlowParticipant { name: String::from("Slow"), delay_ms: 100 });
    let fast_participant = Arc::new(SuccessfulParticipant { name: String::from("Fast") });
    
    coordinator.register_participant(txn_id, slow_participant);
    coordinator.register_participant(txn_id, fast_participant);
    
    let start_time = Instant::now();
    let _ = coordinator.prepare_transaction(txn_id);
    let duration = start_time.elapsed();
    // Ensure that the slow participant causes an expected delay.
    assert!(duration >= Duration::from_millis(100));
    
    coordinator.commit_transaction(txn_id);
    assert_eq!(coordinator.get_transaction_state(txn_id), TransactionState::Committed);
}