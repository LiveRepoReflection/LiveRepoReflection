use std::sync::Arc;
use std::thread;
use std::time::Duration;
use dtc_coordinator::Coordinator;

#[test]
fn test_begin_and_state() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some("Active".to_string()));
}

#[test]
fn test_enlist_and_prepare_commit() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();

    // Enlist two nodes.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_ok());
    assert!(coordinator.enlist_resource(&tx_id, "node2".to_string()).is_ok());

    // Both nodes prepare successfully.
    let prep1 = coordinator.prepare(&tx_id, "node1".to_string()).unwrap();
    let prep2 = coordinator.prepare(&tx_id, "node2".to_string()).unwrap();
    assert!(prep1);
    assert!(prep2);

    // Commit should succeed.
    assert!(coordinator.commit(&tx_id).is_ok());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some("Committed".to_string()));
}

#[test]
fn test_prepare_failure_and_commit() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();

    // Enlist two nodes.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_ok());
    assert!(coordinator.enlist_resource(&tx_id, "node2".to_string()).is_ok());

    // Node1 prepares successfully.
    let prep1 = coordinator.prepare(&tx_id, "node1".to_string()).unwrap();
    assert!(prep1);

    // Do not call prepare for node2 to simulate missing preparation.
    // Commit should fail since not all nodes are prepared.
    let commit_result = coordinator.commit(&tx_id);
    assert!(commit_result.is_err());
    let state = coordinator.get_transaction_state(&tx_id);
    // The state should not be "Committed" in this case.
    assert_ne!(state, Some("Committed".to_string()));
}

#[test]
fn test_commit_idempotent() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();

    // Enlist a node and prepare.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_ok());
    let prep = coordinator.prepare(&tx_id, "node1".to_string()).unwrap();
    assert!(prep);

    // First commit should succeed.
    assert!(coordinator.commit(&tx_id).is_ok());
    // Subsequent commit calls should be idempotent.
    assert!(coordinator.commit(&tx_id).is_ok());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some("Committed".to_string()));
}

#[test]
fn test_rollback_idempotent() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();

    // Enlist a node.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_ok());
    // Rollback the transaction.
    assert!(coordinator.rollback(&tx_id).is_ok());
    // Multiple rollbacks should be idempotent.
    assert!(coordinator.rollback(&tx_id).is_ok());
    let state = coordinator.get_transaction_state(&tx_id);
    assert_eq!(state, Some("RolledBack".to_string()));
}

#[test]
fn test_nonexistent_transaction() {
    let coordinator = Coordinator::new();
    let fake_tx_id = "nonexistent".to_string();

    // Operations on a nonexistent transaction should fail.
    assert!(coordinator.enlist_resource(&fake_tx_id, "node1".to_string()).is_err());
    assert!(coordinator.prepare(&fake_tx_id, "node1".to_string()).is_err());
    assert!(coordinator.commit(&fake_tx_id).is_err());
    assert!(coordinator.rollback(&fake_tx_id).is_err());
    let state = coordinator.get_transaction_state(&fake_tx_id);
    assert!(state.is_none());
}

#[test]
fn test_enlist_duplicate() {
    let coordinator = Coordinator::new();
    let tx_id = coordinator.begin_transaction();

    // Enlist a node.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_ok());
    // Attempting to enlist the same node twice should produce an error.
    assert!(coordinator.enlist_resource(&tx_id, "node1".to_string()).is_err());
}

#[test]
fn test_concurrent_transactions() {
    let coordinator = Arc::new(Coordinator::new());
    let mut handles = Vec::new();

    // Create and process 10 transactions concurrently.
    for i in 0..10 {
        let coord = Arc::clone(&coordinator);
        let handle = thread::spawn(move || {
            let tx_id = coord.begin_transaction();
            let node_id = format!("node_{}", i);
            assert!(coord.enlist_resource(&tx_id, node_id.clone()).is_ok());
            let prep = coord.prepare(&tx_id, node_id.clone()).unwrap();
            assert!(prep);
            // Introduce a slight delay to simulate work.
            thread::sleep(Duration::from_millis(10));
            assert!(coord.commit(&tx_id).is_ok());
            let state = coord.get_transaction_state(&tx_id);
            assert_eq!(state, Some("Committed".to_string()));
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}