use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;

// Assuming the following public API is provided by the library:
// - begin_transaction() -> TransactionId (an opaque type, e.g., u64)
// - read(transaction_id: TransactionId, key: &str) -> Option<String>
// - write(transaction_id: TransactionId, key: &str, value: &str)
// - commit_transaction(transaction_id: TransactionId) -> Result<(), String>
// - abort_transaction(transaction_id: TransactionId) -> Result<(), String>
use dist_tx_store::{begin_transaction, read, write, commit_transaction, abort_transaction};

#[test]
fn test_single_transaction_commit() {
    let tx = begin_transaction();
    write(tx, "key1", "value1");
    write(tx, "key2", "value2");
    let val1 = read(tx, "key1");
    let val2 = read(tx, "key2");
    assert!(val1.is_some());
    assert!(val2.is_some());
    assert_eq!(val1.unwrap(), "value1");
    assert_eq!(val2.unwrap(), "value2");
    assert!(commit_transaction(tx).is_ok());

    // Start a new transaction to confirm committed changes are visible.
    let tx2 = begin_transaction();
    let val1_new = read(tx2, "key1");
    let val2_new = read(tx2, "key2");
    assert!(val1_new.is_some());
    assert!(val2_new.is_some());
    assert_eq!(val1_new.unwrap(), "value1");
    assert_eq!(val2_new.unwrap(), "value2");
    assert!(abort_transaction(tx2).is_ok());
}

#[test]
fn test_abort_transaction() {
    let tx = begin_transaction();
    write(tx, "abort_key", "temporary");
    let val = read(tx, "abort_key");
    assert!(val.is_some());
    assert_eq!(val.unwrap(), "temporary");
    assert!(abort_transaction(tx).is_ok());

    let tx2 = begin_transaction();
    // The aborted transaction should not affect the store.
    let val_after = read(tx2, "abort_key");
    assert!(val_after.is_none());
    assert!(abort_transaction(tx2).is_ok());
}

#[test]
fn test_conflict_resolution() {
    // Begin with an initial transaction that sets a baseline value.
    let tx_init = begin_transaction();
    write(tx_init, "conflict_key", "base");
    assert!(commit_transaction(tx_init).is_ok());

    // Two concurrent transactions modifying the same key.
    let tx_a = begin_transaction();
    let tx_b = begin_transaction();

    write(tx_a, "conflict_key", "valueA");
    write(tx_b, "conflict_key", "valueB");

    // Commit transaction A first.
    assert!(commit_transaction(tx_a).is_ok());
    // Commit transaction B; the conflict resolution function is expected to merge the values
    // deterministically. In this test, we expect the merged value to be "valueA|valueB".
    assert!(commit_transaction(tx_b).is_ok());

    let tx_check = begin_transaction();
    let final_value = read(tx_check, "conflict_key");
    assert!(final_value.is_some());
    assert_eq!(final_value.unwrap(), "valueA|valueB");
    assert!(abort_transaction(tx_check).is_ok());
}

#[test]
fn test_concurrent_transactions() {
    let barrier = Arc::new(Barrier::new(10));
    let mut handles = Vec::new();

    for i in 0..10 {
        let c = barrier.clone();
        handles.push(thread::spawn(move || {
            let tx = begin_transaction();
            let key = format!("concurrent_key_{}", i % 3);
            let value = format!("value_{}", i);
            write(tx, &key, &value);
            // Wait for all threads to be ready
            c.wait();
            // Sleep a little to encourage interleaving.
            thread::sleep(Duration::from_millis(10));
            assert!(commit_transaction(tx).is_ok());
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let tx_final = begin_transaction();
    for i in 0..3 {
        let key = format!("concurrent_key_{}", i);
        let value = read(tx_final, &key);
        // The value may be a result of conflict resolution (merged deterministic value) and should not be None.
        assert!(value.is_some());
    }
    assert!(abort_transaction(tx_final).is_ok());
}

#[test]
fn test_durability() {
    let tx = begin_transaction();
    write(tx, "durable_key", "durable_value");
    assert!(commit_transaction(tx).is_ok());

    // Simulate a "restart" by starting a new transaction.
    let tx2 = begin_transaction();
    let durable_val = read(tx2, "durable_key");
    assert!(durable_val.is_some());
    assert_eq!(durable_val.unwrap(), "durable_value");
    assert!(abort_transaction(tx2).is_ok());
}

#[test]
fn test_key_size_limit() {
    // Create a key of exactly 256 bytes.
    let key = "a".repeat(256);
    let tx = begin_transaction();
    write(tx, &key, "edge_value");
    let val = read(tx, &key);
    assert!(val.is_some());
    assert_eq!(val.unwrap(), "edge_value");
    assert!(commit_transaction(tx).is_ok());

    let tx2 = begin_transaction();
    let val2 = read(tx2, &key);
    assert!(val2.is_some());
    assert_eq!(val2.unwrap(), "edge_value");
    assert!(abort_transaction(tx2).is_ok());
}

#[test]
fn test_value_size_limit() {
    // Create a value of exactly 1 MB.
    let value = "b".repeat(1024 * 1024);
    let tx = begin_transaction();
    write(tx, "big_value_key", &value);
    let val = read(tx, "big_value_key");
    assert!(val.is_some());
    assert_eq!(val.unwrap(), value);
    assert!(commit_transaction(tx).is_ok());

    let tx2 = begin_transaction();
    let val2 = read(tx2, "big_value_key");
    assert!(val2.is_some());
    assert_eq!(val2.unwrap(), value);
    assert!(abort_transaction(tx2).is_ok());
}

#[test]
fn test_read_nonexistent_key() {
    let tx = begin_transaction();
    let value = read(tx, "nonexistent_key");
    assert!(value.is_none());
    assert!(abort_transaction(tx).is_ok());
}