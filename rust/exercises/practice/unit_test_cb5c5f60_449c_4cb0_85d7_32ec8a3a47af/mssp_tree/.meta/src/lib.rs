use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn optimal_mssp_tree(n: usize, edges: Vec<(usize, usize, usize)>, sources: Vec<usize>) -> isize {
    // Use u64 for distances and edge weights to avoid overflow.
    const INF: u64 = u64::MAX / 2;
    
    // Build the adjacency list.
    let mut adj: Vec<Vec<(usize, u64)>> = vec![Vec::new(); n];
    for (u, v, w) in edges {
        let weight = w as u64;
        // Avoid self-loops, they never help forming a tree.
        if u != v {
            adj[u].push((v, weight));
            adj[v].push((u, weight));
        }
    }
    
    // Multi-source Dijkstra.
    // For each vertex, store the shortest distance from any source.
    let mut dist: Vec<u64> = vec![INF; n];
    // For non-source vertices, store the edge weight that connected it to its parent in the tree.
    // For source vertices, cost is 0.
    let mut best_edge: Vec<u64> = vec![INF; n];
    
    // Priority queue: (distance, vertex, candidate_edge_weight)
    let mut heap: BinaryHeap<Reverse<(u64, usize, u64)>> = BinaryHeap::new();
    
    // Initialize sources.
    for &src in sources.iter() {
        if src >= n {
            // Source index out of range, immediately fail.
            return -1;
        }
        dist[src] = 0;
        best_edge[src] = 0;
        heap.push(Reverse((0, src, 0)));
    }
    
    // Perform Dijkstra.
    while let Some(Reverse((d, u, edge_cost))) = heap.pop() {
        if d > dist[u] {
            continue;
        }
        // Explore neighbors.
        for &(v, w) in &adj[u] {
            let candidate = d.saturating_add(w);
            if candidate < dist[v] {
                dist[v] = candidate;
                best_edge[v] = w;
                heap.push(Reverse((candidate, v, w)));
            } else if candidate == dist[v] && w < best_edge[v] {
                best_edge[v] = w;
                heap.push(Reverse((candidate, v, w)));
            }
        }
    }
    
    // Check that every vertex is reachable.
    for d in &dist {
        if *d == INF {
            return -1;
        }
    }
    
    // Sum the parent edge weights for non-source vertices.
    // Note: for source vertices, best_edge is 0.
    let total: u64 = best_edge.iter().sum();
    
    // Check for potential overflow for isize conversion.
    if total > (isize::max_value() as u64) {
        return -1;
    }
    total as isize
}

#[cfg(test)]
mod tests {
    use super::optimal_mssp_tree;

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
}