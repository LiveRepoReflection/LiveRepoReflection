use network_partition::min_resilience_loss;

#[test]
fn test_connected_k1() {
    // A connected tree with 5 nodes and 4 edges.
    // For k = 1, the network is already one component so no removals are needed.
    let n = 5;
    let k = 1;
    let edges = vec![
        (0, 1, 5),
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 2)
    ];
    assert_eq!(min_resilience_loss(n, k, edges), 0);
}

#[test]
fn test_example() {
    // Provided example from the problem statement.
    let n = 4;
    let k = 2;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 5),
        (2, 3, 3),
        (3, 0, 7),
        (0, 2, 2)
    ];
    assert_eq!(min_resilience_loss(n, k, edges), 10);
}

#[test]
fn test_no_edges_impossible() {
    // A graph with no edges: each node is isolated.
    // Removing edges cannot reduce the number of connected components.
    // For n = 4 and k = 3, the graph already has 4 components so it is impossible.
    let n = 4;
    let k = 3;
    let edges: Vec<(usize, usize, usize)> = vec![];
    assert_eq!(min_resilience_loss(n, k, edges), -1);
}

#[test]
fn test_already_disconnected_and_impossible() {
    // A graph that is initially disconnected into 2 components:
    // Component 1: nodes {0, 1}
    // Component 2: nodes {2, 3, 4, 5}
    // For k = 1, it is impossible to merge components by removing edges.
    let n = 6;
    let k = 1;
    let edges = vec![
        (0, 1, 7),
        (2, 3, 10),
        (3, 4, 2),
        (4, 5, 1),
        (2, 5, 15)
    ];
    assert_eq!(min_resilience_loss(n, k, edges), -1);
}

#[test]
fn test_complex_case() {
    // A more involved graph:
    // Graph: Nodes 0-5 with the following edges:
    // (0,1,10), (1,2,8), (2,0,6) form a cycle.
    // (3,4,5), (4,5,4), (5,3,3) form another cycle.
    // (2,3,2) connects the two cycles.
    // Total resilience of all edges = 10+8+6+5+4+3+2 = 38.
    // For k = 3, we need a forest with 6 - 3 = 3 edges.
    // One optimal partition is to have trees: {0,1,2}, {3,4}, {5}.
    // Maximum weights kept: (0,1,10) and (1,2,8) in the first tree, (3,4,5) in the second tree.
    // Sum kept = 10 + 8 + 5 = 23.
    // Hence, minimum resilience loss = 38 - 23 = 15.
    let n = 6;
    let k = 3;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 8),
        (2, 0, 6),
        (3, 4, 5),
        (4, 5, 4),
        (5, 3, 3),
        (2, 3, 2)
    ];
    assert_eq!(min_resilience_loss(n, k, edges), 15);
}

#[test]
fn test_cycle_k2_and_k3() {
    // A simple cycle graph with 3 nodes.
    // Edges: (0,1,1), (1,2,2), (2,0,3).
    // Total resilience = 1 + 2 + 3 = 6.
    // For k = 2: forest will have 3 - 2 = 1 edge.
    // The maximum available edge is (2,0,3), so kept sum = 3 and loss = 6 - 3 = 3.
    // For k = 3: no edges are kept, so loss = 6.
    let n = 3;
    let edges = vec![
        (0, 1, 1),
        (1, 2, 2),
        (2, 0, 3)
    ];
    assert_eq!(min_resilience_loss(n, 2, edges.clone()), 3);
    assert_eq!(min_resilience_loss(n, 3, edges), 6);
}