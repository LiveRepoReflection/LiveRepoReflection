use std::collections::HashSet;
use std::collections::VecDeque;

// We assume that the solution function is defined as follows in the library:
// pub fn optimal_mssp_tree(n: usize, edges: Vec<(usize, usize, usize)>, sources: Vec<usize>) -> isize;

use mssp_tree::optimal_mssp_tree;

#[test]
fn test_single_node() {
    let n = 1;
    let edges = vec![];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 0);
}

#[test]
fn test_linear_graph() {
    // Graph: 0 --10--> 1 --5--> 2
    let n = 3;
    let edges = vec![(0, 1, 10), (1, 2, 5)];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 15);
}

#[test]
fn test_disconnected_graph() {
    // Graph: 0--10--1 and 2--10--3, only one source in first component.
    let n = 4;
    let edges = vec![(0, 1, 10), (2, 3, 10)];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, -1);
}

#[test]
fn test_duplicate_and_self_loop() {
    // Graph: (0,0,100) self loop, duplicate edges (0,1,10) and (0,1,15), (1,2,5)
    let n = 3;
    let edges = vec![(0, 0, 100), (0, 1, 10), (0, 1, 15), (1, 2, 5)];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    // Expected tree uses edge (0,1,10) and (1,2,5)
    assert_eq!(result, 15);
}

#[test]
fn test_complex_tree() {
    // Graph:
    //   0-1:1, 0-2:4, 1-2:2, 1-3:5, 2-3:1
    // Expected MSSPT:
    //   From source 0, best paths: 0-1 (1), 1-2 (2), 2-3 (1) => total = 4.
    let n = 4;
    let edges = vec![(0, 1, 1), (0, 2, 4), (1, 2, 2), (1, 3, 5), (2, 3, 1)];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 4);
}

#[test]
fn test_multiple_sources() {
    // Graph:
    //   0-1:3, 1-2:1, 2-3:4, 3-4:3, 1-4:10
    // Sources: 0 and 2.
    // Expected:
    //   Vertex 1: reachable from 2 (edge 1-2 with weight 1)
    //   Vertex 3: reachable from 2 (edge 2-3 with weight 4)
    //   Vertex 4: reachable from 2: 2-3-4 (4+3=7) rather than 1-4 (10)
    // So, include edges: (1,2)=1, (2,3)=4, (3,4)=3. Total = 8.
    let n = 5;
    let edges = vec![(0, 1, 3), (1, 2, 1), (2, 3, 4), (3, 4, 3), (1, 4, 10)];
    let sources = vec![0, 2];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 8);
}

#[test]
fn test_cycle_graph() {
    // Graph with a cycle:
    //   0-1:2, 1-2:2, 2-0:2, 1-3:3
    // Source: 0.
    // The shortest path tree should include:
    //   Edge (0,1):2, Edge (1,3):3, and for vertex 2, either (0,2):2 or (1,2):2.
    // Total tree weight = 2 + 2 + 3 = 7.
    let n = 4;
    let edges = vec![(0, 1, 2), (1, 2, 2), (2, 0, 2), (1, 3, 3)];
    let sources = vec![0];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 7);
}

#[test]
fn test_all_vertices_source() {
    // Every vertex is a source.
    // In this case, we expect no edges need to be included since every vertex is its own optimal source.
    let n = 5;
    let edges = vec![(0, 1, 10), (1, 2, 20), (2, 3, 30), (3, 4, 40)];
    let sources = vec![0, 1, 2, 3, 4];
    let result = optimal_mssp_tree(n, edges, sources);
    assert_eq!(result, 0);
}