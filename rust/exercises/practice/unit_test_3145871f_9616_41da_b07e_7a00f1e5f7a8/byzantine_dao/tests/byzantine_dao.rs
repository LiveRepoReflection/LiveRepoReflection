use byzantine_dao::simulate_dao;

#[test]
fn test_no_proposals() {
    let proposals: &[&str] = &[];
    // For no proposals the expected decision vector is empty.
    let decisions = simulate_dao(4, 1, proposals);
    let expected: Vec<String> = vec![];
    assert_eq!(decisions, expected);
}

#[test]
fn test_all_non_faulty() {
    // In a network with no faulty nodes, each proposal should be decided as sent.
    let proposals = &["proposal1", "proposal2"];
    let decisions = simulate_dao(4, 0, proposals);
    let expected: Vec<String> = vec!["proposal1".into(), "proposal2".into()];
    assert_eq!(decisions, expected);
}

#[test]
fn test_faulty_nodes_consensus_success() {
    // In a network with Byzantine nodes but a benign proposal, consensus should be reached.
    let proposals = &["network upgrade"];
    let decisions = simulate_dao(7, 2, proposals);
    let expected: Vec<String> = vec!["network upgrade".into()];
    assert_eq!(decisions, expected);
}

#[test]
fn test_consensus_failure_due_to_faulty_leader() {
    // Simulate a scenario where the designated leader is faulty.
    // The simulation is expected to run for MAX_ROUNDS and decide on an empty proposal when consensus is not reached.
    let proposals = &["fail consensus"];
    let decisions = simulate_dao(4, 1, proposals);
    let expected: Vec<String> = vec!["".into()];
    assert_eq!(decisions, expected);
}

#[test]
fn test_multiple_proposals_mixed() {
    // Provide a stream of proposals where one of them simulates a consensus failure.
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
    // Simulate a scenario where no consensus is reached within MAX_ROUNDS.
    let proposals = &["timeout"];
    let decisions = simulate_dao(5, 1, proposals);
    let expected: Vec<String> = vec!["".into()];
    assert_eq!(decisions, expected);
}