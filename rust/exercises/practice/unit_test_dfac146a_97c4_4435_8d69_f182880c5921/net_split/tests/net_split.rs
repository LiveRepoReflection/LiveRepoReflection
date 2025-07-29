use net_split::{min_moves, Node};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_move_needed() {
        let nodes = vec![
            Node { id: 0, partition_id: 0 },
            Node { id: 1, partition_id: 0 },
            Node { id: 2, partition_id: 0 },
            Node { id: 3, partition_id: 1 },
            Node { id: 4, partition_id: 1 },
        ];
        let adj_matrix = vec![
            vec![true,  true,  false, false, false],
            vec![true,  true,  true,  false, false],
            vec![false, true,  true,  false, false],
            vec![false, false, false, true,  true ],
            vec![false, false, false, true,  true ],
        ];
        let k = 2;
        // Partition 0 has 3 nodes; to reduce to k=2, need 1 move.
        let expected = 1;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }

    #[test]
    fn test_no_moves_needed() {
        let nodes = vec![
            Node { id: 0, partition_id: 0 },
            Node { id: 1, partition_id: 0 },
            Node { id: 2, partition_id: 1 },
            Node { id: 3, partition_id: 1 },
            Node { id: 4, partition_id: 1 },
        ];
        let adj_matrix = vec![
            vec![true,  true,  false, false, false],
            vec![true,  true,  false, false, false],
            vec![false, false, true,  true,  true ],
            vec![false, false, true,  true,  true ],
            vec![false, false, true,  true,  true ],
        ];
        let k = 3;
        // All partitions are within the allowed size.
        let expected = 0;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }

    #[test]
    fn test_all_same_partition() {
        let nodes = vec![
            Node { id: 0, partition_id: 0 },
            Node { id: 1, partition_id: 0 },
            Node { id: 2, partition_id: 0 },
        ];
        let adj_matrix = vec![
            vec![true,  false, false],
            vec![false, true,  false],
            vec![false, false, true ],
        ];
        let k = 1;
        // With k = 1, only one node can remain in partition 0.
        // To achieve that, two nodes must be moved.
        let expected = 2;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }

    #[test]
    fn test_disconnected_components() {
        let nodes = vec![
            Node { id: 0, partition_id: 0 },
            Node { id: 1, partition_id: 0 },
            Node { id: 2, partition_id: 0 },
            Node { id: 3, partition_id: 1 },
            Node { id: 4, partition_id: 1 },
            Node { id: 5, partition_id: 2 },
        ];
        let adj_matrix = vec![
            vec![true,  false, false, false, false, false],
            vec![false, true,  false, false, false, false],
            vec![false, false, true,  false, false, false],
            vec![false, false, false, true,  false, false],
            vec![false, false, false, false, true,  false],
            vec![false, false, false, false, false, true ],
        ];
        let k = 2;
        // Partition 0 has 3 nodes; need 1 move, others are within limit.
        let expected = 1;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }

    #[test]
    fn test_complex_partitioning() {
        // Partition distribution:
        // Partition 0: 4 nodes, Partition 1: 2 nodes, Partition 2: 5 nodes.
        let nodes = vec![
            Node { id: 0,  partition_id: 0 },
            Node { id: 1,  partition_id: 0 },
            Node { id: 2,  partition_id: 0 },
            Node { id: 3,  partition_id: 0 },
            Node { id: 4,  partition_id: 1 },
            Node { id: 5,  partition_id: 1 },
            Node { id: 6,  partition_id: 2 },
            Node { id: 7,  partition_id: 2 },
            Node { id: 8,  partition_id: 2 },
            Node { id: 9,  partition_id: 2 },
            Node { id: 10, partition_id: 2 },
        ];
        // Create a simple identity-like adjacency matrix.
        let size = nodes.len();
        let mut adj_matrix = vec![vec![false; size]; size];
        for i in 0..size {
            for j in 0..size {
                if i == j {
                    adj_matrix[i][j] = true;
                }
            }
        }
        let k = 3;
        // For Partition 0: 4 nodes -> 1 move, Partition 2: 5 nodes -> 2 moves. Total = 3 moves.
        let expected = 3;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }
}

#[cfg(test)]
mod integration_tests {
    use super::*;
    use net_split::{min_moves, Node};

    #[test]
    fn test_integration_scenario() {
        // A more complex scenario with varied connectivity.
        let nodes = vec![
            Node { id: 0, partition_id: 0 },
            Node { id: 1, partition_id: 0 },
            Node { id: 2, partition_id: 0 },
            Node { id: 3, partition_id: 1 },
            Node { id: 4, partition_id: 1 },
            Node { id: 5, partition_id: 1 },
            Node { id: 6, partition_id: 2 },
        ];
        let adj_matrix = vec![
            vec![true,  true,  false, false, false, false, false],
            vec![true,  true,  true,  false, false, false, false],
            vec![false, true,  true,  true,  false, false, false],
            vec![false, false, true,  true,  true,  false, false],
            vec![false, false, false, true,  true,  true,  false],
            vec![false, false, false, false, true,  true,  true ],
            vec![false, false, false, false, false, true,  true ],
        ];
        let k = 2;
        // Partition 0 has 3 nodes (requires 1 move),
        // Partition 1 has 3 nodes (requires 1 move),
        // Partition 2 is within limit.
        // Total expected moves: 2.
        let expected = 2;
        assert_eq!(min_moves(&nodes, &adj_matrix, k), expected);
    }
}