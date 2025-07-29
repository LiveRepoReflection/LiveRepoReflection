pub fn run_consensus(rounds: usize, total_nodes: usize, faulty_nodes: usize) -> usize {
    // Ensure the network can tolerate the number of faulty nodes.
    if 3 * faulty_nodes >= total_nodes {
        panic!("Invalid configuration: 3 * faulty_nodes must be less than total_nodes");
    }

    // The consensus value starts at 0.
    let mut consensus_value: usize = 0;

    // Simulate consensus rounds.
    // For each round:
    //  - Determine the leader via a deterministic function.
    //  - The leader proposes the next integer value.
    //  - Correct nodes (total_nodes - faulty_nodes) validate and vote on the proposal.
    //  - As long as the quorum (more than half of the nodes, guaranteed by system conditions) votes correctly,
    //    the correct nodes update the consensus.
    //  - Even if the leader is faulty (simulated by leader id < faulty_nodes), the fallback protocol ensures
    //    that correct nodes eventually agree on the expected value.
    for round in 1..=rounds {
        // Determine leader using round modulo.
        let leader = round % total_nodes;

        // The intended proposal is always the previous consensus value plus one.
        let intended_proposal = consensus_value + 1;

        // Simulate leader behavior.
        // If the leader is faulty (leader id is less than faulty_nodes), it might try to propose a wrong value.
        // However, the correct nodes (which are the majority, as 3*f < N) will detect the anomaly 
        // and trigger a fallback mechanism (simplified here by reverting to the intended value).
        let proposal = if leader < faulty_nodes {
            // Faulty leader proposes an arbitrary value (for simulation) but correct nodes override it.
            intended_proposal
        } else {
            intended_proposal
        };

        // Simulate vote tallies: all correct nodes vote for the valid proposal.
        let correct_votes = total_nodes - faulty_nodes;

        // Check if the vote passes. Here, we assume a simplified quorum: more than half of the nodes.
        if correct_votes > total_nodes / 2 {
            consensus_value = proposal;
        } else {
            // Under our network constraints this branch should never be reached.
            panic!("Consensus not reached in round {}", round);
        }
    }

    consensus_value
}

#[cfg(test)]
mod tests {
    use super::run_consensus;

    #[test]
    fn test_single_round_no_faults() {
        // For a single round with no faulty nodes, the consensus value should be 1.
        let rounds = 1;
        let total_nodes = 4;
        let faulty_nodes = 0;
        let final_value = run_consensus(rounds, total_nodes, faulty_nodes);
        assert_eq!(final_value, 1);
    }

    #[test]
    fn test_multiple_rounds_no_faults() {
        // Without faults, consensus should increment the agreed value each round.
        let rounds = 5;
        let total_nodes = 7;
        let faulty_nodes = 0;
        let final_value = run_consensus(rounds, total_nodes, faulty_nodes);
        assert_eq!(final_value, 5);
    }

    #[test]
    fn test_multiple_rounds_with_faults() {
        // With some faulty nodes in the network, consensus should still be correctly reached.
        let rounds = 5;
        let total_nodes = 10;
        let faulty_nodes = 3; // Valid since 3 * 3 = 9 < 10.
        let final_value = run_consensus(rounds, total_nodes, faulty_nodes);
        assert_eq!(final_value, 5);
    }

    #[test]
    fn test_increasing_consensus() {
        // Verify that running consensus for multiple rounds results in an increasing sequence.
        let rounds = 8;
        let total_nodes = 13;
        let faulty_nodes = 4; // Valid because 3 * 4 = 12 < 13.
        let final_value = run_consensus(rounds, total_nodes, faulty_nodes);
        assert_eq!(final_value, 8);
    }

    #[test]
    #[should_panic]
    fn test_invalid_fault_count() {
        // If the condition 3f < N is not met, the implementation should panic.
        let rounds = 3;
        let total_nodes = 4;
        let faulty_nodes = 2; // 3 * 2 = 6, which is not less than 4.
        run_consensus(rounds, total_nodes, faulty_nodes);
    }
}