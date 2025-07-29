use std::sync::Arc;
use std::thread;
use std::time::Duration;
use consistent_kv::Cluster;

#[test]
fn test_single_put_get() {
    // Create a cluster with 3 nodes.
    let cluster = Cluster::new(3);
    let key = "test_key";
    let value = "value1";
    cluster.put(key, value).expect("Failed to put data");
    let obtained = cluster.get(key).expect("Failed to get data");
    assert_eq!(obtained, value);
}

#[test]
fn test_concurrent_puts() {
    let cluster = Arc::new(Cluster::new(3));
    let key = "concurrent";
    let values = vec!["val1", "val2", "val3", "val4", "val5"];
    let mut handles = Vec::new();

    // Spawn multiple threads to perform concurrent puts.
    for v in values.iter() {
        let cluster_clone = Arc::clone(&cluster);
        let key_clone = key.to_string();
        let value_clone = v.to_string();
        let handle = thread::spawn(move || {
            cluster_clone.put(&key_clone, &value_clone).expect("Put operation failed");
        });
        handles.push(handle);
    }

    // Wait for all threads to complete.
    for handle in handles {
        handle.join().expect("Thread panicked during put");
    }

    // Allow time for consensus to complete.
    thread::sleep(Duration::from_millis(100));

    // The final value should be one of the concurrent writes.
    let final_value = cluster.get(key).expect("Get operation failed");
    let valid = values.into_iter().any(|v| v == final_value);
    assert!(valid, "Final value '{}' is not among the expected values", final_value);
}

#[test]
fn test_fault_tolerance() {
    let mut cluster = Cluster::new(5);

    // Simulate failures of two nodes (less than a majority).
    cluster.fail_node(1).expect("Failed to fail node 1");
    cluster.fail_node(2).expect("Failed to fail node 2");

    let key = "fault_test";
    let value = "resilient";
    cluster.put(key, value).expect("Put operation failed during node failures");
    let obtained = cluster.get(key).expect("Get operation failed during node failures");
    assert_eq!(obtained, value);

    // Recover the failed nodes.
    cluster.recover_node(1).expect("Failed to recover node 1");
    cluster.recover_node(2).expect("Failed to recover node 2");

    // Ensure consistency after recovery.
    let obtained_after = cluster.get(key).expect("Get operation failed after node recovery");
    assert_eq!(obtained_after, value);
}

#[test]
fn test_network_partition_handling() {
    let mut cluster = Cluster::new(3);

    // Simulate a network partition isolating node 0.
    cluster.isolate_node(0).expect("Failed to isolate node 0");

    let key = "partition";
    let value = "should_fail";
    // In the partitioned state, put operation should fail (if majority is not met).
    let result = cluster.put(key, value);
    assert!(result.is_err(), "Put operation should fail during a network partition");

    // Heal the network partition to restore normal operation.
    cluster.heal_partition().expect("Failed to heal partition");

    // After healing the partition, operations should resume normal behavior.
    cluster.put(key, value).expect("Put operation failed after healing partition");
    let obtained = cluster.get(key).expect("Get operation failed after healing partition");
    assert_eq!(obtained, value);
}