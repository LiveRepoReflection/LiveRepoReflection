use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use data_consistency::Node;

#[test]
fn test_node_initialization() {
    let node = Node::new(0, 3);
    let result = node.get("key".to_string());
    assert!(result.is_empty(), "Expected empty result for uninitialized key");
}

#[test]
fn test_single_put_and_get() {
    let node = Node::new(0, 3);
    node.put("key".to_string(), b"value".to_vec());
    node.process_messages();
    
    let result = node.get("key".to_string());
    assert_eq!(result.len(), 1, "Expected one version after put");
    let (val, vector_clock) = &result[0];
    assert_eq!(val, &b"value".to_vec(), "Value does not match");
    // For node 0, vector clock should be [1, 0, 0] for a 3-node system.
    assert_eq!(vector_clock.len(), 3, "Vector clock length mismatch");
    assert_eq!(vector_clock[0], 1, "Vector clock count for node 0 should be 1");
    assert_eq!(vector_clock[1], 0, "Vector clock count for node 1 should be 0");
    assert_eq!(vector_clock[2], 0, "Vector clock count for node 2 should be 0");
}

#[test]
fn test_conflict_resolution_concurrent_updates() {
    // Create two nodes that will concurrently update the same key.
    let node0 = Node::new(0, 3);
    let node1 = Node::new(1, 3);

    // Both nodes update the same key independently.
    node0.put("key".to_string(), b"value0".to_vec());
    node1.put("key".to_string(), b"value1".to_vec());
    node0.process_messages();
    node1.process_messages();

    // Retrieve the current versions from each node.
    let versions_node0 = node0.get("key".to_string());
    let versions_node1 = node1.get("key".to_string());
    assert_eq!(versions_node0.len(), 1, "Node0 should have one version before exchange");
    assert_eq!(versions_node1.len(), 1, "Node1 should have one version before exchange");
    let (val0, vc0) = &versions_node0[0];
    let (val1, vc1) = &versions_node1[0];

    // Exchange updates between nodes.
    node0.receive_update("key".to_string(), val1.clone(), vc1.clone());
    node1.receive_update("key".to_string(), val0.clone(), vc0.clone());
    node0.process_messages();
    node1.process_messages();

    // After exchanging, both nodes should have two conflicting versions.
    let res0 = node0.get("key".to_string());
    let res1 = node1.get("key".to_string());
    assert_eq!(res0.len(), 2, "Expected 2 versions on node0 due to conflict");
    assert_eq!(res1.len(), 2, "Expected 2 versions on node1 due to conflict");

    let values_node0: Vec<Vec<u8>> = res0.iter().map(|(v, _)| v.clone()).collect();
    assert!(values_node0.contains(&b"value0".to_vec()), "node0 missing value0");
    assert!(values_node0.contains(&b"value1".to_vec()), "node0 missing value1");
}

#[test]
fn test_update_overwrites_existing_value() {
    // Update a key twice with strictly increasing vector clocks.
    let node = Node::new(0, 3);
    // Start with an initial update.
    node.put("key".to_string(), b"old".to_vec());
    node.process_messages();

    // Update the key with a new value.
    node.put("key".to_string(), b"new".to_vec());
    node.process_messages();

    let res = node.get("key".to_string());
    // The more recent update should overwrite the old version.
    assert_eq!(res.len(), 1, "Only one version should exist after overwrite");
    let (val, vc) = &res[0];
    assert_eq!(val, &b"new".to_vec(), "Value should be 'new'");
    // The vector clock for node 0 should have been incremented twice.
    assert_eq!(vc[0], 2, "Vector clock for node 0 should be 2 after two updates");
}

#[test]
fn test_asynchronous_message_ordering() {
    // Simulate out-of-order message delivery.
    let node = Node::new(0, 3);
    // Perform an initial put.
    node.put("key".to_string(), b"first".to_vec());
    node.process_messages();
    
    // Capture the initial vector clock.
    let versions = node.get("key".to_string());
    assert_eq!(versions.len(), 1, "Expected one version after first put");
    let (_, vc_first) = &versions[0];

    // Create two updates with different vector clocks.
    let mut updated_vc = vc_first.clone();
    updated_vc[0] += 1;
    let early_update = ("key".to_string(), b"second".to_vec(), vc_first.clone());
    let delayed_update = ("key".to_string(), b"third".to_vec(), updated_vc.clone());

    // Deliver messages out of order.
    node.receive_update(early_update.0.clone(), early_update.1.clone(), early_update.2.clone());
    node.receive_update(delayed_update.0.clone(), delayed_update.1.clone(), delayed_update.2.clone());
    node.process_messages();

    let res = node.get("key".to_string());
    // The update with the higher vector clock should win.
    assert_eq!(res.len(), 1, "Only one version expected after proper ordering");
    let (val, vc) = &res[0];
    assert_eq!(val, &b"third".to_vec(), "Value should be 'third' after asynchronous updates");
    assert_eq!(vc, &updated_vc, "Vector clock should match the delayed update");
}