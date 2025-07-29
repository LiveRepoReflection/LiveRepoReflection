use network_optimus::min_average_cost;

fn approx_eq(a: f64, b: f64, eps: f64) -> bool {
    (a - b).abs() < eps
}

#[test]
fn test_disconnected_graph() {
    // n = 4 with no edges should be disconnected.
    let n = 4;
    let edges: Vec<(usize, usize, u32)> = vec![];
    // Even with k == 1, since there is no connectivity, should return None.
    let k = 1;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_none(), "Expected None for disconnected graph");
}

#[test]
fn test_simple_graph_k1() {
    // Graph:
    // 0 --1-- 1
    // 1 --2-- 2
    // 0 --4-- 2
    // For k = 1, every pair is connected.
    // Minimal costs:
    // 0-1: 1
    // 1-2: 2
    // 0-2: min(4, 1+2) = 3
    // Average = (1 + 2 + 3) / 3 = 2.0
    let n = 3;
    let edges = vec![(0, 1, 1), (1, 2, 2), (0, 2, 4)];
    let k = 1;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_some(), "Expected Some(_) for connected graph with k=1");
    let avg = result.unwrap();
    assert!(approx_eq(avg, 2.0, 1e-6), "Expected 2.0, got {}", avg);
}

#[test]
fn test_insufficient_paths() {
    // Graph with a single unique path between some nodes.
    // Graph:
    // 0 --1-- 1
    // 1 --2-- 2
    // There is only one path between 0 and 2.
    // For k = 2, it should return None.
    let n = 3;
    let edges = vec![(0, 1, 1), (1, 2, 2)];
    let k = 2;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_none(), "Expected None when not enough distinct paths are available");
}

#[test]
fn test_multiple_paths() {
    // Graph:
    // There are multiple edges between nodes 0 and 1, and between 1 and 2.
    // Edges:
    // 0-1: 1 and 2
    // 1-2: 1 and 3
    // 0-2: 5 (single edge)
    //
    // For k = 2, we need at least two distinct paths between every pair.
    // For pair (0,1), two disjoint edges exist: cost = 1 and 2, so minimal cost is 1.
    // For pair (1,2), two disjoint edges exist: cost = 1 and 3, so minimal cost is 1.
    // For pair (0,2), one valid route is 0-1 (using edge cost=1) and 1-2 (using edge cost=1) -> cost 2.
    // The alternative direct edge (0-2) cost=5 gives the second distinct path.
    // Average = (1 + 1 + 2) / 3 ≈ 1.333333
    let n = 3;
    let edges = vec![
        (0, 1, 1),
        (0, 1, 2),
        (1, 2, 1),
        (1, 2, 3),
        (0, 2, 5),
    ];
    let k = 2;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_some(), "Expected Some(_) when k distinct paths exist for all pairs");
    let avg = result.unwrap();
    assert!(approx_eq(avg, 1.333333, 1e-6), "Expected approximately 1.333333, got {}", avg);
}

#[test]
fn test_chain_graph_k1() {
    // Chain graph: 0-1-2-3-4 with edges:
    // 0-1: 1, 1-2: 2, 2-3: 3, 3-4: 4
    // For k = 1, the minimal cost between any two nodes is the sum of the edge weights on the unique path.
    // Pair distances:
    // 0-1: 1, 0-2: 3, 0-3: 6, 0-4: 10,
    // 1-2: 2, 1-3: 5, 1-4: 9,
    // 2-3: 3, 2-4: 7,
    // 3-4: 4.
    // Sum = 1+3+6+10+2+5+9+3+7+4 = 50, count = 10, expected average = 5.0.
    let n = 5;
    let edges = vec![(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4)];
    let k = 1;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_some(), "Expected Some(_) for chain graph with k=1");
    let avg = result.unwrap();
    assert!(approx_eq(avg, 5.0, 1e-6), "Expected 5.0, got {}", avg);
}

#[test]
fn test_cycle_graph_k2() {
    // Cycle graph with an extra chord to allow two distinct paths.
    // Graph:
    // 0 --1-- 1
    // 1 --2-- 2
    // 2 --3-- 3
    // 3 --4-- 0
    // Extra edge: 1 --1-- 3
    //
    // With k = 2, every pair should have at least two distinct paths.
    // We do not compute the exact average here, but we ensure that a valid average is returned.
    let n = 4;
    let edges = vec![
        (0, 1, 1),
        (1, 2, 2),
        (2, 3, 3),
        (3, 0, 4),
        (1, 3, 1),
    ];
    let k = 2;
    let result = min_average_cost(n, edges, k);
    assert!(result.is_some(), "Expected Some(_) for cycle graph with sufficient distinct paths");
    let avg = result.unwrap();
    // We only check that the returned average is a finite number.
    assert!(avg.is_finite(), "Average should be a finite number");
}