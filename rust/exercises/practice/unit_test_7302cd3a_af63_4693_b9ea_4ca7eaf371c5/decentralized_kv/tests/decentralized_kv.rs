use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;
use decentralized_kv::*;

#[test]
fn test_put_get() {
    let mut kv = DecentralizedKV::new(5, 2);
    kv.put("key1".to_string(), "value1".to_string());
    let retrieved = kv.get("key1".to_string());
    assert_eq!(retrieved, Some("value1".to_string()));
}

#[test]
fn test_get_nonexistent() {
    let mut kv = DecentralizedKV::new(5, 2);
    let retrieved = kv.get("nonexistent".to_string());
    assert_eq!(retrieved, None);
}

#[test]
fn test_node_failure_recovery() {
    let mut kv = DecentralizedKV::new(5, 2);
    kv.put("key2".to_string(), "value2".to_string());
    // Simulate failure of one node which might be the primary
    // For the purpose of this test, we intentionally bring down node 0.
    kv.set_node_down(0);
    // Allow some time for the simulated network timeout
    thread::sleep(Duration::from_millis(150));
    let retrieved = kv.get("key2".to_string());
    // The value should still be retrievable from a replica.
    assert_eq!(retrieved, Some("value2".to_string()));
}

#[test]
fn test_all_nodes_down() {
    let mut kv = DecentralizedKV::new(3, 1);
    kv.put("key3".to_string(), "value3".to_string());
    // Bring down all nodes.
    kv.set_node_down(0);
    kv.set_node_down(1);
    kv.set_node_down(2);
    // Allow some time for the simulated network timeouts.
    thread::sleep(Duration::from_millis(150));
    let retrieved = kv.get("key3".to_string());
    assert_eq!(retrieved, None);
}

#[test]
fn test_concurrent_access() {
    let kv = Arc::new(DecentralizedKV::new(10, 3));
    let num_threads = 10;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::with_capacity(num_threads);

    for i in 0..num_threads {
        let kv_clone = Arc::clone(&kv);
        let barrier_clone = Arc::clone(&barrier);
        let key = format!("concurrent_key_{}", i);
        let value = format!("concurrent_value_{}", i);
        let handle = thread::spawn(move || {
            barrier_clone.wait();
            kv_clone.put(key.clone(), value.clone());
            // Simulate slight delay to mix the order of operations.
            thread::sleep(Duration::from_millis(10));
            let retrieved = kv_clone.get(key);
            assert_eq!(retrieved, Some(value));
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}