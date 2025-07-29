use std::sync::{Arc, Barrier};
use std::thread;
use txn_kv::{KVStore, TransactionError};

#[test]
fn test_basic_commit() {
    let store = KVStore::new();
    let tx1 = store.begin_transaction();
    store.write(tx1, "key1", "value1");
    // Within the same transaction, the written value should be visible.
    let local_read = store.read(tx1, "key1");
    assert!(local_read.is_some(), "Expected value to be present in tx1");
    assert_eq!(local_read.unwrap(), "value1");

    let commit_result = store.commit_transaction(tx1);
    assert!(commit_result.is_ok(), "Commit should succeed");

    // In a new transaction, the committed value should be visible.
    let tx2 = store.begin_transaction();
    let read_val = store.read(tx2, "key1");
    assert!(read_val.is_some(), "Committed value should be visible in tx2");
    assert_eq!(read_val.unwrap(), "value1");
    store.abort_transaction(tx2);
}

#[test]
fn test_conflict_detection() {
    let store = KVStore::new();
    let tx1 = store.begin_transaction();
    let tx2 = store.begin_transaction();

    store.write(tx1, "conflict_key", "tx1_value");
    store.write(tx2, "conflict_key", "tx2_value");

    // Commit the first transaction.
    let result1 = store.commit_transaction(tx1);
    assert!(result1.is_ok(), "First commit should succeed");

    // Attempt to commit the second transaction; it should conflict.
    let result2 = store.commit_transaction(tx2);
    assert!(result2.is_err(), "Second commit should fail due to conflict");
    if let Err(err) = result2 {
        match err {
            TransactionError::Conflict => {},
            _ => panic!("Expected a Conflict error"),
        }
    }
}

#[test]
fn test_abort_transaction() {
    let store = KVStore::new();
    let tx = store.begin_transaction();
    store.write(tx, "key_abort", "value_abort");
    // Abort the transaction, discarding the write.
    store.abort_transaction(tx);

    // In a new transaction the aborted write should not be visible.
    let tx_new = store.begin_transaction();
    let read_val = store.read(tx_new, "key_abort");
    assert!(read_val.is_none(), "Aborted transaction's changes should not be visible");
    store.abort_transaction(tx_new);
}

#[test]
fn test_snapshot_isolation() {
    let store = KVStore::new();

    // Begin a transaction that sees the initial state.
    let tx1 = store.begin_transaction();
    assert!(store.read(tx1, "snap_key").is_none(), "Expected no value in tx1 initially");

    // Start a second transaction and commit an update.
    let tx2 = store.begin_transaction();
    store.write(tx2, "snap_key", "value_tx2");
    let commit_tx2 = store.commit_transaction(tx2);
    assert!(commit_tx2.is_ok(), "Tx2 should commit successfully");

    // tx1 should not see the update because it operates on an earlier snapshot.
    let tx1_read = store.read(tx1, "snap_key");
    assert!(tx1_read.is_none(), "Tx1 should not see changes from tx2");
    store.abort_transaction(tx1);

    // A new transaction should see the committed value.
    let tx3 = store.begin_transaction();
    let read_val = store.read(tx3, "snap_key");
    assert!(read_val.is_some(), "New transaction should see the committed value");
    assert_eq!(read_val.unwrap(), "value_tx2");
    store.abort_transaction(tx3);
}

#[test]
fn test_concurrent_transactions() {
    let store = Arc::new(KVStore::new());
    let num_threads = 4;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = vec![];

    for i in 0..num_threads {
        let store_clone = Arc::clone(&store);
        let barrier_clone = Arc::clone(&barrier);
        let handle = thread::spawn(move || {
            let tx = store_clone.begin_transaction();
            // Synchronize all threads before writing.
            barrier_clone.wait();
            let key = format!("key_thread_{}", i);
            let value = format!("value_thread_{}", i);
            store_clone.write(tx, &key, &value);
            let local_read = store_clone.read(tx, &key);
            assert!(local_read.is_some(), "Each thread should see its own write");
            assert_eq!(local_read.unwrap(), value);
            let commit_result = store_clone.commit_transaction(tx);
            assert!(commit_result.is_ok(), "Commit in concurrent thread should succeed");
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    // Verify all updates in a new transaction.
    let tx_main = store.begin_transaction();
    for i in 0..num_threads {
        let key = format!("key_thread_{}", i);
        let expected = format!("value_thread_{}", i);
        let read_val = store.read(tx_main, &key);
        assert!(read_val.is_some(), "Main transaction should see value from thread");
        assert_eq!(read_val.unwrap(), expected);
    }
    store.abort_transaction(tx_main);
}

#[test]
fn test_garbage_collection() {
    let store = KVStore::new();

    // Perform an initial transaction.
    let tx1 = store.begin_transaction();
    store.write(tx1, "gc_key", "initial");
    let _ = store.commit_transaction(tx1);

    // Perform several updates.
    for _ in 0..5 {
        let tx = store.begin_transaction();
        store.write(tx, "gc_key", "updated");
        let _ = store.commit_transaction(tx);
    }

    // Invoke garbage collection with a minimal transaction ID.
    store.garbage_collect(2);

    // Verify that the latest committed value is still available.
    let tx_latest = store.begin_transaction();
    let read_val = store.read(tx_latest, "gc_key");
    assert!(read_val.is_some(), "After garbage collection, value should still be available");
    assert_eq!(read_val.unwrap(), "updated");
    store.abort_transaction(tx_latest);
}