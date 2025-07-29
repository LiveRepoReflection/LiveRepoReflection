use std::sync::{Arc, Barrier};
use std::thread;

use distributed_commit::{Coordinator, TransactionState, Vote};

#[test]
fn test_start_transaction_success() {
    let coordinator = Coordinator::new(5);
    let tx_id = 1;
    let participants = vec![1, 2, 3];
    let result = coordinator.start_transaction(tx_id, participants.clone());
    assert!(result.is_ok(), "Starting transaction should succeed");

    let state = coordinator.get_transaction_state(tx_id);
    assert!(state.is_ok(), "Transaction should exist");
    assert_eq!(state.unwrap(), TransactionState::Pending, "Initial state must be Pending");
}

#[test]
fn test_duplicate_transaction() {
    let coordinator = Coordinator::new(5);
    let tx_id = 2;
    let participants = vec![1, 2];
    assert!(coordinator.start_transaction(tx_id, participants.clone()).is_ok());
    let result = coordinator.start_transaction(tx_id, participants);
    assert!(result.is_err(), "Duplicate transaction should return an error");
}

#[test]
fn test_receive_vote_non_participant() {
    let coordinator = Coordinator::new(5);
    let tx_id = 3;
    let participants = vec![1, 2];
    coordinator.start_transaction(tx_id, participants).unwrap();
    let result = coordinator.receive_vote(tx_id, 3, Vote::Commit);
    assert!(result.is_err(), "Non-participant vote should return an error");
}

#[test]
fn test_receive_vote_invalid_transaction() {
    let coordinator = Coordinator::new(5);
    let result = coordinator.receive_vote(999, 1, Vote::Commit);
    assert!(result.is_err(), "Voting on non-existent transaction should error");
}

#[test]
fn test_make_decision_pending_votes() {
    let coordinator = Coordinator::new(5);
    let tx_id = 4;
    let participants = vec![1, 2];
    coordinator.start_transaction(tx_id, participants).unwrap();
    // Only one participant votes
    coordinator.receive_vote(tx_id, 1, Vote::Commit).unwrap();
    let decision = coordinator.make_decision(tx_id);
    assert!(decision.is_err(), "Decision should not be made if not all votes are received");
    assert_eq!(decision.unwrap_err(), "Not all votes received", "Expect not all votes received error");
}

#[test]
fn test_make_decision_commit() {
    let coordinator = Coordinator::new(5);
    let tx_id = 5;
    let participants = vec![1, 2, 3];
    coordinator.start_transaction(tx_id, participants).unwrap();
    // All participants vote commit
    coordinator.receive_vote(tx_id, 1, Vote::Commit).unwrap();
    coordinator.receive_vote(tx_id, 2, Vote::Commit).unwrap();
    coordinator.receive_vote(tx_id, 3, Vote::Commit).unwrap();
    let decision = coordinator.make_decision(tx_id);
    assert!(decision.is_ok(), "Decision should succeed when all votes are in");
    assert_eq!(decision.unwrap(), TransactionState::Committed, "Expected transaction to be committed");
}

#[test]
fn test_make_decision_abort() {
    let coordinator = Coordinator::new(5);
    let tx_id = 6;
    let participants = vec![1, 2, 3, 4];
    coordinator.start_transaction(tx_id, participants).unwrap();
    // One node votes abort; rest vote commit
    coordinator.receive_vote(tx_id, 1, Vote::Commit).unwrap();
    coordinator.receive_vote(tx_id, 2, Vote::Abort).unwrap();
    coordinator.receive_vote(tx_id, 3, Vote::Commit).unwrap();
    coordinator.receive_vote(tx_id, 4, Vote::Commit).unwrap();
    let decision = coordinator.make_decision(tx_id);
    assert!(decision.is_ok(), "Decision should succeed when all votes are in");
    assert_eq!(decision.unwrap(), TransactionState::Aborted, "Expected transaction to be aborted");
}

#[test]
fn test_get_transaction_state_not_found() {
    let coordinator = Coordinator::new(5);
    let result = coordinator.get_transaction_state(1000);
    assert!(result.is_err(), "Getting state of non-existent transaction should error");
}

#[test]
fn test_concurrent_votes() {
    let coordinator = Arc::new(Coordinator::new(10));
    let tx_id = 7;
    let participants: Vec<usize> = (1..=8).collect();
    coordinator.start_transaction(tx_id, participants.clone()).unwrap();

    // Barrier to sync threads so that they all attempt to vote at roughly the same time.
    let barrier = Arc::new(Barrier::new(participants.len()));
    let mut handles = Vec::new();

    for node in participants {
        let coord = Arc::clone(&coordinator);
        let cbarrier = Arc::clone(&barrier);
        let handle = thread::spawn(move || {
            cbarrier.wait();
            // All nodes vote commit concurrently.
            coord.receive_vote(tx_id, node, Vote::Commit).unwrap();
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    let decision = coordinator.make_decision(tx_id);
    assert!(decision.is_ok(), "Decision should succeed after concurrent votes");
    assert_eq!(decision.unwrap(), TransactionState::Committed, "All concurrent commits should result in committed state");
}