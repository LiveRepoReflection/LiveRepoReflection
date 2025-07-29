use std::collections::HashSet;
use std::sync::{Arc, Barrier, Mutex};
use std::thread;

use dist_tx::{
    begin_transaction,
    read,
    write,
    commit_transaction,
    rollback_transaction,
};

#[test]
fn test_begin_transaction_uniqueness() {
    let tx1 = begin_transaction();
    let tx2 = begin_transaction();
    assert_ne!(tx1, tx2, "Transaction IDs should be unique");
}

#[test]
fn test_read_write_and_commit() {
    // Begin a transaction and perform writes on two resource managers.
    let tx = begin_transaction();
    write(tx, 1, "key1".to_string(), "value1".to_string());
    write(tx, 2, "key2".to_string(), "value2".to_string());

    // Within the same transaction, reads must reflect uncommitted writes.
    assert_eq!(read(tx, 1, "key1".to_string()), Some("value1".to_string()));
    assert_eq!(read(tx, 2, "key2".to_string()), Some("value2".to_string()));

    // Commit the transaction.
    let commit_success = commit_transaction(tx);
    assert!(commit_success, "Commit should succeed");

    // In a new transaction, the committed values must be visible.
    let tx2 = begin_transaction();
    assert_eq!(read(tx2, 1, "key1".to_string()), Some("value1".to_string()));
    assert_eq!(read(tx2, 2, "key2".to_string()), Some("value2".to_string()));
}

#[test]
fn test_rollback_discards_changes() {
    // Begin a transaction, write some data and then rollback.
    let tx = begin_transaction();
    write(tx, 1, "key3".to_string(), "value3".to_string());

    // The transaction sees its own write before rollback.
    assert_eq!(read(tx, 1, "key3".to_string()), Some("value3".to_string()));

    // Now rollback the transaction.
    rollback_transaction(tx);

    // In a new transaction, the rolled-back changes must not appear.
    let tx2 = begin_transaction();
    assert_eq!(read(tx2, 1, "key3".to_string()), None);
}

#[test]
fn test_concurrent_transactions() {
    let num_threads = 10;
    let barrier = Arc::new(Barrier::new(num_threads));
    let tx_ids = Arc::new(Mutex::new(Vec::new()));
    let mut handles = vec![];

    for i in 0..num_threads {
        let c_barrier = barrier.clone();
        let c_tx_ids = tx_ids.clone();
        let handle = thread::spawn(move || {
            // Ensure all threads start together.
            c_barrier.wait();
            let tx = begin_transaction();
            let key = format!("concurrent_key_{}", i);
            let value = format!("value_{}", i);
            write(tx, 1, key, value);
            let committed = commit_transaction(tx);
            assert!(committed, "Concurrent commit should succeed");
            let mut ids = c_tx_ids.lock().unwrap();
            ids.push(tx);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
    let ids = tx_ids.lock().unwrap();
    let unique_ids: HashSet<u64> = ids.iter().cloned().collect();
    assert_eq!(unique_ids.len(), num_threads, "Each transaction must have a unique ID");
}

#[test]
fn test_duplicate_commit_and_rollback() {
    let tx = begin_transaction();
    write(tx, 1, "dup".to_string(), "first".to_string());
    
    // First commit should succeed.
    let first_commit = commit_transaction(tx);
    assert!(first_commit, "Initial commit should succeed");
    
    // Duplicate commit invocation should be handled gracefully.
    let second_commit = commit_transaction(tx);
    // Duplicate operations might be no-ops; we don't enforce a specific return value.
    
    // Duplicate rollback should not cause a panic.
    rollback_transaction(tx);
}

#[test]
fn test_resource_manager_failure_simulation() {
    // This test simulates a failure in one resource manager during the commit phase.
    // It assumes that if the resource manager (id:2) fails, the commit_transaction call returns false.
    #[cfg(feature = "simulate_failure")]
    {
        use dist_tx::set_resource_failure;
        // Simulate a failure in resource manager with id 2.
        set_resource_failure(2, true);

        let tx = begin_transaction();
        write(tx, 1, "fail_key".to_string(), "value_ok".to_string());
        write(tx, 2, "fail_key".to_string(), "value_fail".to_string());
        let commit_success = commit_transaction(tx);
        assert!(!commit_success, "Commit should fail due to simulated resource manager failure");

        // Reset the simulation.
        set_resource_failure(2, false);
    }
    #[cfg(not(feature = "simulate_failure"))]
    {
        eprintln!("Skipping test_resource_manager_failure_simulation: simulate_failure feature not enabled");
    }
}

#[test]
fn test_orphaned_transaction_recovery() {
    // This test simulates recovery from an orphaned transaction.
    // It assumes that the recover_orphaned_transactions function is available when the "recovery" feature is enabled.
    #[cfg(feature = "recovery")]
    {
        use dist_tx::recover_orphaned_transactions;
        let tx = begin_transaction();
        write(tx, 1, "orphan".to_string(), "temp".to_string());
        // Simulate a coordinator crash by not calling commit/rollback.
        // Invoke recovery mechanism.
        recover_orphaned_transactions();

        // A new transaction should not see the changes left by the orphaned transaction.
        let tx2 = begin_transaction();
        let result = read(tx2, 1, "orphan".to_string());
        assert!(result.is_none(), "Orphaned transaction should not be committed after recovery");
    }
    #[cfg(not(feature = "recovery"))]
    {
        eprintln!("Skipping test_orphaned_transaction_recovery: recovery feature not enabled");
    }
}