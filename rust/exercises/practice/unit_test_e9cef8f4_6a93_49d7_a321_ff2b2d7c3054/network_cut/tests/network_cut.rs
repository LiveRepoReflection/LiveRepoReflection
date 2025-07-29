use network_cut::min_cut;

#[test]
fn example_test() {
    let n = 5;
    let edges = vec![(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)];
    let k = 2;
    let result = min_cut(n, edges, k);
    assert_eq!(result, 1);
}

#[test]
fn already_partitioned() {
    // Graph where vertex 0 is isolated, and the remaining vertices form a connected component.
    let n = 6;
    let edges = vec![(1, 2), (2, 3), (3, 4), (4, 5)];
    let k = 1; // component {0} is already isolated.
    let result = min_cut(n, edges, k);
    assert_eq!(result, 0);
}

#[test]
fn triangle_complete() {
    // Complete graph of 3 nodes (triangle).
    let n = 3;
    let edges = vec![(0, 1), (1, 2), (0, 2)];
    let k = 1;
    let result = min_cut(n, edges, k);
    // Optimal cut: remove 2 edges to isolate one vertex.
    assert_eq!(result, 2);
}

#[test]
fn star_graph() {
    // Star graph with center node 0.
    let n = 5;
    let edges = vec![(0, 1), (0, 2), (0, 3), (0, 4)];
    let k = 1;
    let result = min_cut(n, edges, k);
    // Removing any one edge isolates a leaf.
    assert_eq!(result, 1);
}

#[test]
fn chain_graph() {
    // Chain graph where vertices form a straight line.
    let n = 4;
    let edges = vec![(0, 1), (1, 2), (2, 3)];
    let k = 1;
    let result = min_cut(n, edges, k);
    // Best strategy: remove an edge incident to an end vertex.
    assert_eq!(result, 1);
}

#[test]
fn no_edges() {
    // Graph with no edges, every vertex is isolated.
    let n = 4;
    let edges = Vec::new();
    let k = 1;
    let result = min_cut(n, edges, k);
    // Already partitioned with isolated vertices.
    assert_eq!(result, 0);
}

#[test]
fn dense_graph_complete() {
    // Complete graph on 6 nodes.
    let n = 6;
    let mut edges = Vec::new();
    for i in 0..n {
        for j in (i + 1)..n {
            edges.push((i, j));
        }
    }
    let k = 2;
    let result = min_cut(n, edges, k);
    // Optimal cut: isolate one vertex; cost = n - 1 = 5.
    assert_eq!(result, 5);
}