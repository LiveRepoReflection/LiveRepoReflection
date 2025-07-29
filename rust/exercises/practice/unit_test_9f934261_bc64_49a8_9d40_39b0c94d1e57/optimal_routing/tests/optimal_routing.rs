use optimal_routing::solve;

#[cfg(test)]
mod tests {
    use super::solve;

    #[test]
    fn test_simple_routing() {
        let n = 4;
        let edges = vec![
            (0, 1, 10, 5),
            (1, 2, 5, 2),
            (2, 3, 15, 10),
            (0, 3, 25, 3),
        ];
        let flows = vec![
            (0, 2, 1, 1),
            (1, 3, 2, 2),
            (0, 3, 1, 3),
        ];
        let l = 30;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 3);
    }

    #[test]
    fn test_latency_exceeded() {
        // Flow should not be routed if no path meets the maximum latency constraint.
        let n = 3;
        let edges = vec![
            (0, 1, 50, 10),
            (1, 2, 50, 10),
        ];
        let flows = vec![
            (0, 2, 5, 10),
        ];
        let l = 30;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 0);
    }

    #[test]
    fn test_bandwidth_limitation() {
        // Multiple flows share the same edges, causing bandwidth constraint to kick in.
        // Assume each packet requires bandwidth unit 1.
        let n = 3;
        let edges = vec![
            (0, 1, 10, 2),
            (1, 2, 10, 2),
        ];
        let flows = vec![
            (0, 2, 3, 1), // highest priority; should be routed first
            (0, 2, 2, 2),
            (0, 2, 1, 3),
        ];
        let l = 30;
        // Only two flows can share the edges because of bandwidth limitation.
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 2);
    }

    #[test]
    fn test_disconnected_graph() {
        // One flow has a reachable destination and one does not.
        let n = 4;
        let edges = vec![
            (0, 1, 10, 10),
            (1, 2, 10, 10),
        ]; // Node 3 is disconnected.
        let flows = vec![
            (0, 2, 1, 1),
            (0, 3, 2, 2),
        ];
        let l = 50;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 1);
    }

    #[test]
    fn test_equal_priorities_tie_break() {
        // When priorities are equal, tie-breaker is arbitrary but both flows can be routed if conditions permit.
        let n = 4;
        let edges = vec![
            (0, 1, 10, 5),
            (1, 3, 10, 5),
            (0, 2, 10, 5),
            (2, 3, 10, 5),
        ];
        let flows = vec![
            (0, 3, 5, 10),
            (0, 3, 5, 20),
        ];
        let l = 30;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 2);
    }

    #[test]
    fn test_multiple_paths() {
        // Complex graph where multiple distinct paths exist.
        let n = 5;
        let edges = vec![
            (0, 1, 5, 5),
            (1, 4, 5, 5),
            (0, 2, 10, 3),
            (2, 3, 10, 3),
            (3, 4, 5, 3),
            (0, 4, 50, 1), // direct but inefficient due to high latency.
        ];
        let flows = vec![
            (0, 4, 10, 101),
            (0, 4, 8, 102),
            (0, 4, 6, 103),
            (0, 4, 4, 104),
        ];
        let l = 20;
        // Only the efficient path (0->1->4) is acceptable; all flows should be routed if capacity permits.
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 4);
    }

    #[test]
    fn test_edge_overflow_latency() {
        // Validate that latency calculation does not overflow.
        let n = 2;
        let max_latency = 1_000;
        let edges = vec![
            (0, 1, max_latency, 100),
        ];
        let flows = vec![
            (0, 1, 100, 1),
        ];
        let l = max_latency;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 1);
    }

    #[test]
    fn test_no_flows() {
        // Test when no flows are provided.
        let n = 3;
        let edges = vec![
            (0, 1, 10, 10),
            (1, 2, 10, 10),
        ];
        let flows = vec![];
        let l = 30;
        let result = solve(n, edges, flows, l);
        assert_eq!(result, 0);
    }
}