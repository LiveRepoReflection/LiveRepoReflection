use std::collections::HashMap;
use std::sync::{Arc, Mutex};

// The following is a simulated interface for a distributed transactional key-value store.
// It is assumed that the implementation in the library (dist_tx_kv) exposes a struct
// named "DistTxKv" with the methods as described below.
// For the purpose of unit tests, we assume that the implementation supports the following methods:
//   - new(node_count: usize) -> Self
//   - begin_transaction() -> u64
//   - read(tid: u64, key: String) -> Option<String>
//   - write(tid: u64, key: String, value: String)
//   - commit_transaction(tid: u64) -> bool
//   - rollback_transaction(tid: u64)
//   - fail_node(node_id: usize)
//   - recover_node(node_id: usize)
//
// It is also assumed that the system guarantees ACID properties and proper isolation between transactions.
// The tests below simulate various scenarios such as basic commit, rollback, isolation between transactions,
// conflict resolution, durability (with simulated node failure), and scalability with multiple concurrent transactions.

use dist_tx_kv::DistTxKv;

#[test]
fn test_unique_transaction_ids() {
    let mut store = DistTxKv::new(3);
    let tid1 = store.begin_transaction();
    let tid2 = store.begin_transaction();
    assert_ne!(tid1, tid2, "Transaction IDs should be unique");
}

#[test]
fn test_basic_commit() {
    let mut store = DistTxKv::new(3);
    let tid = store.begin_transaction();
    store.write(tid, "a".to_string(), "value_a".to_string());
    // Within the same transaction, the written value should be immediately visible.
    assert_eq!(store.read(tid, "a".to_string()), Some("value_a".to_string()));
    // Commit and check that the value is persisted.
    assert!(store.commit_transaction(tid), "Commit should succeed");
    let tid2 = store.begin_transaction();
    assert_eq!(store.read(tid2, "a".to_string()), Some("value_a".to_string()));
}

#[test]
fn test_transaction_rollback() {
    let mut store = DistTxKv::new(3);
    let tid = store.begin_transaction();
    store.write(tid, "b".to_string(), "value_b".to_string());
    // Rollback the transaction.
    store.rollback_transaction(tid);
    let tid2 = store.begin_transaction();
    // The rolled back write should not be visible in a new transaction.
    assert_eq!(store.read(tid2, "b".to_string()), None);
}

#[test]
fn test_transaction_isolation() {
    let mut store = DistTxKv::new(3);
    let tid1 = store.begin_transaction();
    store.write(tid1, "c".to_string(), "value_c".to_string());
    
    let tid2 = store.begin_transaction();
    // Transaction tid2 should not see uncommitted changes from tid1.
    assert_eq!(store.read(tid2, "c".to_string()), None);

    // Commit the first transaction.
    assert!(store.commit_transaction(tid1), "Commit for tid1 should succeed");
    // Depending on the isolation level, tid2 might still not see tid1's changes.
    // Start a new transaction to see the committed value.
    let tid3 = store.begin_transaction();
    assert_eq!(store.read(tid3, "c".to_string()), Some("value_c".to_string()));
}

#[test]
fn test_conflict_resolution() {
    let mut store = DistTxKv::new(3);
    // Start two transactions concurrently that attempt to write to the same key.
    let tid1 = store.begin_transaction();
    let tid2 = store.begin_transaction();
    store.write(tid1, "d".to_string(), "value_d1".to_string());
    store.write(tid2, "d".to_string(), "value_d2".to_string());
    // Commit the first transaction.
    assert!(store.commit_transaction(tid1), "First commit should succeed");
    // Committing the second transaction should fail due to a write conflict.
    assert!(!store.commit_transaction(tid2), "Second commit should fail due to conflict");
    
    // Verify that the committed value is from the first transaction.
    let tid3 = store.begin_transaction();
    assert_eq!(store.read(tid3, "d".to_string()), Some("value_d1".to_string()));
}

#[test]
fn test_durability_after_failure() {
    let mut store = DistTxKv::new(3);
    let tid = store.begin_transaction();
    store.write(tid, "e".to_string(), "value_e".to_string());
    assert!(store.commit_transaction(tid), "Commit should succeed");
    
    // Simulate a node failure.
    store.fail_node(1);
    
    // After a node failure, the committed data should still be accessible.
    let tid2 = store.begin_transaction();
    assert_eq!(store.read(tid2, "e".to_string()), Some("value_e".to_string()));
    
    // Recover the failed node.
    store.recover_node(1);
}

#[test]
fn test_concurrent_transactions_scalability() {
    let mut store = DistTxKv::new(5);
    let mut tids = Vec::new();
    
    // Begin and write in 50 separate transactions.
    for i in 0..50 {
        let tid = store.begin_transaction();
        let key = format!("key_{}", i);
        let value = format!("value_{}", i);
        store.write(tid, key.clone(), value.clone());
        // Verify that within the transaction, the value is visible.
        assert_eq!(store.read(tid, key.clone()), Some(value));
        tids.push(tid);
    }
    
    // Commit all transactions.
    for tid in tids {
        assert!(store.commit_transaction(tid), "Commit should succeed for each transaction");
    }
    
    // Start a new transaction to verify that all committed values are present.
    let tid_new = store.begin_transaction();
    for i in 0..50 {
        let key = format!("key_{}", i);
        let expected = format!("value_{}", i);
        assert_eq!(store.read(tid_new, key), Some(expected));
    }
}