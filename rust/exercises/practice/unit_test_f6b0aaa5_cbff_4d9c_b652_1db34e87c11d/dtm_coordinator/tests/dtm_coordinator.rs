use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use dtm_coordinator::{Coordinator, Participant, TransactionState};

struct DummyParticipant {
    id: String,
    prepare_success: bool,
    commit_success: bool,
    rollback_success: bool,
}

impl DummyParticipant {
    fn new(id: &str, prepare_success: bool, commit_success: bool, rollback_success: bool) -> Self {
        Self {
            id: id.to_string(),
            prepare_success,
            commit_success,
            rollback_success,
        }
    }
}

impl Participant for DummyParticipant {
    fn prepare(&self) -> Result<(), String> {
        if self.prepare_success {
            Ok(())
        } else {
            Err(format!("Participant {} failed to prepare", self.id))
        }
    }

    fn commit(&self) -> Result<(), String> {
        if self.commit_success {
            Ok(())
        } else {
            Err(format!("Participant {} failed to commit", self.id))
        }
    }

    fn rollback(&self) -> Result<(), String> {
        if self.rollback_success {
            Ok(())
        } else {
            Err(format!("Participant {} failed to rollback", self.id))
        }
    }
}

#[test]
fn test_successful_transaction() {
    // Create coordinator and register participants that all succeed.
    let mut coordinator = Coordinator::new();
    let p1 = Box::new(DummyParticipant::new("p1", true, true, true));
    let p2 = Box::new(DummyParticipant::new("p2", true, true, true));
    let p3 = Box::new(DummyParticipant::new("p3", true, true, true));
    coordinator.register_participant("p1".to_string(), p1);
    coordinator.register_participant("p2".to_string(), p2);
    coordinator.register_participant("p3".to_string(), p3);

    let tx_id = "tx_success".to_string();
    let result = coordinator.execute_transaction(tx_id.clone());
    assert!(result.is_ok());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some(TransactionState::Committed));
}

#[test]
fn test_prepare_failure_transaction() {
    // Create coordinator and register a participant that fails during the prepare phase.
    let mut coordinator = Coordinator::new();
    let p1 = Box::new(DummyParticipant::new("p1", true, true, true));
    let p2 = Box::new(DummyParticipant::new("p2", false, true, true)); // Fails in prepare.
    coordinator.register_participant("p1".to_string(), p1);
    coordinator.register_participant("p2".to_string(), p2);

    let tx_id = "tx_fail_prepare".to_string();
    let result = coordinator.execute_transaction(tx_id.clone());
    assert!(result.is_err());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some(TransactionState::Aborted));
}

#[test]
fn test_commit_failure_transaction() {
    // Create coordinator and register a participant that fails during the commit phase.
    let mut coordinator = Coordinator::new();
    let p1 = Box::new(DummyParticipant::new("p1", true, false, true)); // Fails in commit.
    let p2 = Box::new(DummyParticipant::new("p2", true, true, true));
    coordinator.register_participant("p1".to_string(), p1);
    coordinator.register_participant("p2".to_string(), p2);

    let tx_id = "tx_fail_commit".to_string();
    let result = coordinator.execute_transaction(tx_id.clone());
    // In the event of a commit failure, the coordinator should rollback.
    assert!(result.is_err());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some(TransactionState::Aborted));
}

#[test]
fn test_transaction_timeout() {
    // Create coordinator and register a participant that simulates a slow response.
    let mut coordinator = Coordinator::new();
    struct SlowParticipant {
        id: String,
    }
    impl Participant for SlowParticipant {
        fn prepare(&self) -> Result<(), String> {
            thread::sleep(Duration::from_secs(65));
            Ok(())
        }
        fn commit(&self) -> Result<(), String> {
            thread::sleep(Duration::from_secs(65));
            Ok(())
        }
        fn rollback(&self) -> Result<(), String> {
            Ok(())
        }
    }
    let slow = Box::new(SlowParticipant { id: "slow".to_string() });
    coordinator.register_participant("slow".to_string(), slow);

    let tx_id = "tx_timeout".to_string();
    let result = coordinator.execute_transaction(tx_id.clone());
    // Transaction should timeout and be rolled back.
    assert!(result.is_err());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some(TransactionState::Aborted));
}

#[test]
fn test_concurrent_transactions() {
    // Test handling of multiple concurrent transactions.
    let coordinator = Arc::new(Mutex::new(Coordinator::new()));
    let mut handles = Vec::new();

    for i in 0..10 {
        let coordinator_clone = Arc::clone(&coordinator);
        let tx_id = format!("tx_{}", i);
        let handle = thread::spawn(move || {
            let mut local_coordinator = coordinator_clone.lock().unwrap();
            let p1 = Box::new(DummyParticipant::new("p1", true, true, true));
            let p2 = Box::new(DummyParticipant::new("p2", true, true, true));
            local_coordinator.register_participant(format!("p1_{}", tx_id), p1);
            local_coordinator.register_participant(format!("p2_{}", tx_id), p2);
            local_coordinator.execute_transaction(tx_id)
        });
        handles.push(handle);
    }

    for handle in handles {
        let res = handle.join().unwrap();
        assert!(res.is_ok());
    }
}

#[test]
fn test_crash_recovery() {
    // Simulate a crash scenario by executing a transaction then persisting and recovering state.
    let mut coordinator = Coordinator::new();
    let p1 = Box::new(DummyParticipant::new("p1", true, true, true));
    coordinator.register_participant("p1".to_string(), p1);

    let tx_id = "tx_recover".to_string();
    let _ = coordinator.execute_transaction(tx_id.clone());

    // Persist the current state.
    coordinator.persist_state().unwrap();
    // Simulate recovery from persisted state.
    let recovered_coordinator = Coordinator::recover_state().unwrap();
    let state = recovered_coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some(TransactionState::Committed));
}