use bft_consensus::run_consensus;

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