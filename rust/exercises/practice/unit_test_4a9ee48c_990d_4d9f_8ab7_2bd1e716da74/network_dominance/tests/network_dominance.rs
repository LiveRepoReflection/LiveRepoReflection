use network_dominance::find_dominant_users;

#[test]
fn test_single_node_dominant() {
    // Single node with no edges; node should be dominant if k == 1, otherwise not.
    let n = 1;
    let edges = vec![];
    let k1 = 1;
    let k2 = 2;
    let result_k1 = find_dominant_users(n, edges.clone(), k1);
    assert_eq!(result_k1, vec![0]);
    let result_k2 = find_dominant_users(n, edges, k2);
    assert_eq!(result_k2, Vec::<usize>::new());
}

#[test]
fn test_linear_graph() {
    // Graph: 0 -> 1, 1 -> 2
    // Reachability:
    // 0: {0, 1, 2}  (count = 3)
    // 1: {1, 2}     (count = 2)
    // 2: {2}        (count = 1)
    let n = 3;
    let edges = vec![(0, 1), (1, 2)];
    let res_k1 = find_dominant_users(n, edges.clone(), 1);
    assert_eq!(res_k1, vec![0, 1, 2]);
    let res_k2 = find_dominant_users(n, edges.clone(), 2);
    assert_eq!(res_k2, vec![0, 1]);
    let res_k3 = find_dominant_users(n, edges, 3);
    assert_eq!(res_k3, vec![0]);
}

#[test]
fn test_cycle_graph() {
    // Cycle: 0 -> 1, 1 -> 2, 2 -> 0
    // Every node can reach all nodes in the cycle.
    let n = 3;
    let edges = vec![(0, 1), (1, 2), (2, 0)];
    let res_k1 = find_dominant_users(n, edges.clone(), 1);
    assert_eq!(res_k1, vec![0, 1, 2]);
    let res_k2 = find_dominant_users(n, edges.clone(), 2);
    assert_eq!(res_k2, vec![0, 1, 2]);
    let res_k3 = find_dominant_users(n, edges, 3);
    assert_eq!(res_k3, vec![0, 1, 2]);
}

#[test]
fn test_disconnected_graph() {
    // Disconnected graph with 5 nodes:
    // Component 1: Cycle between 0 and 1 (0 <-> 1).
    // Component 2: Chain from 2 -> 3.
    // Component 3: Isolated node 4.
    // Reachability:
    // 0: {0,1}  (count = 2)
    // 1: {0,1}  (count = 2)
    // 2: {2,3}  (count = 2)
    // 3: {3}    (count = 1)
    // 4: {4}    (count = 1)
    let n = 5;
    let edges = vec![(0, 1), (1, 0), (2, 3)];
    let res_k1 = find_dominant_users(n, edges.clone(), 1);
    assert_eq!(res_k1, vec![0, 1, 2, 3, 4]);
    let res_k2 = find_dominant_users(n, edges.clone(), 2);
    assert_eq!(res_k2, vec![0, 1, 2]);
    let res_k3 = find_dominant_users(n, edges, 3);
    assert_eq!(res_k3, Vec::<usize>::new());
}

#[test]
fn test_self_loops() {
    // Graph with self-loop: 0 -> 0 and 0 -> 1.
    // Even with the self-loop, node 0 should count {0, 1} only once.
    let n = 2;
    let edges = vec![(0, 0), (0, 1)];
    let res_k1 = find_dominant_users(n, edges.clone(), 1);
    assert_eq!(res_k1, vec![0, 1]);
    let res_k2 = find_dominant_users(n, edges, 2);
    assert_eq!(res_k2, vec![0]);
}

#[test]
fn test_duplicate_edges() {
    // Duplicate edges should be treated as a single edge.
    // Graph: 0 -> 1 (twice), 1 -> 2 (thrice).
    // Reachability:
    // 0: {0, 1, 2}  (count = 3)
    // 1: {1, 2}     (count = 2)
    // 2: {2}        (count = 1)
    let n = 3;
    let edges = vec![(0, 1), (0, 1), (1, 2), (1, 2), (1, 2)];
    let res = find_dominant_users(n, edges, 3);
    assert_eq!(res, vec![0]);
}

#[test]
fn test_complex_graph() {
    // Complex graph with branching and cycles:
    // Structure:
    // 0 -> 1, 0 -> 2
    // 1 -> 2, 1 -> 3
    // 2 -> 0 (creates a cycle among 0, 1, 2)
    // 3 -> 4
    // 4 -> 5
    // 5 -> 3 (creates a cycle among 3, 4, 5)
    // Reachability:
    // Nodes 0, 1, 2: can reach all nodes {0, 1, 2, 3, 4, 5} (count = 6)
    // Nodes 3, 4, 5: can reach only their cycle {3, 4, 5} (count = 3)
    let n = 6;
    let edges = vec![
        (0, 1), (0, 2),
        (1, 2), (1, 3),
        (2, 0),
        (3, 4),
        (4, 5),
        (5, 3)
    ];
    let res_k6 = find_dominant_users(n, edges.clone(), 6);
    assert_eq!(res_k6, vec![0, 1, 2]);
    let res_k3 = find_dominant_users(n, edges, 3);
    assert_eq!(res_k3, vec![0, 1, 2, 3, 4, 5]);
}