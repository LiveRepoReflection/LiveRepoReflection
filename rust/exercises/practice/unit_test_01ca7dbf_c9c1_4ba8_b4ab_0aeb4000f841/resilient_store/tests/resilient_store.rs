use resilient_store::Store;
use std::sync::{Arc, Mutex};
use std::thread;

#[test]
fn test_put_and_get_success() {
    // Create a store with 5 nodes and majority factor of 3.
    let store = Store::new(5, 3);

    // Insert a key-value pair.
    let res = store.put("key1".to_string(), "value1".to_string(), 1);
    assert!(res, "put operation should succeed with majority");

    // Retrieve the value.
    let result = store.get("key1".to_string());
    assert_eq!(result, Some("value1".to_string()), "get should return value1");
}

#[test]
fn test_put_ignore_older_timestamp() {
    let store = Store::new(5, 3);

    // Insert a key-value pair with timestamp 10.
    let res = store.put("key2".to_string(), "value10".to_string(), 10);
    assert!(res, "first put should succeed");

    // Try updating with an older timestamp (5).
    let res2 = store.put("key2".to_string(), "value5".to_string(), 5);
    assert!(!res2, "put with older timestamp should be ignored");

    // Ensure the value remains the latest.
    let result = store.get("key2".to_string());
    assert_eq!(result, Some("value10".to_string()), "value should remain unchanged");
}

#[test]
fn test_delete_operation() {
    let store = Store::new(5, 3);

    // Insert a key-value pair.
    let _ = store.put("key3".to_string(), "value3".to_string(), 1);

    // Delete the key with a higher timestamp.
    let del = store.delete("key3".to_string(), 2);
    assert!(del, "delete should succeed with majority");

    // Retrieving the key should now return None.
    let result = store.get("key3".to_string());
    assert_eq!(result, None, "key3 should be deleted");
}

#[test]
fn test_concurrent_access() {
    let store = Arc::new(Store::new(7, 4)); // 7 nodes with a majority factor of 4.
    let keys = vec!["alpha", "beta", "gamma", "delta"];
    let mut handles = Vec::new();

    for i in 0..keys.len() {
        let store_clone = Arc::clone(&store);
        let key = keys[i].to_string();
        handles.push(thread::spawn(move || {
            // Each thread performs multiple put operations with increasing timestamps.
            for t in 1..=100 {
                let val = format!("{}_{}", key, t);
                let _ = store_clone.put(key.clone(), val, t);
            }
        }));
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    // Verify that each key holds the latest value.
    for key in keys {
        let result = store.get(key.to_string());
        let expected = format!("{}_{}", key, 100);
        assert_eq!(result, Some(expected), "get should return the latest value for key {}", key);
    }
}

#[test]
fn test_node_failure_simulation() {
    let mut store = Store::new(5, 3);

    // Simulate a node failure (assume node index 0 fails).
    store.fail_node(0);

    // Operations should still succeed with the majority of nodes available.
    let res = store.put("key_fail".to_string(), "value_fail".to_string(), 1);
    assert!(res, "put should succeed even after a node failure");

    let result = store.get("key_fail".to_string());
    assert_eq!(result, Some("value_fail".to_string()), "get should return correct value despite node failure");

    // Recover the failed node.
    store.recover_node(0);

    // Sync the recovered node so that it catches up to the latest state.
    store.sync_node(0);

    // Verify that the recovered node reflects the latest state.
    let result_after_sync = store.get("key_fail".to_string());
    assert_eq!(result_after_sync, Some("value_fail".to_string()), "recovered node should be in sync");
}

#[test]
fn test_tombstone_prevention() {
    let store = Store::new(5, 3);

    // Insert a key with a certain timestamp.
    let _ = store.put("key4".to_string(), "initial".to_string(), 10);

    // Delete the key with a higher timestamp (creates a tombstone).
    let _ = store.delete("key4".to_string(), 20);

    // Attempt to update the key with an older timestamp; this should be ignored.
    let res = store.put("key4".to_string(), "stale".to_string(), 15);
    assert!(!res, "old put should be ignored after deletion tombstone");

    // A newer put should succeed.
    let res2 = store.put("key4".to_string(), "new_value".to_string(), 25);
    assert!(res2, "newer put should succeed over tombstone");

    let result = store.get("key4".to_string());
    assert_eq!(result, Some("new_value".to_string()), "get should return the updated value");
}