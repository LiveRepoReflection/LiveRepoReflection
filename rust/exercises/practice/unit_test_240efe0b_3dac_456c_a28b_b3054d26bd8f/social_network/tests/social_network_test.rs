extern crate social_network;

use social_network::*;
use std::sync::Arc;
use std::thread;

#[test]
fn test_add_user() {
    let network = SocialNetwork::new();
    let user_id = 1;
    let username = "Alice".to_string();
    let bio = "I love coding".to_string();
    
    network.add_user(user_id, username.clone(), bio.clone());
    
    let profile = network.get_profile(user_id);
    assert!(profile.is_some());
    let profile = profile.unwrap();
    assert_eq!(profile.username, username);
    assert_eq!(profile.bio, bio);
}

#[test]
fn test_add_connection() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(2, "Bob".to_string(), "I love music".to_string());
    
    assert!(network.add_connection(1, 2));
    
    // Test bidirectionality
    let connections_1 = network.get_connections(1);
    let connections_2 = network.get_connections(2);
    
    assert!(connections_1.contains(&2));
    assert!(connections_2.contains(&1));
}

#[test]
fn test_remove_connection() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(2, "Bob".to_string(), "I love music".to_string());
    
    assert!(network.add_connection(1, 2));
    assert!(network.remove_connection(1, 2));
    
    // Test bidirectionality
    let connections_1 = network.get_connections(1);
    let connections_2 = network.get_connections(2);
    
    assert!(!connections_1.contains(&2));
    assert!(!connections_2.contains(&1));
}

#[test]
fn test_find_shortest_path_direct_connection() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(2, "Bob".to_string(), "I love music".to_string());
    
    network.add_connection(1, 2);
    
    let path = network.find_shortest_path(1, 2);
    assert_eq!(path, Some(vec![1, 2]));
}

#[test]
fn test_find_shortest_path_indirect_connection() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(2, "Bob".to_string(), "I love music".to_string());
    network.add_user(3, "Charlie".to_string(), "I love movies".to_string());
    
    network.add_connection(1, 2);
    network.add_connection(2, 3);
    
    let path = network.find_shortest_path(1, 3);
    assert_eq!(path, Some(vec![1, 2, 3]));
}

#[test]
fn test_find_shortest_path_no_connection() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(4, "Dave".to_string(), "I love hiking".to_string());
    
    let path = network.find_shortest_path(1, 4);
    assert_eq!(path, None);
}

#[test]
fn test_find_shortest_path_same_user() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    
    let path = network.find_shortest_path(1, 1);
    assert_eq!(path, Some(vec![1]));
}

#[test]
fn test_find_shortest_path_nonexistent_user() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    
    let path = network.find_shortest_path(1, 999);
    assert_eq!(path, None);
    
    let path = network.find_shortest_path(999, 1);
    assert_eq!(path, None);
}

#[test]
fn test_find_shortest_path_with_offline_users() {
    let network = SocialNetwork::new();
    
    network.add_user(1, "Alice".to_string(), "I love coding".to_string());
    network.add_user(2, "Bob".to_string(), "I love music".to_string());
    network.add_user(3, "Charlie".to_string(), "I love movies".to_string());
    network.add_user(4, "Dave".to_string(), "I love hiking".to_string());
    
    network.add_connection(1, 2);
    network.add_connection(2, 3);
    network.add_connection(1, 4);
    network.add_connection(4, 3);
    
    // Mark user 2 as offline
    network.set_user_status(2, false);
    
    // Path should now go through user 4
    let path = network.find_shortest_path(1, 3);
    assert_eq!(path, Some(vec![1, 4, 3]));
    
    // Mark user 4 as offline too
    network.set_user_status(4, false);
    
    // Now there should be no path
    let path = network.find_shortest_path(1, 3);
    assert_eq!(path, None);
}

#[test]
fn test_concurrent_operations() {
    let network = Arc::new(SocialNetwork::new());
    
    for i in 1..=100 {
        network.add_user(i, format!("User{}", i), format!("Bio for user {}", i));
    }
    
    let mut handles = vec![];
    
    // Add connections in multiple threads
    for i in 1..=50 {
        let network_clone = Arc::clone(&network);
        let handle = thread::spawn(move || {
            network_clone.add_connection(i, i+50);
        });
        handles.push(handle);
    }
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    // Verify connections
    for i in 1..=50 {
        let connections = network.get_connections(i);
        assert!(connections.contains(&(i+50)));
        
        let connections = network.get_connections(i+50);
        assert!(connections.contains(&i));
    }
}

#[test]
fn test_complex_network_path_finding() {
    let network = SocialNetwork::new();
    
    // Create a more complex network
    for i in 1..=20 {
        network.add_user(i, format!("User{}", i), format!("Bio for user {}", i));
    }
    
    // Create a network with multiple possible paths
    network.add_connection(1, 2);
    network.add_connection(2, 3);
    network.add_connection(3, 4);
    network.add_connection(4, 5);
    
    network.add_connection(1, 6);
    network.add_connection(6, 7);
    network.add_connection(7, 5);
    
    network.add_connection(1, 8);
    network.add_connection(8, 9);
    network.add_connection(9, 10);
    network.add_connection(10, 5);
    
    // Test path finding - should return one of the shortest paths
    let path = network.find_shortest_path(1, 5);
    assert!(path.is_some());
    
    let path = path.unwrap();
    // There are two shortest paths with 3 hops: 1-6-7-5 and 1-2-3-4-5
    assert!(path.len() == 3 || path.len() == 4);
    assert_eq!(path[0], 1);
    assert_eq!(path[path.len() - 1], 5);
}

#[test]
fn test_large_network() {
    let network = SocialNetwork::new();
    
    // Add a large number of users
    for i in 1..=1000 {
        network.add_user(i, format!("User{}", i), format!("Bio for user {}", i));
    }
    
    // Create a chain of connections
    for i in 1..1000 {
        network.add_connection(i, i+1);
    }
    
    // Test path finding in the large network
    let path = network.find_shortest_path(1, 1000);
    assert!(path.is_some());
    
    let path = path.unwrap();
    assert_eq!(path.len(), 1000);
    assert_eq!(path[0], 1);
    assert_eq!(path[path.len() - 1], 1000);
}