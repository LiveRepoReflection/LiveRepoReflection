use k_anon_graph::anonymize_graph;

fn sort_edges(mut edges: Vec<(usize, usize)>) -> Vec<(usize, usize)> {
    // Ensure each edge is represented with the smaller node first.
    for edge in edges.iter_mut() {
        if edge.0 > edge.1 {
            std::mem::swap(&mut edge.0, &mut edge.1);
        }
    }
    edges.sort();
    edges
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_already_k_anonymous() {
        let n = 3;
        let edges = vec![(0, 1), (1, 2), (0, 2)];
        let k = 2;
        let result = anonymize_graph(n, edges.clone(), k);
        // The input is already k-anonymous, so the graph should remain the same.
        let expected = sort_edges(edges);
        let res = sort_edges(result);
        assert_eq!(res, expected);
    }

    #[test]
    fn test_empty_graph() {
        let n = 0;
        let edges = vec![];
        let k = 1;
        let result = anonymize_graph(n, edges, k);
        // An empty graph should result in an empty output.
        assert!(result.is_empty());
    }

    #[test]
    fn test_self_loops_removed() {
        let n = 3;
        let edges = vec![(0, 0), (0, 1), (1, 2), (2, 2)];
        let k = 1;
        let result = anonymize_graph(n, edges, k);
        // Self-loops should be removed. Expected remaining edges: (0,1) and (1,2).
        let expected = sort_edges(vec![(0, 1), (1, 2)]);
        let res = sort_edges(result);
        assert_eq!(res, expected);
    }

    #[test]
    fn test_disconnected_components() {
        let n = 6;
        let edges = vec![(0, 1), (0, 2), (1, 2), (3, 4), (4, 5)];
        let k = 2;
        let result = anonymize_graph(n, edges, k);
        // The first component (0,1,2) forms a triangle with each node having degree 2.
        // The second component (3,4,5) is a chain where nodes 3 and 5 have degree 1 and 4 has degree 2.
        // Only the first component can be retained as k-anonymous.
        let expected = sort_edges(vec![(0, 1), (0, 2), (1, 2)]);
        let res = sort_edges(result);
        assert_eq!(res, expected);
    }

    #[test]
    fn test_infeasible_case() {
        let n = 4;
        let edges = vec![(0, 1), (0, 2), (0, 3)];
        let k = 3;
        let result = anonymize_graph(n, edges, k);
        // It is impossible to achieve a 3-anonymous graph in this configuration, so return an empty vector.
        assert!(result.is_empty());
    }

    #[test]
    fn test_minimal_deletion() {
        // Graph configuration:
        // n = 5
        // Edges: (0,1), (1,2), (0,2) form a triangle (all nodes degree 2)
        //       (2,3) and (3,4) form a chain (nodes 3 and 4 have degree 1)
        // With k = 2, the minimal deletion is to remove nodes 3 and 4 entirely.
        let n = 5;
        let edges = vec![(0, 1), (1, 2), (0, 2), (2, 3), (3, 4)];
        let k = 2;
        let result = anonymize_graph(n, edges, k);
        let expected = sort_edges(vec![(0, 1), (0, 2), (1, 2)]);
        let res = sort_edges(result);
        assert_eq!(res, expected);
    }
}