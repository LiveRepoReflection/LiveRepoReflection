use std::collections::{HashMap, HashSet};
use byzantine_broadcast::broadcast;

#[test]
fn test_no_byzantine() {
    // A simple graph with 4 nodes and no Byzantine nodes.
    let n = 4;
    let edges = vec![
        (0, 1), (0, 2), (0, 3),
        (1, 2), (2, 3)
    ];
    let e = edges.len();
    let source = 0;
    let byzantine = HashSet::new();
    let message = 42;
    let result: HashMap<usize, i32> = broadcast(n, e, &edges, source, &byzantine, message);

    // Every node should have agreed on the source's message.
    for node in 0..n {
        assert!(result.contains_key(&node));
        assert_eq!(result[&node], 42);
    }
}

#[test]
fn test_with_byzantine() {
    // A graph with 6 nodes and one Byzantine node.
    let n = 6;
    let edges = vec![
        (0, 1), (0, 2),
        (1, 3), (2, 3),
        (3, 4), (4, 5),
        (2, 5), (1, 2),
        (5, 1)
    ];
    let e = edges.len();
    let source = 0;
    let mut byzantine = HashSet::new();
    // Mark node 3 as Byzantine.
    byzantine.insert(3);
    let message = 99;
    let result: HashMap<usize, i32> = broadcast(n, e, &edges, source, &byzantine, message);

    // All honest nodes should agree on the source's message.
    for node in 0..n {
        if !byzantine.contains(&node) {
            assert!(result.contains_key(&node));
            assert_eq!(result[&node], 99);
        } else {
            // Byzantine node may have an arbitrary value, but it should still be present in the result.
            assert!(result.contains_key(&node));
        }
    }
}

#[test]
fn test_source_byzantine() {
    // A graph where the source is Byzantine.
    let n = 5;
    let edges = vec![
        (0, 1), (0, 2),
        (1, 3), (2, 3),
        (3, 4), (1, 2)
    ];
    let e = edges.len();
    let source = 0;
    let mut byzantine = HashSet::new();
    // Mark the source node as Byzantine.
    byzantine.insert(0);
    let message = 123;
    let result: HashMap<usize, i32> = broadcast(n, e, &edges, source, &byzantine, message);

    // Honest nodes (1, 2, 3, 4) should all agree on the same value,
    // though it might not necessarily be the source's message.
    let mut honest_value = None;
    for node in 0..n {
        if !byzantine.contains(&node) {
            let value = result[&node];
            match honest_value {
                None => honest_value = Some(value),
                Some(v) => {
                    assert_eq!(v, value);
                }
            }
        }
    }
}

#[test]
fn test_cyclic_graph() {
    // A graph with cycles and self-contained cycles.
    let n = 7;
    let edges = vec![
        (0, 1), (1, 2), (2, 3), (3, 1), // Cycle among nodes 1, 2, 3.
        (2, 4), (4, 5), (5, 6), (6, 4), // Cycle among nodes 4, 5, 6.
        (0, 4), (3, 6)
    ];
    let e = edges.len();
    let source = 0;
    let byzantine = HashSet::new();
    let message = 555;
    let result: HashMap<usize, i32> = broadcast(n, e, &edges, source, &byzantine, message);

    // All nodes should eventually agree on the source's message.
    for node in 0..n {
        assert!(result.contains_key(&node));
        assert_eq!(result[&node], 555);
    }
}