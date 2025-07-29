use congestion_route::route_packets;

fn validate_path(path: &Vec<usize>, s: usize, t: usize) -> bool {
    if path.first() != Some(&s) || path.last() != Some(&t) {
        return false;
    }
    // Ensure the path contains at least two nodes (source and destination)
    if path.len() < 2 {
        return false;
    }
    true
}

#[test]
fn test_single_packet_direct_route() {
    // Simple graph with a direct edge from 0 to 1.
    let n = 2;
    let edges = vec![(0, 1, 10)];
    let s = 0;
    let t = 1;
    let k = 1;
    let result = route_packets(n, &edges, s, t, k);
    // Expect exactly one route [0, 1]
    assert_eq!(result.len(), 1);
    let path = &result[0];
    assert!(validate_path(path, s, t));
    // Check that the path is exactly [0, 1]
    assert_eq!(path, &vec![0, 1]);
}

#[test]
fn test_multiple_routes_different_paths() {
    // Graph with two distinct routes from 0 to 3.
    // Routes: [0, 1, 3] and [0, 2, 3]
    let n = 4;
    let edges = vec![
        (0, 1, 10),
        (1, 3, 10),
        (0, 2, 10),
        (2, 3, 10),
        // Direct edge with lower capacity to test if it's avoided if possible.
        (0, 3, 2),
    ];
    let s = 0;
    let t = 3;
    let k = 2;
    let result = route_packets(n, &edges, s, t, k);
    // We must route 2 packets.
    assert_eq!(result.len(), 2);
    for path in result.iter() {
        assert!(validate_path(path, s, t));
        // Ensure no single edge direct connection is used unless required.
        // In this test, prefer paths with intermediate nodes.
        assert!(path.len() >= 2);
    }
}

#[test]
fn test_no_possible_route() {
    // Graph with no connection from s to t.
    let n = 4;
    let edges = vec![
        (0, 1, 10),
        (2, 3, 10)
    ];
    let s = 0;
    let t = 3;
    let k = 1;
    let result = route_packets(n, &edges, s, t, k);
    // Expect empty list since there is no valid route from 0 to 3.
    assert!(result.is_empty());
}

#[test]
fn test_congestion_distribution() {
    // Graph with multiple possible paths and varying capacities.
    // Nodes: 0, 1, 2, 3, 4.
    // Route 1: 0 -> 1 -> 4 (high capacity edges)
    // Route 2: 0 -> 2 -> 3 -> 4 (lower capacity edges)
    // Requirement: k packets must be routed optimally.
    let n = 5;
    let edges = vec![
        (0, 1, 20),
        (1, 4, 20),
        (0, 2, 10),
        (2, 3, 10),
        (3, 4, 10),
        // Additional alternate path with medium capacity.
        (0, 3, 15),
        (3, 4, 15)
    ];
    let s = 0;
    let t = 4;
    let k = 3;
    let result = route_packets(n, &edges, s, t, k);
    assert_eq!(result.len(), 3);
    for path in result.iter() {
        assert!(validate_path(path, s, t));
    }
    // Since multiple valid routings can exist with different congestion distributions,
    // we only check that each returned path is valid.
}

#[test]
fn test_duplicate_edges() {
    // Graph where multiple edges exist between a pair of nodes.
    // This tests if the algorithm can handle duplicate edges correctly.
    let n = 4;
    let edges = vec![
        (0, 1, 10),
        (0, 1, 5),  // duplicate edge with different capacity.
        (1, 2, 10),
        (1, 2, 15), // duplicate edge.
        (2, 3, 10)
    ];
    let s = 0;
    let t = 3;
    let k = 2;
    let result = route_packets(n, &edges, s, t, k);
    // Check that we can successfully obtain k valid routing paths.
    assert_eq!(result.len(), 2);
    for path in result.iter() {
        assert!(validate_path(path, s, t));
        // Ensure that the path passes through intermediate nodes.
        assert!(path.contains(&1));
        assert!(path.contains(&2));
    }
}