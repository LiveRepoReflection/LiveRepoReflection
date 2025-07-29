use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use network_pathfinder::Network;

#[test]
fn test_empty_network() {
    let network = Network::new();
    // Test path from node 1 to 2 in an empty network.
    let result = network.shortest_path(1, 2);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), None);
}

#[test]
fn test_same_source_destination() {
    let network = Network::new();
    // When source and destination are the same, cost is 0 and the path is [src].
    let result = network.shortest_path(42, 42);
    assert!(result.is_ok());
    let opt_path = result.unwrap();
    assert!(opt_path.is_some());
    let (cost, path) = opt_path.unwrap();
    assert!((cost - 0.0).abs() < 1e-9);
    assert_eq!(path, vec![42]);
}

#[test]
fn test_direct_connection() {
    let mut network = Network::new();
    // Add a single edge between nodes 1 and 2.
    assert!(network.add_edge(1, 2, 1.5).is_ok());
    let result = network.shortest_path(1, 2);
    assert!(result.is_ok());
    let opt_path = result.unwrap();
    assert!(opt_path.is_some());
    let (cost, path) = opt_path.unwrap();
    assert!((cost - 1.5).abs() < 1e-9);
    assert_eq!(path, vec![1, 2]);
}

#[test]
fn test_disconnected_nodes() {
    let mut network = Network::new();
    // Create nodes 1, 2, and 3. Only connect 1 and 2.
    assert!(network.add_edge(1, 2, 2.0).is_ok());
    let result = network.shortest_path(1, 3);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), None);
}

#[test]
fn test_multiple_paths() {
    let mut network = Network::new();
    // Create a graph:
    // 1--(1.0)-->2--(1.0)-->4
    // 1--(2.5)-->3--(0.5)-->4
    assert!(network.add_edge(1, 2, 1.0).is_ok());
    assert!(network.add_edge(2, 4, 1.0).is_ok());
    assert!(network.add_edge(1, 3, 2.5).is_ok());
    assert!(network.add_edge(3, 4, 0.5).is_ok());
    // The shortest path should be 1 -> 2 -> 4 with cost 2.0.
    let result = network.shortest_path(1, 4);
    assert!(result.is_ok());
    let opt_path = result.unwrap();
    assert!(opt_path.is_some());
    let (cost, path) = opt_path.unwrap();
    assert!((cost - 2.0).abs() < 1e-9);
    assert_eq!(path, vec![1, 2, 4]);
}

#[test]
fn test_removed_edge() {
    let mut network = Network::new();
    // Add edges then remove one and test that the shortest path is updated accordingly.
    assert!(network.add_edge(1, 2, 1.0).is_ok());
    assert!(network.add_edge(2, 3, 1.0).is_ok());
    // Initially, path from 1 to 3 exists.
    let result_before = network.shortest_path(1, 3);
    assert!(result_before.is_ok());
    assert!(result_before.unwrap().is_some());
    
    // Remove the edge between 2 and 3.
    assert!(network.remove_edge(2, 3).is_ok());
    let result_after = network.shortest_path(1, 3);
    assert!(result_after.is_ok());
    assert_eq!(result_after.unwrap(), None);
}

#[test]
fn test_update_edge() {
    let mut network = Network::new();
    // Add an edge and then update its weight.
    assert!(network.add_edge(1, 2, 5.0).is_ok());
    // Update the edge to a lower weight.
    assert!(network.update_edge(1, 2, 2.0).is_ok());
    let result = network.shortest_path(1, 2);
    assert!(result.is_ok());
    let opt_path = result.unwrap();
    assert!(opt_path.is_some());
    let (cost, path) = opt_path.unwrap();
    assert!((cost - 2.0).abs() < 1e-9);
    assert_eq!(path, vec![1, 2]);
}

#[test]
fn test_negative_edge_error() {
    let mut network = Network::new();
    // Attempt to add a negative edge weight.
    let result = network.add_edge(1, 2, -3.5);
    assert!(result.is_err());
}

#[test]
fn test_concurrent_updates_and_queries() {
    // Shared network protected by Mutex for concurrent access.
    let network = Arc::new(Mutex::new(Network::new()));
    // Prepopulate network with a basic structure.
    {
        let mut net = network.lock().unwrap();
        // Create a simple chain: 1-2, 2-3, 3-4.
        assert!(net.add_edge(1, 2, 1.0).is_ok());
        assert!(net.add_edge(2, 3, 1.0).is_ok());
        assert!(net.add_edge(3, 4, 1.0).is_ok());
    }

    // Spawn threads to perform updates.
    let network_clone = Arc::clone(&network);
    let updater = thread::spawn(move || {
        for _ in 0..10 {
            {
                let mut net = network_clone.lock().unwrap();
                // Randomly update the edge between 2 and 3.
                let _ = net.update_edge(2, 3, 0.5);
            }
            thread::sleep(Duration::from_millis(10));
        }
    });

    // Spawn threads to perform queries concurrently.
    let mut query_handles = vec![];
    for _ in 0..5 {
        let network_clone = Arc::clone(&network);
        let handle = thread::spawn(move || {
            for _ in 0..20 {
                {
                    let net = network_clone.lock().unwrap();
                    let result = net.shortest_path(1, 4);
                    assert!(result.is_ok());
                    // The path may change if update occurs, but it should always be valid.
                    // Either [1,2,3,4] with updated cost or None if temporarily disconnected.
                    let _ = result.unwrap();
                }
                thread::sleep(Duration::from_millis(5));
            }
        });
        query_handles.push(handle);
    }

    updater.join().unwrap();
    for handle in query_handles {
        handle.join().unwrap();
    }
}