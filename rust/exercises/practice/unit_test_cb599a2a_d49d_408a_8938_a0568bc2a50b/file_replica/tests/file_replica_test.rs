use std::sync::Arc;
use std::thread;

// Assuming the implementation is in the file_replica crate with the following public interface.
use file_replica::ReplicaSystem;

#[test]
fn test_store_and_fetch_success() {
    let system = ReplicaSystem::new(3);
    let data = b"chunk_data".to_vec();
    // Store chunk_id = 100 on node 0.
    assert!(system.store(0, 100, data.clone()).is_ok());
    // Fetch from node 0.
    let fetched = system.fetch(0, 100).unwrap();
    assert_eq!(fetched, data);
}

#[test]
fn test_store_duplicate_error() {
    let system = ReplicaSystem::new(3);
    let data = b"duplicate_chunk".to_vec();
    // First store should succeed.
    assert!(system.store(1, 200, data.clone()).is_ok());
    // Second store on the same node with same chunk_id should return an error.
    let result = system.store(1, 200, data);
    assert!(result.is_err());
}

#[test]
fn test_invalid_node_error() {
    let system = ReplicaSystem::new(3);
    let data = b"invalid_node_chunk".to_vec();
    // Attempt to store on an invalid node id (3 is invalid for 3 nodes: 0,1,2).
    let result = system.store(3, 300, data.clone());
    assert!(result.is_err());
    // Attempt to fetch from an invalid node.
    let fetch_result = system.fetch(3, 300);
    assert!(fetch_result.is_err());
}

#[test]
fn test_replicate_success() {
    let system = ReplicaSystem::new(4);
    let data = b"replicable_chunk".to_vec();
    // Initially store the chunk on node 0.
    assert!(system.store(0, 400, data.clone()).is_ok());
    // Request to replicate the chunk to 3 distinct nodes.
    let replication_result = system.replicate(400, 3);
    assert!(replication_result.is_ok());
    let nodes = replication_result.unwrap();
    // Check that we got exactly 3 distinct node IDs.
    assert_eq!(nodes.len(), 3);
    let mut unique_nodes = nodes.clone();
    unique_nodes.sort_unstable();
    unique_nodes.dedup();
    assert_eq!(unique_nodes.len(), 3);
    // Verify that each replicated node can fetch the data.
    for node in nodes {
        let fetched = system.fetch(node, 400).unwrap();
        assert_eq!(fetched, data);
    }
}

#[test]
fn test_replicate_too_high() {
    let system = ReplicaSystem::new(3);
    let data = b"cannot_replicate_chunk".to_vec();
    // Store the chunk initially.
    assert!(system.store(0, 500, data.clone()).is_ok());
    // Try to replicate with replication_factor greater than number of available nodes.
    let replication_result = system.replicate(500, 4);
    assert!(replication_result.is_err());
}

#[test]
fn test_delete_functionality() {
    let system = ReplicaSystem::new(4);
    let data = b"deletable_chunk".to_vec();
    // Store and replicate.
    assert!(system.store(0, 600, data.clone()).is_ok());
    let replication_result = system.replicate(600, 3);
    assert!(replication_result.is_ok());
    // Delete the chunk from all nodes.
    assert!(system.delete(600).is_ok());
    // Verify that fetching the chunk on any node returns an error.
    for node in 0..4 {
        let fetch_result = system.fetch(node, 600);
        assert!(fetch_result.is_err());
    }
}

#[test]
fn test_recover_success() {
    let system = ReplicaSystem::new(4);
    let data = b"recoverable_chunk".to_vec();
    // Store and replicate the chunk.
    assert!(system.store(1, 700, data.clone()).is_ok());
    let replication_result = system.replicate(700, 3);
    assert!(replication_result.is_ok());
    // Attempt to recover the chunk.
    let recovered = system.recover(700).unwrap();
    assert_eq!(recovered, data);
}

#[test]
fn test_concurrent_store_and_fetch() {
    let system = Arc::new(ReplicaSystem::new(8));
    let mut handles = Vec::new();

    // Launch 10 threads, each storing a unique chunk on a chosen node.
    for i in 0..10 {
        let sys_clone = Arc::clone(&system);
        handles.push(thread::spawn(move || {
            let node_id = i % 8;
            let chunk_id = 800 + i;
            let data = format!("data_{}", i).into_bytes();
            // Store the chunk.
            assert!(sys_clone.store(node_id, chunk_id, data.clone()).is_ok());
            // Fetch the chunk and verify.
            let fetched = sys_clone.fetch(node_id, chunk_id).unwrap();
            assert_eq!(fetched, data);
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_concurrent_replicate_and_recover() {
    let system = Arc::new(ReplicaSystem::new(10));
    // Store a single chunk.
    let chunk_id = 900;
    let data = b"concurrent_replication".to_vec();
    assert!(system.store(0, chunk_id, data.clone()).is_ok());
    
    let sys_clone = Arc::clone(&system);
    // Spawn a thread to run replication concurrently.
    let replicate_handle = thread::spawn(move || {
        // Request replication to 5 nodes.
        let replication_result = sys_clone.replicate(chunk_id, 5);
        replication_result.unwrap()
    });

    // Meanwhile, in the main thread, wait and then call recover.
    let recovered = system.recover(chunk_id).unwrap();
    assert_eq!(recovered, data);

    // Verify replication list.
    let nodes = replicate_handle.join().unwrap();
    assert_eq!(nodes.len(), 5);
    let mut unique_nodes = nodes;
    unique_nodes.sort_unstable();
    unique_nodes.dedup();
    assert_eq!(unique_nodes.len(), 5);
}