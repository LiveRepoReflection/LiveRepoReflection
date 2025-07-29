use network_paths::{RoutingTable, find_k_shortest_paths};
use std::collections::HashMap;

#[test]
fn test_empty_network() {
    let rt = RoutingTable::new();
    let result = find_k_shortest_paths(&rt, 1, 2, 1);
    assert!(result.is_err());
}

#[test]
fn test_single_node_network() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    let result = find_k_shortest_paths(&rt, 1, 1, 1);
    assert_eq!(result.unwrap(), vec![vec![1]]);
}

#[test]
fn test_direct_connection() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_edge(1, 2, 10);
    let result = find_k_shortest_paths(&rt, 1, 2, 1);
    assert_eq!(result.unwrap(), vec![vec![1, 2]]);
}

#[test]
fn test_multiple_paths() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_node(3);
    rt.add_edge(1, 2, 10);
    rt.add_edge(1, 3, 5);
    rt.add_edge(3, 2, 3);
    
    let result = find_k_shortest_paths(&rt, 1, 2, 2);
    let expected = vec![
        vec![1, 3, 2], // total weight 8
        vec![1, 2]     // total weight 10
    ];
    assert_eq!(result.unwrap(), expected);
}

#[test]
fn test_path_not_found() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_node(3);
    rt.add_edge(1, 2, 10);
    
    let result = find_k_shortest_paths(&rt, 1, 3, 1);
    assert!(result.is_err());
}

#[test]
fn test_limited_local_view() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_node(3);
    rt.add_node(4);
    rt.add_edge(1, 2, 1);
    rt.add_edge(2, 3, 1);
    rt.add_edge(3, 4, 1);
    
    // Simulate limited view (only 2 hops)
    rt.set_max_hops(2);
    
    let result = find_k_shortest_paths(&rt, 1, 4, 1);
    assert!(result.is_err()); // Should fail because 4 is 3 hops away
}

#[test]
fn test_network_updates() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_edge(1, 2, 10);
    
    let result1 = find_k_shortest_paths(&rt, 1, 2, 1);
    assert_eq!(result1.unwrap(), vec![vec![1, 2]]);
    
    // Update edge weight
    rt.add_edge(1, 2, 20);
    let result2 = find_k_shortest_paths(&rt, 1, 2, 1);
    assert_eq!(result2.unwrap(), vec![vec![1, 2]]);
    
    // Remove edge
    rt.remove_edge(1, 2);
    let result3 = find_k_shortest_paths(&rt, 1, 2, 1);
    assert!(result3.is_err());
}

#[test]
fn test_k_greater_than_available_paths() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_node(3);
    rt.add_edge(1, 2, 1);
    rt.add_edge(1, 3, 2);
    rt.add_edge(3, 2, 1);
    
    let result = find_k_shortest_paths(&rt, 1, 2, 5);
    let expected = vec![
        vec![1, 2],     // weight 1
        vec![1, 3, 2],  // weight 3
    ];
    assert_eq!(result.unwrap(), expected);
}

#[test]
fn test_cycle_detection() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    rt.add_node(3);
    rt.add_edge(1, 2, 1);
    rt.add_edge(2, 3, 1);
    rt.add_edge(3, 1, 1);
    
    let result = find_k_shortest_paths(&rt, 1, 3, 1);
    assert_eq!(result.unwrap(), vec![vec![1, 2, 3]]);
}

#[test]
fn test_timestamp_conflict_resolution() {
    let mut rt = RoutingTable::new();
    rt.add_node(1);
    rt.add_node(2);
    
    // Add edge with timestamp 1
    rt.add_edge_with_timestamp(1, 2, 10, 1);
    
    // Try to add older edge information
    rt.add_edge_with_timestamp(1, 2, 5, 0);
    
    // Should keep the newer information
    let result = find_k_shortest_paths(&rt, 1, 2, 1);
    assert_eq!(result.unwrap(), vec![vec![1, 2]]);
}