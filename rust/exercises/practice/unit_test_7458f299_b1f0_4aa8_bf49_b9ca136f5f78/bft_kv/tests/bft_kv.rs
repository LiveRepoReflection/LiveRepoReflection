use std::sync::Arc;
use std::thread;
use std::time::Duration;

use bft_kv::BftKvStore;

#[test]
fn test_put_and_get_without_faults() {
    // Create a BFT key-value store with 4 replicas and tolerate 1 faulty node
    let store = BftKvStore::new(4, 1, vec![]);
    
    // Simple put and get operations should work correctly
    store.put("alpha".to_string(), "1".to_string());
    let result = store.get("alpha".to_string());
    assert_eq!(result, Some("1".to_string()));
    
    store.put("beta".to_string(), "2".to_string());
    let result = store.get("beta".to_string());
    assert_eq!(result, Some("2".to_string()));
}

#[test]
fn test_get_nonexistent_key() {
    // Create a store without faulty nodes for simplicity.
    let store = BftKvStore::new(4, 1, vec![]);
    
    // Getting a key that has not been inserted should return None.
    let result = store.get("nonexistent".to_string());
    assert_eq!(result, None);
}

#[test]
fn test_faulty_nodes_behavior() {
    // Create a store with 7 replicas, tolerate up to 2 faulty nodes.
    // Mark replica indices 1 and 4 as faulty.
    let store = BftKvStore::new(7, 2, vec![1, 4]);
    
    // Even with faulty replicas, the correct value must be agreed upon.
    store.put("key".to_string(), "normal".to_string());
    let result = store.get("key".to_string());
    assert_eq!(result, Some("normal".to_string()));

    // Overwrite the value and check for consensus agreement.
    store.put("key".to_string(), "consensus".to_string());
    let result = store.get("key".to_string());
    assert_eq!(result, Some("consensus".to_string()));
}

#[test]
fn test_concurrent_access() {
    // Create a store with 7 replicas with one simulated faulty node.
    let store = Arc::new(BftKvStore::new(7, 2, vec![2]));

    // Spawn multiple threads to perform concurrent put and get operations.
    let mut handles = Vec::new();
    for i in 0..10 {
        let store_ref = Arc::clone(&store);
        let key = format!("key{}", i);
        let value = format!("value{}", i);
        let handle = thread::spawn(move || {
            store_ref.put(key.clone(), value.clone());
            // Small delay to simulate network latency
            thread::sleep(Duration::from_millis(10));
            let result = store_ref.get(key.clone());
            assert_eq!(result, Some(value));
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().expect("Thread panicked");
    }
}

#[test]
fn test_repeated_operations_and_consistency() {
    // Create a store with 10 replicas and tolerate 3 faulty nodes.
    let store = BftKvStore::new(10, 3, vec![0, 3, 7]);
    
    // Perform a series of put and get operations for multiple keys.
    let keys = vec!["a", "b", "c", "d", "e"];
    for (i, key) in keys.iter().enumerate() {
        store.put(key.to_string(), format!("v{}", i));
    }
    for (i, key) in keys.iter().enumerate() {
        let result = store.get(key.to_string());
        assert_eq!(result, Some(format!("v{}", i)));
    }
    
    // Update the values and check for consistency.
    for (i, key) in keys.iter().enumerate() {
        store.put(key.to_string(), format!("u{}", i));
        // A brief pause to allow consensus rounds to complete.
        thread::sleep(Duration::from_millis(5));
    }
    for (i, key) in keys.iter().enumerate() {
        let result = store.get(key.to_string());
        assert_eq!(result, Some(format!("u{}", i)));
    }
}