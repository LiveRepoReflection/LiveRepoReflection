use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use dist_cache::DistributedCache;

#[test]
fn test_basic_put_get() {
    let mut cache = DistributedCache::new(3, 100, 1);
    cache.put("key1".to_string(), "value1".to_string());
    let result = cache.get("key1");
    assert_eq!(result, Some("value1".to_string()));
}

#[test]
fn test_conflict_resolution() {
    let mut cache = DistributedCache::new(3, 100, 1);
    // First put with earlier timestamp.
    cache.put("conflict".to_string(), "first".to_string());
    // Sleep to ensure a later timestamp.
    thread::sleep(Duration::from_millis(10));
    cache.put("conflict".to_string(), "second".to_string());
    let result = cache.get("conflict");
    assert_eq!(result, Some("second".to_string()));
}

#[test]
fn test_eviction() {
    // Use a single node to clearly test the LRU eviction.
    let mut cache = DistributedCache::new(1, 2, 0);
    cache.put("a".to_string(), "val_a".to_string());
    cache.put("b".to_string(), "val_b".to_string());
    // Access "a" so that "b" becomes the least recently used.
    let _ = cache.get("a");
    cache.put("c".to_string(), "val_c".to_string());
    // "a" and "c" should remain; "b" should be evicted.
    assert_eq!(cache.get("a"), Some("val_a".to_string()));
    assert_eq!(cache.get("c"), Some("val_c".to_string()));
    assert_eq!(cache.get("b"), None);
}

#[test]
fn test_node_failure() {
    let mut cache = DistributedCache::new(3, 100, 1);
    // Simulate a node failure for node with id 1.
    cache.fail_node(1);
    cache.put("fail_test".to_string(), "value_fail".to_string());
    // Allow some time for asynchronous replication to complete.
    thread::sleep(Duration::from_millis(20));
    let result = cache.get("fail_test");
    assert_eq!(result, Some("value_fail".to_string()));
}

#[test]
fn test_replication_eventual_consistency() {
    let mut cache = DistributedCache::new(4, 100, 2);
    cache.put("replicate".to_string(), "rep_value".to_string());
    // Wait to allow asynchronous replication to take effect.
    thread::sleep(Duration::from_millis(50));
    let result = cache.get("replicate");
    assert_eq!(result, Some("rep_value".to_string()));
}

#[test]
fn test_concurrency() {
    let cache = Arc::new(DistributedCache::new(5, 1000, 2));
    let mut handles = Vec::new();

    // Spawn multiple threads performing concurrent put/get operations.
    for i in 0..10 {
        let cache_clone = Arc::clone(&cache);
        handles.push(thread::spawn(move || {
            for j in 0..100 {
                let key = format!("key_{}_{}", i, j);
                let value = format!("value_{}_{}", i, j);
                cache_clone.put(key.clone(), value.clone());
                // Retrieve immediately after put.
                let res = cache_clone.get(&key);
                // Since replication and ordering are handled internally,
                // the retrieved value should be equal to what was put.
                assert_eq!(res, Some(value));
            }
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
}