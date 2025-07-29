use std::collections::HashMap;
use byzantine_tx::{Coordinator, OperationType};

/// Helper function to check if all correct nodes have identical state.
fn assert_consistent_state(state: &Vec<HashMap<String, String>>) {
    let first_state = state.first().expect("At least one node expected");
    for s in state.iter() {
        assert_eq!(first_state, s, "Node states are inconsistent");
    }
}

#[test]
fn test_successful_transaction_without_faults() {
    // For N = 4: f = 1, so zero faulty nodes is acceptable.
    let mut coord = Coordinator::new(4);
    // Transaction: write key "a" with value "1" to node 0, and key "b" with value "2" to node 1.
    let tx = vec![
        (0, OperationType::Write, "a".to_string(), Some("1".to_string())),
        (1, OperationType::Write, "b".to_string(), Some("2".to_string())),
    ];
    // Expect successful execution.
    assert!(coord.execute_transaction(tx).is_ok());
    // After the transaction, all honest nodes must have the same state.
    let state = coord.get_nodes_state();
    assert_consistent_state(&state);
    let first = state.first().unwrap();
    assert_eq!(first.get("a"), Some(&"1".to_string()));
    assert_eq!(first.get("b"), Some(&"2".to_string()));
}

#[test]
fn test_transaction_with_faulty_nodes_exceeding_tolerance() {
    // For N = 4, tolerance is f = 1. Here we inject 2 faulty nodes which is above tolerance.
    let mut coord = Coordinator::new(4);
    coord.set_faulty_nodes(vec![0, 1]);
    // Transaction targeting nodes 2 and 3.
    let tx = vec![
        (2, OperationType::Write, "x".to_string(), Some("10".to_string())),
        (3, OperationType::Write, "y".to_string(), Some("20".to_string())),
    ];
    // The consensus must fail due to excessive faulty nodes.
    assert!(coord.execute_transaction(tx).is_err());
}

#[test]
fn test_atomicity_on_transaction_failure() {
    // Create a coordinator with valid configuration.
    let mut coord = Coordinator::new(4);
    // Inject a faulty behavior on node 2 that may cause inconsistency.
    coord.set_faulty_nodes(vec![2]);
    // The transaction contains operations on a correct node and one on the faulty node.
    let tx = vec![
        (0, OperationType::Write, "k".to_string(), Some("v".to_string())),
        (2, OperationType::Write, "malicious".to_string(), Some("payload".to_string())),
    ];
    // If the transaction fails, no node should have performed a partial write.
    let result = coord.execute_transaction(tx);
    if result.is_err() {
        let state = coord.get_nodes_state();
        // None of the nodes should contain "k" or "malicious" if the transaction aborted.
        for s in state.iter() {
            assert!(!s.contains_key("k"), "Partial write occurred on key 'k'");
            assert!(!s.contains_key("malicious"), "Partial write occurred on key 'malicious'");
        }
    }
}

#[test]
fn test_serialization_of_transactions() {
    let mut coord = Coordinator::new(4);
    // First transaction: Write "foo" = "bar" to node 0.
    let tx1 = vec![
        (0, OperationType::Write, "foo".to_string(), Some("bar".to_string())),
    ];
    assert!(coord.execute_transaction(tx1).is_ok());

    // Second transaction: Read "foo" from node 0 and Write "baz" = "qux" to node 1.
    let tx2 = vec![
        (0, OperationType::Read, "foo".to_string(), None),
        (1, OperationType::Write, "baz".to_string(), Some("qux".to_string())),
    ];
    assert!(coord.execute_transaction(tx2).is_ok());

    // Validate that the state from all non-faulty nodes is consistent.
    let state = coord.get_nodes_state();
    assert_consistent_state(&state);
    let first = state.first().unwrap();
    assert_eq!(first.get("foo"), Some(&"bar".to_string()));
    assert_eq!(first.get("baz"), Some(&"qux".to_string()));
}