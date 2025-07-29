use std::thread;
use std::sync::Arc;
use trust_network::*;

#[test]
fn test_basic_trust_path() {
    let mut network = TrustNetwork::new();
    
    // Adding trust assertions
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(2, 3, Some(0.9));
    network.add_trust_assertion(1, 3, Some(0.5));
    
    // Query path from 1 to 3
    let result = network.highest_trust_path(1, 3);
    assert_eq!(result, 0.8);
}

#[test]
fn test_no_path_exists() {
    let mut network = TrustNetwork::new();
    
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(3, 4, Some(0.9));
    
    let result = network.highest_trust_path(1, 4);
    assert_eq!(result, 0.0);
}

#[test]
fn test_removing_trust() {
    let mut network = TrustNetwork::new();
    
    // Adding trust assertions
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(2, 3, Some(0.9));
    network.add_trust_assertion(1, 3, Some(0.5));
    
    // Initial query
    let result1 = network.highest_trust_path(1, 3);
    assert_eq!(result1, 0.8);
    
    // Remove trust from 2 to 3
    network.add_trust_assertion(2, 3, None);
    
    // Query again, should only have direct path now
    let result2 = network.highest_trust_path(1, 3);
    assert_eq!(result2, 0.5);
}

#[test]
fn test_longer_trust_paths() {
    let mut network = TrustNetwork::new();
    
    network.add_trust_assertion(1, 2, Some(0.9));
    network.add_trust_assertion(2, 3, Some(0.8));
    network.add_trust_assertion(3, 4, Some(0.7));
    network.add_trust_assertion(4, 5, Some(0.6));
    network.add_trust_assertion(1, 5, Some(0.5));
    
    // Path 1->2->3->4->5 has value min(0.9, 0.8, 0.7, 0.6) = 0.6
    // Path 1->5 has value 0.5
    // The highest trust path value is 0.6
    let result = network.highest_trust_path(1, 5);
    assert_eq!(result, 0.6);
}

#[test]
fn test_cyclic_trust_paths() {
    let mut network = TrustNetwork::new();
    
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(2, 3, Some(0.7));
    network.add_trust_assertion(3, 1, Some(0.9));
    network.add_trust_assertion(1, 4, Some(0.5));
    network.add_trust_assertion(3, 4, Some(0.6));
    
    // Path 1->2->3->4 has value min(0.8, 0.7, 0.6) = 0.6
    // Path 1->4 has value 0.5
    // The highest trust path value is 0.6
    let result = network.highest_trust_path(1, 4);
    assert_eq!(result, 0.6);
}

#[test]
fn test_float_precision() {
    let mut network = TrustNetwork::new();
    
    network.add_trust_assertion(1, 2, Some(0.8123));
    network.add_trust_assertion(2, 3, Some(0.8124));
    
    let result = network.highest_trust_path(1, 3);
    assert!((result - 0.8123).abs() < 0.0001);
}

#[test]
fn test_multiple_paths_same_length() {
    let mut network = TrustNetwork::new();
    
    // Two paths from 1 to 4:
    // Path A: 1->2->4 with trust min(0.8, 0.7) = 0.7
    // Path B: 1->3->4 with trust min(0.9, 0.6) = 0.6
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(1, 3, Some(0.9));
    network.add_trust_assertion(2, 4, Some(0.7));
    network.add_trust_assertion(3, 4, Some(0.6));
    
    let result = network.highest_trust_path(1, 4);
    assert_eq!(result, 0.7);
}

#[test]
fn test_path_to_self() {
    let mut network = TrustNetwork::new();
    
    network.add_trust_assertion(1, 2, Some(0.8));
    
    // Trust path to self should always be 1.0
    let result = network.highest_trust_path(1, 1);
    assert_eq!(result, 1.0);
}

#[test]
fn test_concurrent_access() {
    let network = Arc::new(ConcurrentTrustNetwork::new());
    
    // Set up initial assertions
    network.add_trust_assertion(1, 2, Some(0.8));
    network.add_trust_assertion(2, 3, Some(0.7));
    
    // Spawn threads for concurrent access
    let mut handles = vec![];
    
    // Thread 1: add assertions
    let network_clone = Arc::clone(&network);
    handles.push(thread::spawn(move || {
        network_clone.add_trust_assertion(3, 4, Some(0.6));
        network_clone.add_trust_assertion(4, 5, Some(0.5));
    }));
    
    // Thread 2: remove assertions
    let network_clone = Arc::clone(&network);
    handles.push(thread::spawn(move || {
        network_clone.add_trust_assertion(1, 3, Some(0.9));
        thread::sleep(std::time::Duration::from_millis(10));
        network_clone.add_trust_assertion(1, 3, None);
    }));
    
    // Thread 3: query paths
    let network_clone = Arc::clone(&network);
    handles.push(thread::spawn(move || {
        thread::sleep(std::time::Duration::from_millis(5));
        let result = network_clone.highest_trust_path(1, 3);
        assert!(result > 0.0); // At some point, there should be a path
    }));
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Final assertions
    let result = network.highest_trust_path(1, 5);
    // Should find path 1->2->3->4->5 with value min(0.8, 0.7, 0.6, 0.5) = 0.5
    assert_eq!(result, 0.5);
}

#[test]
fn test_large_scale() {
    let mut network = TrustNetwork::new();
    
    // Add a larger number of assertions to stress test
    for i in 0..100 {
        for j in 0..5 {
            let next_user = i * 5 + j + 1;
            // Avoid creating a complete graph to make the test more realistic
            if next_user % 7 != 0 {
                network.add_trust_assertion(i, next_user, Some(0.7 + (j as f64 * 0.05)));
            }
        }
    }
    
    // Test some long-distance paths
    let result = network.highest_trust_path(0, 499);
    // The result should be reasonable based on the graph structure
    assert!(result >= 0.0 && result <= 1.0);
}

#[test]
fn test_dynamic_updates_affecting_paths() {
    let mut network = TrustNetwork::new();
    
    // Initial setup
    network.add_trust_assertion(1, 2, Some(0.9));
    network.add_trust_assertion(2, 3, Some(0.8));
    
    // Initial path 1->2->3 has value 0.8
    let result1 = network.highest_trust_path(1, 3);
    assert_eq!(result1, 0.8);
    
    // Add better path
    network.add_trust_assertion(1, 4, Some(0.95));
    network.add_trust_assertion(4, 3, Some(0.9));
    
    // Now path 1->4->3 has value min(0.95, 0.9) = 0.9
    let result2 = network.highest_trust_path(1, 3);
    assert_eq!(result2, 0.9);
    
    // Remove better path
    network.add_trust_assertion(4, 3, None);
    
    // Back to original path
    let result3 = network.highest_trust_path(1, 3);
    assert_eq!(result3, 0.8);
}