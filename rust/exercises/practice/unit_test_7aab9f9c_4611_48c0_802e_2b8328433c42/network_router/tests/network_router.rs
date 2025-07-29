use network_router::can_reach_destination;

#[test]
fn test_basic_path() {
    let edges = vec![(0, 1, 1), (1, 2, 2)];
    assert!(can_reach_destination(3, &edges, 0, 2, 5));
    assert!(!can_reach_destination(3, &edges, 0, 2, 2));
}

#[test]
fn test_no_path_exists() {
    let edges = vec![(0, 1, 1), (2, 3, 1)];
    assert!(!can_reach_destination(4, &edges, 0, 3, 10));
}

#[test]
fn test_zero_cost_edges() {
    let edges = vec![(0, 1, 0), (1, 2, 0), (2, 3, 0)];
    assert!(can_reach_destination(4, &edges, 0, 3, 0));
}

#[test]
fn test_self_loops() {
    let edges = vec![(0, 0, 1), (0, 1, 2)];
    assert!(can_reach_destination(2, &edges, 0, 1, 2));
}

#[test]
fn test_multiple_paths() {
    let edges = vec![
        (0, 1, 1),
        (1, 2, 4),
        (0, 3, 2),
        (3, 2, 2),
    ];
    assert!(can_reach_destination(4, &edges, 0, 2, 4));
}

#[test]
fn test_invalid_node_ids() {
    let edges = vec![(0, 1, 1)];
    assert!(!can_reach_destination(2, &edges, 0, 5, 10));
    assert!(!can_reach_destination(2, &edges, 5, 0, 10));
}

#[test]
fn test_large_graph() {
    let mut edges = Vec::new();
    for i in 0..999 {
        edges.push((i, i + 1, 1));
    }
    assert!(can_reach_destination(1000, &edges, 0, 999, 999));
    assert!(!can_reach_destination(1000, &edges, 0, 999, 998));
}

#[test]
fn test_cycle_in_graph() {
    let edges = vec![
        (0, 1, 1),
        (1, 2, 1),
        (2, 0, 1),
        (1, 3, 2),
    ];
    assert!(can_reach_destination(4, &edges, 0, 3, 3));
}

#[test]
fn test_exact_cost_limit() {
    let edges = vec![(0, 1, 5), (1, 2, 5)];
    assert!(can_reach_destination(3, &edges, 0, 2, 10));
    assert!(!can_reach_destination(3, &edges, 0, 2, 9));
}

#[test]
fn test_single_node() {
    let edges = Vec::new();
    assert!(can_reach_destination(1, &edges, 0, 0, 0));
}

#[test]
fn test_multiple_edges_between_same_nodes() {
    let edges = vec![
        (0, 1, 5),
        (0, 2, 2),
        (2, 1, 1),
    ];
    assert!(can_reach_destination(3, &edges, 0, 1, 3));
}

#[test]
fn test_edge_cases() {
    // Empty edge list
    assert!(can_reach_destination(2, &[], 0, 0, 0));
    assert!(!can_reach_destination(2, &[], 0, 1, 0));

    // Maximum cost
    let edges = vec![(0, 1, 1000)];
    assert!(can_reach_destination(2, &edges, 0, 1, 1000));
    assert!(!can_reach_destination(2, &edges, 0, 1, 999));
}