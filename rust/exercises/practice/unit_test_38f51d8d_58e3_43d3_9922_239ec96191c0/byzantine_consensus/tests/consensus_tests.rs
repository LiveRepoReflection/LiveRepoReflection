#[cfg(test)]
mod tests {
    use byzantine_consensus::simulate;

    #[test]
    fn test_all_honest_single_round() {
        let n = 4;
        let f = 0;
        let byzantine_nodes = vec![];
        let rounds = 1;
        let initial_values = vec![1, 0, 1, 0];
        // With all honest nodes, the leader (node 0) proposes its initial value (1) and consensus is reached.
        let result = simulate(n, f, byzantine_nodes, rounds, initial_values.clone());
        let expected = vec![1, 1, 1, 1];
        assert_eq!(result, expected);
    }

    #[test]
    fn test_all_honest_multiple_rounds() {
        let n = 5;
        let f = 0;
        let byzantine_nodes = vec![];
        let rounds = 3;
        // Leaders by round: 0, 1, and 2. The final decision will be based on leader 2's proposal.
        let initial_values = vec![1, 0, 1, 0, 1];
        let result = simulate(n, f, byzantine_nodes, rounds, initial_values.clone());
        let expected = vec![1, 1, 1, 1, 1];
        assert_eq!(result, expected);
    }

    #[test]
    fn test_benign_byzantine() {
        let n = 4;
        let f = 1;
        // Even though node 2 is marked as Byzantine, assume it behaves benignly.
        let byzantine_nodes = vec![2];
        let rounds = 1;
        // Leader is node 0 (with initial value 0), so consensus should be reached on 0.
        let initial_values = vec![0, 1, 1, 0];
        let result = simulate(n, f, byzantine_nodes, rounds, initial_values.clone());
        let expected = vec![0, 0, 0, 0];
        assert_eq!(result, expected);
    }

    #[test]
    fn test_byzantine_leader() {
        let n = 4;
        let f = 1;
        // Leader (node 0) is Byzantine.
        let byzantine_nodes = vec![0];
        let rounds = 1;
        // In the presence of a Byzantine leader, consensus is not reached and nodes default to their initial values.
        let initial_values = vec![1, 0, 0, 1];
        let result = simulate(n, f, byzantine_nodes, rounds, initial_values.clone());
        let expected = initial_values.clone();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_multiple_rounds_mixed() {
        let n = 7;
        let f = 2;
        // Byzantine nodes: 2 and 5.
        // Rounds: 3. Leaders: round1 -> node 0, round2 -> node 1, round3 -> node 2 (Byzantine).
        let byzantine_nodes = vec![2, 5];
        let rounds = 3;
        // In the final round, due to a Byzantine leader, consensus fails and default values are used.
        let initial_values = vec![1, 0, 1, 0, 1, 0, 1];
        let result = simulate(n, f, byzantine_nodes, rounds, initial_values.clone());
        let expected = initial_values.clone();
        assert_eq!(result, expected);
    }
}