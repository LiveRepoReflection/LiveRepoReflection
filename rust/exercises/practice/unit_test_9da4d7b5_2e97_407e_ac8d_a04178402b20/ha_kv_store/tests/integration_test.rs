use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use ha_kv_store::Cluster;

#[test]
fn test_basic_insert_get() {
    let mut cluster = Cluster::new(3);
    // Insert a key-value pair; should replicate to a majority (2 out of 3 nodes)
    cluster.insert("key1", "value1").expect("Insert failed");
    let result = cluster.get("key1").expect("Get failed");
    assert_eq!(result, "value1");
}

#[test]
fn test_delete_operation() {
    let mut cluster = Cluster::new(3);
    cluster.insert("del_key", "to_delete").expect("Insert failed");
    let result = cluster.get("del_key").expect("Get failed");
    assert_eq!(result, "to_delete");
    cluster.delete("del_key").expect("Delete failed");
    let result = cluster.get("del_key");
    assert!(result.is_err(), "Key should not exist after deletion");
}

#[test]
fn test_replication_failure() {
    let mut cluster = Cluster::new(3);
    // Fail two nodes to break the majority requirement.
    cluster.fail_node(1);
    cluster.fail_node(2);
    let result = cluster.insert("key_fail", "value_fail");
    assert!(result.is_err(), "Insert should fail with insufficient available nodes");
    // Recover one node so that a majority is available
    cluster.recover_node(1);
    let result = cluster.insert("key_fail", "value_fail");
    assert!(result.is_ok(), "Insert should succeed when majority is available");
    let value = cluster.get("key_fail").expect("Get failed after recovery");
    assert_eq!(value, "value_fail");
}

#[test]
fn test_conflict_resolution() {
    let mut cluster = Cluster::new(3);
    // Use force_insert to simulate concurrent conflicting updates with controlled Lamport clocks.
    // In the forced insert, the fourth parameter is the Lamport clock timestamp.
    // First, insert a value with a lower timestamp.
    cluster.force_insert(0, "conflict_key", "A", 5).expect("Force insert failed");
    // Then, simulate a concurrent update on a different node with a higher timestamp.
    cluster.force_insert(1, "conflict_key", "B", 10).expect("Force insert failed");
    // The conflict resolution should choose the value with higher timestamp.
    let result = cluster.get("conflict_key").expect("Get failed");
    assert_eq!(result, "B");

    // Now simulate a tie in timestamps: both updates have the same timestamp.
    // In a tie, the lexicographically smaller value should be chosen.
    cluster.force_insert(0, "tie_key", "X", 15).expect("Force insert failed");
    cluster.force_insert(1, "tie_key", "W", 15).expect("Force insert failed");
    let result = cluster.get("tie_key").expect("Get failed");
    assert_eq!(result, "W");
}

#[test]
fn test_node_recovery_sync() {
    let mut cluster = Cluster::new(3);
    // Insert an initial value.
    cluster.insert("sync_key", "initial").expect("Insert failed");
    // Fail node 1.
    cluster.fail_node(1);
    // Update the key on the cluster through an available node.
    cluster.insert("sync_key", "updated").expect("Insert failed");
    // Recover node 1; it should synchronize and reflect the latest update.
    cluster.recover_node(1);
    // Allow time for the recovery sync to complete.
    thread::sleep(Duration::from_millis(100));
    let result = cluster.get("sync_key").expect("Get failed");
    assert_eq!(result, "updated");
}

#[test]
fn test_concurrent_operations() {
    // Create a cluster with 5 nodes.
    let cluster = Arc::new(Mutex::new(Cluster::new(5)));

    let mut handles = vec![];

    // Spawn threads to perform inserts concurrently.
    for i in 0..10 {
        let cluster_clone = Arc::clone(&cluster);
        let handle = thread::spawn(move || {
            let key = format!("key_{}", i);
            let value = format!("value_{}", i);
            let mut cl = cluster_clone.lock().unwrap();
            cl.insert(&key, &value).expect("Concurrent insert failed");
        });
        handles.push(handle);
    }

    // Wait for all insert operations to complete.
    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    // Verify that all keys were inserted correctly.
    let cl = cluster.lock().unwrap();
    for i in 0..10 {
        let key = format!("key_{}", i);
        let result = cl.get(&key).expect("Get failed in concurrent test");
        assert_eq!(result, format!("value_{}", i));
    }
}