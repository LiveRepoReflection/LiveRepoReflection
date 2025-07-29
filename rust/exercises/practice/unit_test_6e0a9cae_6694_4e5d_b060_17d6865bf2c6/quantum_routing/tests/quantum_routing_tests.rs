use std::collections::HashSet;
use quantum_routing::find_k_paths;

#[test]
fn test_broken_node_single_path() {
    let n = 5;
    let edges = vec![
        (0, 1, 10),
        (0, 2, 15),
        (1, 2, 5),
        (1, 3, 20),
        (2, 3, 10),
        (3, 4, 5),
    ];
    let start = 0;
    let end = 4;
    let k = 2;
    let broken_nodes: HashSet<usize> = [2].iter().cloned().collect();

    let result = find_k_paths(n, edges, start, end, k, broken_nodes);
    let expected: Vec<Vec<usize>> = vec![vec![0, 1, 3, 4]];

    assert_eq!(result, expected);
}

#[test]
fn test_multiple_paths() {
    let n = 5;
    let edges = vec![
        (0, 1, 2),
        (1, 4, 2),
        (0, 2, 2),
        (2, 4, 2),
        (0, 3, 5),
        (3, 4, 1),
    ];
    let start = 0;
    let end = 4;
    let k = 2;
    let broken_nodes: HashSet<usize> = HashSet::new();

    let result = find_k_paths(n, edges, start, end, k, broken_nodes);
    // The two best edge-disjoint paths should be:
    // Path 1: 0 -> 1 -> 4  (Cost: 2+2=4, Hops: 2)
    // Path 2: 0 -> 2 -> 4  (Cost: 2+2=4, Hops: 2)
    let expected: Vec<Vec<usize>> = vec![vec![0, 1, 4], vec![0, 2, 4]];

    assert_eq!(result, expected);
}

#[test]
fn test_no_path_due_to_broken_nodes() {
    let n = 3;
    let edges = vec![
        (0, 1, 1),
        (1, 2, 1),
    ];
    let start = 0;
    let end = 2;
    let k = 2;
    let broken_nodes: HashSet<usize> = [1].iter().cloned().collect();

    let result = find_k_paths(n, edges, start, end, k, broken_nodes);
    let expected: Vec<Vec<usize>> = vec![];

    assert_eq!(result, expected);
}

#[test]
fn test_insufficient_paths() {
    let n = 4;
    let edges = vec![
        (0, 1, 3),
        (1, 3, 4),
        (0, 2, 5),
        (2, 3, 6),
    ];
    let start = 0;
    let end = 3;
    let k = 3;
    let broken_nodes: HashSet<usize> = HashSet::new();

    // Available disjoint paths:
    // Path 1: 0 -> 1 -> 3 (Cost = 7, Hops = 2)
    // Path 2: 0 -> 2 -> 3 (Cost = 11, Hops = 2)
    // Only two edge-disjoint paths exist.
    let result = find_k_paths(n, edges, start, end, k, broken_nodes);
    let expected: Vec<Vec<usize>> = vec![vec![0, 1, 3], vec![0, 2, 3]];

    assert_eq!(result, expected);
}

#[test]
fn test_priority_by_hops() {
    let n = 5;
    let edges = vec![
        (0, 1, 4),
        (1, 4, 5),
        (0, 2, 4),
        (2, 3, 2),
        (3, 4, 3),
    ];
    let start = 0;
    let end = 4;
    let k = 2;
    let broken_nodes: HashSet<usize> = HashSet::new();

    // Two disjoint paths exist with equal total cost:
    // Path 1: 0 -> 1 -> 4  (Cost = 9, Hops = 2)
    // Path 2: 0 -> 2 -> 3 -> 4  (Cost = 9, Hops = 3)
    // The path with fewer hops should be prioritized.
    let result = find_k_paths(n, edges, start, end, k, broken_nodes);
    let expected: Vec<Vec<usize>> = vec![vec![0, 1, 4], vec![0, 2, 3, 4]];

    assert_eq!(result, expected);
}