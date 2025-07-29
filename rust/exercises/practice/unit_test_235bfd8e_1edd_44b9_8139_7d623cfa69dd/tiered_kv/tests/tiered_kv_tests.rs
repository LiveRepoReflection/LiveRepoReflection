use std::sync::Arc;
use std::thread;
use tiered_kv::{Cluster, Node};

#[test]
fn test_put_get_single_node() {
    let cluster = Cluster::new(1, 3);
    cluster.put("key1".to_string(), "value1".to_string());
    let result = cluster.get("key1".to_string());
    assert_eq!(result, Some("value1".to_string()));
}

#[test]
fn test_non_existing_key() {
    let cluster = Cluster::new(2, 2);
    assert_eq!(cluster.get("nonexistent".to_string()), None);
}

#[test]
fn test_cache_eviction() {
    // Create a cluster with one node and a small cache to force eviction.
    let cluster = Cluster::new(1, 2);
    // Insert two keys to fill the cache.
    cluster.put("key1".to_string(), "value1".to_string());
    cluster.put("key2".to_string(), "value2".to_string());
    // Access key1 to mark it as recently used.
    assert_eq!(cluster.get("key1".to_string()), Some("value1".to_string()));
    // Inserting a new key should evict the least recently used key from Tier1.
    cluster.put("key3".to_string(), "value3".to_string());
    // key2 should be evicted from the in-memory cache.
    // However, it should still be retrievable from Tier2 (disk), and then promoted to the cache.
    let value = cluster.get("key2".to_string());
    assert_eq!(value, Some("value2".to_string()));
}

#[test]
fn test_multiple_nodes_distribution() {
    // Create a cluster with three nodes.
    let cluster = Cluster::new(3, 2);
    cluster.put("a".to_string(), "alpha".to_string());
    cluster.put("b".to_string(), "beta".to_string());
    cluster.put("c".to_string(), "gamma".to_string());
    cluster.put("d".to_string(), "delta".to_string());

    let keys = vec!["a", "b", "c", "d"];
    let values = vec!["alpha", "beta", "gamma", "delta"];

    for (k, v) in keys.iter().zip(values.iter()) {
        assert_eq!(cluster.get(k.to_string()), Some(v.to_string()));
    }
}

#[test]
fn test_concurrent_put_get() {
    let cluster = Arc::new(Cluster::new(3, 3));
    let mut handles = vec![];

    // Spawn threads to perform concurrent put operations.
    for i in 0..10 {
        let cluster_clone = Arc::clone(&cluster);
        handles.push(thread::spawn(move || {
            let key = format!("key{}", i);
            let value = format!("value{}", i);
            cluster_clone.put(key, value);
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }

    // Spawn threads to perform concurrent get operations.
    let mut read_handles = vec![];
    for i in 0..10 {
        let cluster_clone = Arc::clone(&cluster);
        read_handles.push(thread::spawn(move || {
            let key = format!("key{}", i);
            let value = format!("value{}", i);
            for _ in 0..5 {
                if let Some(v) = cluster_clone.get(key.clone()) {
                    assert_eq!(v, value);
                }
            }
        }));
    }
    for handle in read_handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_disk_persistence_simulation() {
    // Simulate disk persistence by using a single-node cluster.
    // We assume that the underlying implementation persists data in Tier2.
    // For this test, we simulate a node restart by invoking a restart method on the cluster.
    let mut cluster = Cluster::new(1, 2);
    cluster.put("persist_key".to_string(), "persist_value".to_string());
    // Simulate a node restart to clear the in-memory cache.
    cluster.restart_node(0);
    // The key should still be retrievable due to Tier2 persistence.
    assert_eq!(cluster.get("persist_key".to_string()), Some("persist_value".to_string()));
}