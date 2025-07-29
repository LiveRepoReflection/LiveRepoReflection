use std::sync::Arc;
use std::thread;
use distributed_tx::{Outcome, TransactionCoordinator};

#[test]
fn test_all_commit() {
    let coordinator = TransactionCoordinator::new();
    // All participants are expected to vote commit.
    let outcome = coordinator.execute_transaction(
        "tx1".to_string(),
        vec!["p1".to_string(), "p2".to_string(), "p3".to_string()],
    );
    assert_eq!(outcome, Outcome::Commit);
}

#[test]
fn test_abort_due_to_failure() {
    let coordinator = TransactionCoordinator::new();
    // Participants voting: p1 and p3 commit, but participant with id "fail_p2" simulates an abort vote.
    let outcome = coordinator.execute_transaction(
        "tx2".to_string(),
        vec!["p1".to_string(), "fail_p2".to_string(), "p3".to_string()],
    );
    assert_eq!(outcome, Outcome::Abort);
}

#[test]
fn test_concurrent_transactions() {
    let coordinator = Arc::new(TransactionCoordinator::new());
    let mut handles = Vec::new();

    // Spawn multiple transactions concurrently.
    for i in 0..10 {
        let coord_clone = Arc::clone(&coordinator);
        let tx_id = format!("concurrent_tx_{}", i);
        let participants = vec![
            "p1".to_string(),
            "p2".to_string(),
            "p3".to_string(),
        ];
        handles.push(thread::spawn(move || {
            coord_clone.execute_transaction(tx_id, participants)
        }));
    }

    // Ensure all transactions commit.
    for handle in handles {
        let outcome = handle.join().unwrap();
        assert_eq!(outcome, Outcome::Commit);
    }
}

#[test]
fn test_recovery_after_crash() {
    let coordinator = TransactionCoordinator::new();
    // Simulate a transaction where the coordinator crashes before sending final decision,
    // and then recovers. All participants vote commit.
    let outcome = coordinator.simulate_crash_and_recover(
        "tx3".to_string(),
        vec!["p1".to_string(), "p2".to_string(), "p3".to_string()],
    );
    assert_eq!(outcome, Outcome::Commit);

    // Now simulate a transaction where one participant votes abort before the crash.
    let outcome_abort = coordinator.simulate_crash_and_recover(
        "tx4".to_string(),
        vec!["p1".to_string(), "fail_p2".to_string(), "p3".to_string()],
    );
    assert_eq!(outcome_abort, Outcome::Abort);
}

#[test]
fn test_delayed_messages_simulation() {
    let coordinator = TransactionCoordinator::new();
    // Simulate a scenario where one participant (delay_p2) sends its vote with delay.
    // The coordinator should correctly handle delayed messages and commit if appropriate.
    let outcome = coordinator.execute_transaction(
        "tx5".to_string(),
        vec!["p1".to_string(), "delay_p2".to_string(), "p3".to_string()],
    );
    assert_eq!(outcome, Outcome::Commit);
}