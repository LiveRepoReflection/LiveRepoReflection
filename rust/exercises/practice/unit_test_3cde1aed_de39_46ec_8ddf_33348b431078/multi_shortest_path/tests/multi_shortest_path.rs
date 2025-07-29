use multi_shortest_path::multi_source_shortest_path;

#[test]
fn test_linear_graph() {
    // Graph: 0 -> 1 (2), 1 -> 2 (2), 2 -> 3 (2), 3 -> 4 (2)
    let num_nodes = 5;
    let edges = vec![(0, 1, 2), (1, 2, 2), (2, 3, 2), (3, 4, 2)];
    let sources = vec![0];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    let expected = vec![0, 2, 4, 6, 8];
    assert_eq!(result, expected);
}

#[test]
fn test_multiple_sources() {
    // Graph: 0 -> 1 (1), 2 -> 1 (1), 1 -> 3 (2)
    let num_nodes = 4;
    let edges = vec![(0, 1, 1), (2, 1, 1), (1, 3, 2)];
    let sources = vec![0, 2];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    // Expected: node0: 0, node1: 1, node2: 0, node3: 3
    let expected = vec![0, 1, 0, 3];
    assert_eq!(result, expected);
}

#[test]
fn test_disconnected_graph() {
    // Graph: 0 -> 1 (10) and nodes 2 and 3 remain disconnected.
    let num_nodes = 4;
    let edges = vec![(0, 1, 10)];
    let sources = vec![0];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    // Expected: node0: 0, node1: 10, node2: -1, node3: -1
    let expected = vec![0, 10, -1, -1];
    assert_eq!(result, expected);
}

#[test]
fn test_cycle_graph() {
    // Graph with a cycle: 0 -> 1 (3), 1 -> 2 (4), 2 -> 0 (5), and 1 -> 3 (2)
    let num_nodes = 4;
    let edges = vec![(0, 1, 3), (1, 2, 4), (2, 0, 5), (1, 3, 2)];
    let sources = vec![0];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    // Expected distances: 0:0, 1:3, 2:7, 3:5
    let expected = vec![0, 3, 7, 5];
    assert_eq!(result, expected);
}

#[test]
fn test_multiple_sources_complex() {
    // Graph: nodes = 6, edges: 0 -> 1 (2), 1 -> 2 (2), 2 -> 3 (2), 1 -> 4 (5), 5 -> 2 (1)
    let num_nodes = 6;
    let edges = vec![(0, 1, 2), (1, 2, 2), (2, 3, 2), (1, 4, 5), (5, 2, 1)];
    let sources = vec![0, 5];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    // Expected distances:
    // From source 0: 0:0, 1:2, 2:4, 3:6, 4:7.
    // From source 5: 5:0, 2:1, 3:3.
    // Combined best distances: [0, 2, 1, 3, 7, 0]
    let expected = vec![0, 2, 1, 3, 7, 0];
    assert_eq!(result, expected);
}

#[test]
fn test_duplicate_edges() {
    // Graph with duplicate edges: two edges from 0 -> 1 (weights 4 and 2), 1 -> 2 (3)
    let num_nodes = 3;
    let edges = vec![(0, 1, 4), (0, 1, 2), (1, 2, 3)];
    let sources = vec![0];
    let result = multi_source_shortest_path(num_nodes, edges, sources);
    // Expected distances: 0:0, 1:2, 2:5
    let expected = vec![0, 2, 5];
    assert_eq!(result, expected);
}