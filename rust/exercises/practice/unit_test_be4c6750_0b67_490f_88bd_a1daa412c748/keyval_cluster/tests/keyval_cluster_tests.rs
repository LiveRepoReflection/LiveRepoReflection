use std::thread;
use std::time::Duration;
use keyval_cluster::Cluster;

#[test]
fn test_simple_write_read() {
    let cluster = Cluster::new(3, 3, Duration::from_millis(100), 3);
    let key = b"hello";
    let value = b"world";
    cluster.write(key, value).expect("Write failed");
    // Allow time for replication.
    thread::sleep(Duration::from_millis(150));
    let result = cluster.read(key);
    assert!(result.is_some(), "Value not found for key 'hello'");
    assert_eq!(result.unwrap(), value.to_vec());
}

#[test]
fn test_conflict_resolution() {
    let cluster = Cluster::new(3, 3, Duration::from_millis(100), 3);
    let key = b"conflict";
    let value1 = b"first";
    let value2 = b"second";
    // Write the initial value.
    cluster.write(key, value1).expect("Initial write failed");
    // Delay to ensure a later timestamp.
    thread::sleep(Duration::from_millis(50));
    // Write conflicting value that should win (last write wins).
    cluster.write(key, value2).expect("Conflicting write failed");
    thread::sleep(Duration::from_millis(150));
    let result = cluster.read(key);
    assert!(result.is_some(), "Value not found for key 'conflict'");
    assert_eq!(result.unwrap(), value2.to_vec());
}

#[test]
fn test_failure_handling() {
    // Create cluster with 4 nodes and replication factor 3.
    let cluster = Cluster::new(4, 3, Duration::from_millis(100), 3);
    // Simulate failure on node 2.
    cluster.simulate_failure(2).expect("Failed to simulate node failure");
    let key = b"node_failure";
    let value = b"resilient";
    cluster.write(key, value).expect("Write failed after node failure");
    thread::sleep(Duration::from_millis(150));
    let result = cluster.read(key);
    assert!(result.is_some(), "Value not found after node failure");
    assert_eq!(result.unwrap(), value.to_vec());
}

#[test]
fn test_gossip_failure_detection() {
    let cluster = Cluster::new(5, 4, Duration::from_millis(50), 2);
    // Initially, no nodes should be reported as failed.
    assert!(cluster.failed_nodes().is_empty(), "There should be no failed nodes initially");
    // Simulate failures on nodes 1 and 3.
    cluster.simulate_failure(1).expect("Failed to simulate node failure on node 1");
    cluster.simulate_failure(3).expect("Failed to simulate node failure on node 3");
    thread::sleep(Duration::from_millis(200));
    let failed = cluster.failed_nodes();
    // Verify that nodes 1 and 3 are reported as failed.
    assert!(failed.contains(&1), "Node 1 should be marked as failed");
    assert!(failed.contains(&3), "Node 3 should be marked as failed");
}

#[test]
fn test_concurrent_access() {
    let cluster = Cluster::new(6, 4, Duration::from_millis(100), 3);
    let key = b"concurrent";
    let initial_value = b"0";
    cluster.write(key, initial_value).expect("Initial write failed");
    
    let mut handles = vec![];
    // Spawn multiple threads to perform concurrent writes.
    for i in 1..=10 {
        let cl = cluster.clone();
        let key_local = key.clone();
        let value = i.to_string().into_bytes();
        handles.push(thread::spawn(move || {
            cl.write(&key_local, &value).expect("Concurrent write failed");
        }));
    }

    // Wait for all threads to finish.
    for handle in handles {
        handle.join().expect("Thread panicked");
    }
    thread::sleep(Duration::from_millis(200));
    let result = cluster.read(key);
    assert!(result.is_some(), "Value missing after concurrent writes");
    // Since last write wins, ensure the retrieved value is one of "1" to "10".
    let val_str = String::from_utf8(result.unwrap()).expect("Invalid UTF-8");
    let num: u32 = val_str.parse().expect("Parsed value is not a number");
    assert!(num >= 1 && num <= 10, "Read value ({}) not in expected range 1 to 10", num);
}

#[test]
fn test_read_repair() {
    let cluster = Cluster::new(3, 3, Duration::from_millis(100), 3);
    let key = b"repair";
    let correct_value = b"fixed";
    let stale_value = b"stale";
    // Write an initial stale value.
    cluster.write(key, stale_value).expect("Initial write of stale value failed");
    thread::sleep(Duration::from_millis(150));
    // For testing, force one node's local store to remain stale.
    // Assume a test-only function force_update_node exists.
    cluster.force_update_node(1, key, stale_value).expect("Force update failed");
    // Now write the correct value to update timestamps across nodes.
    cluster.write(key, correct_value).expect("Correct write failed");
    thread::sleep(Duration::from_millis(150));
    // Trigger read repair via normal read.
    let result = cluster.read(key);
    assert!(result.is_some(), "Value missing during read repair");
    assert_eq!(result.unwrap(), correct_value.to_vec(), "Read repair did not update stale value");
}