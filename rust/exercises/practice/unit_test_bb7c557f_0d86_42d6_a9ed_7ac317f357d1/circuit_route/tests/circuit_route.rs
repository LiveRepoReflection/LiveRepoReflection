use circuit_route::minimal_delay;

#[test]
fn test_empty_start_components() {
    // When no start components, function should return -1.
    let n = 3;
    let edges = vec![(0, 1, 3), (1, 2, 4)];
    let start_components = vec![];
    let end_components = vec![2];
    let max_allowed_delay = 10;
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), -1);
}

#[test]
fn test_empty_end_components() {
    // When no end components, function should return -1.
    let n = 3;
    let edges = vec![(0, 1, 3), (1, 2, 4)];
    let start_components = vec![0];
    let end_components = vec![];
    let max_allowed_delay = 10;
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), -1);
}

#[test]
fn test_simple_valid_connection() {
    // Simple graph with two nodes connected directly.
    let n = 2;
    let edges = vec![(0, 1, 5)];
    let start_components = vec![0];
    let end_components = vec![1];
    let max_allowed_delay = 5;
    // The only path delay is 5.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), 5);
}

#[test]
fn test_simple_exceed_delay() {
    // Same graph as before but the allowed delay is less than the edge weight.
    let n = 2;
    let edges = vec![(0, 1, 5)];
    let start_components = vec![0];
    let end_components = vec![1];
    let max_allowed_delay = 4;
    // No valid path exists under delay constraint.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), -1);
}

#[test]
fn test_multiple_routes() {
    // Graph with multiple paths.
    // Graph:
    // 0 --2--> 1 --2--> 2 --2--> 3
    // 0 --------7----------> 3
    let n = 4;
    let edges = vec![(0, 1, 2), (1, 2, 2), (2, 3, 2), (0, 3, 7)];
    let start_components = vec![0, 1];
    let end_components = vec![2, 3];
    let max_allowed_delay = 6;
    // There is a valid path from 1 to 2 with delay 2.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), 2);
}

#[test]
fn test_disconnected_graph() {
    // Graph where start and end are in different disconnected components.
    // Graph:
    // 0 --1--> 1, and 2 --1--> 3; node 4 isolated.
    let n = 5;
    let edges = vec![(0, 1, 1), (2, 3, 1)];
    let start_components = vec![0];
    let end_components = vec![3];
    let max_allowed_delay = 5;
    // There is no path between node 0 and node 3.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), -1);
}

#[test]
fn test_complex_route_with_multiple_paths() {
    // Graph:
    // 0 --1--> 1 --1--> 2 --10--> 3
    // 0 --2--> 4 --2--> 3
    // 3 --1--> 5
    let n = 6;
    let edges = vec![
        (0, 1, 1),
        (1, 2, 1),
        (2, 3, 10),
        (0, 4, 2),
        (4, 3, 2),
        (3, 5, 1)
    ];
    let start_components = vec![0];
    let end_components = vec![3, 5];
    let max_allowed_delay = 5;
    // Possibility: 0 -> 4 -> 3 with total delay 4.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), 4);
}

#[test]
fn test_multiple_start_and_end_nodes() {
    // Graph with cycles and multiple possible routes.
    // Graph:
    // 0 --1--> 1 --1--> 2 --1--> 3
    // 0 --2--> 4 --2--> 5 --2--> 6
    // 3 --4--> 6
    let n = 7;
    let edges = vec![
        (0, 1, 1),
        (1, 2, 1),
        (2, 3, 1),
        (0, 4, 2),
        (4, 5, 2),
        (5, 6, 2),
        (3, 6, 4)
    ];
    let start_components = vec![0, 4];
    let end_components = vec![3, 6];
    let max_allowed_delay = 4;
    // Valid path: 0 -> 1 -> 2 -> 3 with delay 3.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), 3);
}

#[test]
fn test_large_chain_graph() {
    // Create a large chain graph with 10000 nodes.
    // The chain: 0 -1-> 1 -1-> 2 ... such that the path delay is the number of edges.
    let n = 10000;
    let mut edges = Vec::with_capacity(n - 1);
    for i in 0..n-1 {
        edges.push((i, i+1, 1));
    }
    let start_components = vec![0];
    let end_components = vec![n - 1];
    let max_allowed_delay = 10000;
    // Minimal delay should be n-1.
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), (n - 1) as i64);
}

#[test]
fn test_large_chain_exceed_delay() {
    // Create the same large chain but set max_allowed_delay too low.
    let n = 10000;
    let mut edges = Vec::with_capacity(n - 1);
    for i in 0..n-1 {
        edges.push((i, i+1, 1));
    }
    let start_components = vec![0];
    let end_components = vec![n - 1];
    let max_allowed_delay = 5000; // too low for a chain of n-1 = 9999
    assert_eq!(minimal_delay(n, edges, start_components, end_components, max_allowed_delay), -1);
}