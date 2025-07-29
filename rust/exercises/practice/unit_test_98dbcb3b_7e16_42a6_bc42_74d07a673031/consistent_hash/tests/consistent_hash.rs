use std::sync::{Arc, RwLock};
use std::thread;
use consistent_hash::ConsistentHashing;

#[test]
fn test_add_and_get_node() {
    let mut ch = ConsistentHashing::new(3);
    let result = ch.add_node("node1".to_string());
    assert!(result.is_ok(), "Adding node1 should succeed");
    
    // Test that get_node returns the only added node.
    let node = ch.get_node("my_key");
    assert!(node.is_ok(), "get_node should succeed");
    assert_eq!(node.unwrap(), "node1", "The only node available should be node1");
}

#[test]
fn test_duplicate_node() {
    let mut ch = ConsistentHashing::new(3);
    let res1 = ch.add_node("node1".to_string());
    assert!(res1.is_ok(), "First addition of node1 should succeed");
    let res2 = ch.add_node("node1".to_string());
    assert!(res2.is_err(), "Adding duplicate node1 should return an error");
}

#[test]
fn test_remove_node() {
    let mut ch = ConsistentHashing::new(3);
    let _ = ch.add_node("node1".to_string());
    let _ = ch.add_node("node2".to_string());
    
    let key = "test_key";
    let node_before = ch.get_node(key).unwrap();
    assert!(node_before == "node1" || node_before == "node2", "get_node must return one of the added nodes");
    
    let remove_res = ch.remove_node("node1");
    assert!(remove_res.is_ok(), "Removing an existing node should succeed");
    
    let node_after = ch.get_node(key).unwrap();
    assert_ne!(node_after, "node1", "After removal, get_node should not return the removed node");
}

#[test]
fn test_rebalance_effect() {
    let mut ch = ConsistentHashing::new(5);
    let _ = ch.add_node("node1".to_string());
    let _ = ch.add_node("node2".to_string());
    let _ = ch.add_node("node3".to_string());
    
    let key = "balance_test_key";
    let node_before_rebalance = ch.get_node(key).unwrap();
    
    // Remove the node that was responsible for the key.
    let _ = ch.remove_node(&node_before_rebalance);
    ch.rebalance();
    
    let node_after_rebalance = ch.get_node(key).unwrap();
    assert_ne!(
        node_before_rebalance, node_after_rebalance,
        "After removal and rebalance, the responsible node must change"
    );
}

#[test]
fn test_thread_safety() {
    let ch = Arc::new(RwLock::new(ConsistentHashing::new(3)));
    {
        let mut hasher = ch.write().unwrap();
        let _ = hasher.add_node("node1".to_string());
        let _ = hasher.add_node("node2".to_string());
        let _ = hasher.add_node("node3".to_string());
    }

    let mut handles = vec![];
    for i in 0..10 {
        let ch_cloned = Arc::clone(&ch);
        let key = format!("key_{}", i);
        let handle = thread::spawn(move || {
            let hasher = ch_cloned.read().unwrap();
            let node = hasher.get_node(&key);
            assert!(node.is_ok(), "get_node should succeed in thread");
            node.unwrap()
        });
        handles.push(handle);
    }
    for handle in handles {
        let _node = handle.join().unwrap();
    }
}