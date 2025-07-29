use std::collections::HashMap;

#[test]
fn test_simple_two_node_network() {
    let n = 2;
    let connections = vec![(0, 1, 5)]; // One direct connection with latency 5
    let node_capacities = vec![2, 2]; // Each node can handle 2 connections
    let requests = vec![(0, 1, 1)]; // One request from node 0 to 1

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    
    let expected_path = vec![0, 1];
    assert_eq!(result.get(&(0, 1)), Some(&expected_path));
}

#[test]
fn test_three_node_network() {
    let n = 3;
    let connections = vec![(0, 1, 10), (1, 2, 10), (0, 2, 25)];
    let node_capacities = vec![2, 2, 2];
    let requests = vec![(0, 2, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    
    let path = result.get(&(0, 2)).unwrap();
    assert!(path == &vec![0, 1, 2] || path == &vec![0, 2]);
}

#[test]
fn test_network_with_capacity_constraints() {
    let n = 3;
    let connections = vec![(0, 1, 5), (1, 2, 5)];
    let node_capacities = vec![1, 1, 1]; // Minimal capacity
    let requests = vec![(0, 2, 1), (2, 0, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests);
    assert!(result.is_err()); // Should fail due to capacity constraints
}

#[test]
fn test_disconnected_network() {
    let n = 4;
    let connections = vec![(0, 1, 5), (2, 3, 5)]; // Two separate components
    let node_capacities = vec![2, 2, 2, 2];
    let requests = vec![(0, 2, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests);
    assert!(result.is_err()); // Should fail due to disconnected components
}

#[test]
fn test_complex_network() {
    let n = 5;
    let connections = vec![
        (0, 1, 10), (1, 2, 10), (2, 3, 10), (3, 4, 10),
        (0, 2, 25), (1, 3, 25), (2, 4, 25)
    ];
    let node_capacities = vec![3, 3, 3, 3, 3];
    let requests = vec![(0, 4, 1), (4, 0, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    
    // Check that paths exist for both requests
    assert!(result.contains_key(&(0, 4)));
    assert!(result.contains_key(&(4, 0)));
}

#[test]
fn test_high_traffic_node() {
    let n = 4;
    let connections = vec![
        (0, 2, 5), (1, 2, 5), (2, 3, 5)
    ];
    let node_capacities = vec![2, 2, 2, 2];
    let requests = vec![
        (0, 3, 1),
        (1, 3, 1),
        (0, 1, 1)
    ];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests);
    assert!(result.is_err()); // Should fail as node 2 becomes a bottleneck
}

#[test]
fn test_multiple_equal_paths() {
    let n = 4;
    let connections = vec![
        (0, 1, 10), (1, 3, 10),
        (0, 2, 10), (2, 3, 10)
    ];
    let node_capacities = vec![2, 2, 2, 2];
    let requests = vec![(0, 3, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    
    let path = result.get(&(0, 3)).unwrap();
    assert!(
        path == &vec![0, 1, 3] || 
        path == &vec![0, 2, 3]
    );
}

#[test]
fn test_max_constraints() {
    let n = 1000; // Maximum allowed nodes
    let connections = vec![(0, 999, 1000)]; // Maximum allowed latency
    let mut node_capacities = vec![100; 1000]; // Maximum allowed capacity
    let requests = vec![(0, 999, 100)]; // Maximum allowed data size

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    assert!(result.contains_key(&(0, 999)));
}

#[test]
fn test_empty_requests() {
    let n = 2;
    let connections = vec![(0, 1, 5)];
    let node_capacities = vec![2, 2];
    let requests: Vec<(usize, usize, u32)> = vec![];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests).unwrap();
    assert!(result.is_empty());
}

#[test]
fn test_invalid_node_ids() {
    let n = 2;
    let connections = vec![(0, 2, 5)]; // Node 2 doesn't exist
    let node_capacities = vec![2, 2];
    let requests = vec![(0, 1, 1)];

    let result = net_router::find_optimal_routes(n, connections, node_capacities, requests);
    assert!(result.is_err());
}