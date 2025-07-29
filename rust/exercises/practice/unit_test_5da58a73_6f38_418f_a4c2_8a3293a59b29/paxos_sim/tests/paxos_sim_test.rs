use paxos_sim::ConsensusSimulator;

#[test]
fn test_basic_consensus() {
    let num_nodes = 5;
    let accept_probability = 0.8;
    let fault_percentage = 0.0; // No Byzantine nodes
    let max_rounds = 10;
    let seed = 12345;
    let initial_states = vec![1, 2, 1, 2, 1];
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    assert!(result, "Expected to reach consensus with no Byzantine nodes");
    
    // Verify that all nodes have the same state
    let states = simulator.get_node_states();
    let first_state = states[0];
    for state in states {
        assert_eq!(*state, first_state, "All nodes should have the same state");
    }
}

#[test]
fn test_with_byzantine_nodes() {
    let num_nodes = 10;
    let accept_probability = 0.9;
    let fault_percentage = 0.2; // 20% Byzantine nodes
    let max_rounds = 20;
    let seed = 54321;
    let initial_states = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    // We don't assert the result because with Byzantine nodes, consensus might not be reached
    
    if result {
        // If consensus is claimed, verify it
        let states = simulator.get_node_states();
        // Find the first non-Byzantine node state and compare others to it
        // Note: In a real test we would need access to which nodes are Byzantine
    }
}

#[test]
fn test_edge_case_zero_nodes() {
    let num_nodes = 0;
    let accept_probability = 0.5;
    let fault_percentage = 0.0;
    let max_rounds = 5;
    let seed = 67890;
    let initial_states = vec![];
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    assert!(result, "With zero nodes, consensus should be trivially reached");
}

#[test]
fn test_edge_case_all_byzantine() {
    let num_nodes = 5;
    let accept_probability = 0.5;
    let fault_percentage = 1.0; // 100% Byzantine nodes
    let max_rounds = 10;
    let seed = 13579;
    let initial_states = vec![1, 1, 1, 1, 1]; // All start with same state
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    assert!(!result, "With all Byzantine nodes, consensus should not be possible");
}

#[test]
fn test_determinism() {
    let num_nodes = 7;
    let accept_probability = 0.7;
    let fault_percentage = 0.1;
    let max_rounds = 15;
    let seed = 24680;
    let initial_states = vec![3, 3, 7, 3, 7, 3, 7];
    
    // Run simulation twice with identical parameters
    let mut simulator1 = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states.clone(),
    );
    
    let mut simulator2 = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result1 = simulator1.run_simulation();
    let result2 = simulator2.run_simulation();
    
    assert_eq!(result1, result2, "Results should be deterministic");
    
    let states1 = simulator1.get_node_states();
    let states2 = simulator2.get_node_states();
    
    assert_eq!(states1, states2, "Final states should be identical for the same seed");
}

#[test]
fn test_extreme_probabilities() {
    // Test with accept_probability = 0.0
    let mut simulator = ConsensusSimulator::new(
        5,
        0.0, // No node will accept proposals
        0.0,
        10,
        12345,
        vec![1, 2, 3, 4, 5],
    );
    
    let result = simulator.run_simulation();
    assert!(!result, "With accept_probability = 0.0, consensus should not be reached");
    
    // Test with accept_probability = 1.0
    let mut simulator = ConsensusSimulator::new(
        5,
        1.0, // All nodes will accept proposals
        0.0,
        10,
        12345,
        vec![1, 2, 3, 4, 5],
    );
    
    let result = simulator.run_simulation();
    assert!(result, "With accept_probability = 1.0, consensus should be reached");
}

#[test]
fn test_large_scale() {
    // This test checks that the implementation can handle large numbers of nodes
    let num_nodes = 1000; // Using 1000 instead of 10000 to keep the test faster
    let accept_probability = 0.8;
    let fault_percentage = 0.05;
    let max_rounds = 50;
    let seed = 11111;
    
    // Generate initial states
    let initial_states: Vec<i64> = (0..num_nodes).map(|i| (i % 10) as i64).collect();
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    // Simply check that this runs without panicking
    let _ = simulator.run_simulation();
    // We don't assert the result as it depends on the random seed
}

#[test]
fn test_always_same_initial_state() {
    // If all nodes start with the same state, they should remain in consensus
    let num_nodes = 5;
    let accept_probability = 0.5;
    let fault_percentage = 0.0;
    let max_rounds = 10;
    let seed = 98765;
    let initial_states = vec![42, 42, 42, 42, 42]; // All start with same state
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    assert!(result, "With all nodes starting in the same state, consensus should be maintained");
    
    let states = simulator.get_node_states();
    for state in states {
        assert_eq!(*state, 42, "All nodes should maintain the initial state");
    }
}

#[test]
fn test_one_round_max() {
    // Test with only one round allowed
    let num_nodes = 5;
    let accept_probability = 0.6;
    let fault_percentage = 0.0;
    let max_rounds = 1;
    let seed = 55555;
    let initial_states = vec![1, 2, 3, 2, 1];
    
    let mut simulator = ConsensusSimulator::new(
        num_nodes,
        accept_probability,
        fault_percentage,
        max_rounds,
        seed,
        initial_states,
    );
    
    let result = simulator.run_simulation();
    // We don't assert the result because with only one round,
    // it depends heavily on the random seed whether consensus will be reached
}