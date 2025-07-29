use std::collections::HashMap;
use packet_route::optimal_route;

#[test]
fn test_basic_route() {
    // Graph: 0 -> 1 -> 2 -> 3
    let n = 4;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 10),
        (2, 3, 10)
    ];
    let source = 0;
    let destination = 3;
    let packet_size_bytes = 1000;
    // No bandwidth settings provided: default bandwidth will be used (1000)
    let edge_bandwidths: HashMap<(usize, usize), u64> = HashMap::new();
    // No packet loss probabilities provided: default (0.0) will be used.
    let packet_loss_probabilities: HashMap<usize, f64> = HashMap::new();

    // For default bandwidth 1000, each edge cost = latency + (packet_size / 1000 * latency) = 10 + 10 = 20.
    // Total expected cost = 20 * 3 = 60.
    let result = optimal_route(
        n,
        &edges,
        source,
        destination,
        packet_size_bytes,
        &edge_bandwidths,
        &packet_loss_probabilities,
    );
    assert!(result.is_some());
    let (total_cost, path) = result.unwrap();
    assert_eq!(total_cost, 60);
    assert_eq!(path, vec![0, 1, 2, 3]);
}

#[test]
fn test_route_with_bandwidth_variation() {
    // Graph: Two routes from 0 to 3:
    // Route A: 0 -> 1 -> 3 and Route B: 0 -> 2 -> 3.
    // Edge latencies:
    // 0-1: 10, 1-3: 50, 0-2: 20, 2-3: 20.
    let n = 4;
    let edges = vec![
        (0, 1, 10),
        (1, 3, 50),
        (0, 2, 20),
        (2, 3, 20)
    ];
    let source = 0;
    let destination = 3;
    let packet_size_bytes = 1000;
    
    let mut edge_bandwidths = HashMap::new();
    // For edge (0,1), specify low bandwidth: 500 bytes per second.
    // Penalty = (1000 / 500) * latency = 2 * 10 = 20, total cost on edge = 10 + 20 = 30.
    edge_bandwidths.insert((0, 1), 500);
    edge_bandwidths.insert((1, 0), 500);
    // For edge (1,3), specify high bandwidth: 2000 bytes per second.
    // Penalty = (1000 / 2000) * latency = 0 * 50 = 0, total cost on edge = 50.
    edge_bandwidths.insert((1, 3), 2000);
    edge_bandwidths.insert((3, 1), 2000);
    // For edges not specified, default bandwidth (1000) will be used.
    
    let packet_loss_probabilities: HashMap<usize, f64> = HashMap::new();
    
    // Calculation:
    // Route A: (0-1): 10 + (1000/500 * 10) = 10 + 20 = 30; (1-3): 50 + (1000/2000 * 50) = 50 + 0 = 50; Total = 80.
    // Route B: (0-2): 20 + (1000/1000 * 20) = 20 + 20 = 40; (2-3): 20 + 20 = 40; Total = 80.
    // Both routes yield a total cost of 80.
    let result = optimal_route(
        n,
        &edges,
        source,
        destination,
        packet_size_bytes,
        &edge_bandwidths,
        &packet_loss_probabilities,
    );
    assert!(result.is_some());
    let (total_cost, path) = result.unwrap();
    assert_eq!(total_cost, 80);
    // Accept either valid path.
    let valid_paths = vec![vec![0, 1, 3], vec![0, 2, 3]];
    assert!(valid_paths.contains(&path));
}

#[test]
fn test_route_with_packet_loss() {
    // Graph: 0 -> 1 -> 2 with a packet loss probability at node 1.
    let n = 3;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 10)
    ];
    let source = 0;
    let destination = 2;
    let packet_size_bytes = 1000;
    // Use default bandwidth for all edges.
    let edge_bandwidths: HashMap<(usize, usize), u64> = HashMap::new();
    
    let mut packet_loss_probabilities = HashMap::new();
    // Assign a packet loss probability to node 1.
    packet_loss_probabilities.insert(1, 0.1);

    // For default bandwidth 1000, each edge base cost = 10 + 10 = 20.
    // Assume a simple overhead: for each intermediate node, add floor(latency * packet_loss_probability).
    // For edge from 0->1, node 1 overhead: floor(10 * 0.1) = 1; so cost becomes 20 + 1 = 21.
    // For edge from 1->2, node 2 has default packet loss 0, cost remains 20.
    // Total expected cost = 21 + 20 = 41.
    let result = optimal_route(
        n,
        &edges,
        source,
        destination,
        packet_size_bytes,
        &edge_bandwidths,
        &packet_loss_probabilities,
    );
    assert!(result.is_some());
    let (total_cost, path) = result.unwrap();
    assert_eq!(total_cost, 41);
    assert_eq!(path, vec![0, 1, 2]);
}

#[test]
fn test_no_path() {
    // Graph: Only an edge from 0 to 1 exists.
    let n = 3;
    let edges = vec![
        (0, 1, 10)
    ];
    let source = 0;
    let destination = 2;
    let packet_size_bytes = 1000;
    let edge_bandwidths: HashMap<(usize, usize), u64> = HashMap::new();
    let packet_loss_probabilities: HashMap<usize, f64> = HashMap::new();
    
    let result = optimal_route(
        n,
        &edges,
        source,
        destination,
        packet_size_bytes,
        &edge_bandwidths,
        &packet_loss_probabilities,
    );
    assert!(result.is_none());
}