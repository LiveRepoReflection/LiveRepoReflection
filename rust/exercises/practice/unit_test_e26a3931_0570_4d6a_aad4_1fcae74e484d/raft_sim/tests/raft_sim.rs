use raft_sim::{simulate, SimulationConfig};
use std::collections::HashSet;
use std::thread;
use std::time::Duration;

#[test]
fn test_consensus_with_minimal_nodes() {
    let config = SimulationConfig {
        num_nodes: 3,
        network_delay_ms_min: 10,
        network_delay_ms_max: 50,
        timeout_ms_min: 150,
        timeout_ms_max: 300,
        simulation_timeout_ms: 5000,
        message_loss_probability: 0.1,
    };

    let result = simulate(config);
    assert!(result.is_some(), "Simulation should reach consensus");
    
    let (value, committed_nodes) = result.unwrap();
    assert!(committed_nodes > 1, "Majority of nodes should commit the value");
    println!("Consensus reached with value: {} by {} nodes", value, committed_nodes);
}

#[test]
fn test_consensus_with_larger_cluster() {
    let config = SimulationConfig {
        num_nodes: 5,
        network_delay_ms_min: 10,
        network_delay_ms_max: 50,
        timeout_ms_min: 150,
        timeout_ms_max: 300,
        simulation_timeout_ms: 5000,
        message_loss_probability: 0.1,
    };

    let result = simulate(config);
    assert!(result.is_some(), "Simulation should reach consensus");
    
    let (value, committed_nodes) = result.unwrap();
    assert!(committed_nodes >= 3, "Majority of nodes (at least 3 out of 5) should commit the value");
    println!("Consensus reached with value: {} by {} nodes", value, committed_nodes);
}

#[test]
fn test_high_network_latency() {
    let config = SimulationConfig {
        num_nodes: 3,
        network_delay_ms_min: 100,
        network_delay_ms_max: 300,
        timeout_ms_min: 350,
        timeout_ms_max: 600,
        simulation_timeout_ms: 7000,
        message_loss_probability: 0.1,
    };

    let result = simulate(config);
    assert!(result.is_some(), "Simulation should reach consensus even with high latency");
    
    let (value, committed_nodes) = result.unwrap();
    assert!(committed_nodes > 1, "Majority of nodes should commit the value");
}

#[test]
fn test_high_message_loss() {
    let config = SimulationConfig {
        num_nodes: 5,
        network_delay_ms_min: 10,
        network_delay_ms_max: 50,
        timeout_ms_min: 150,
        timeout_ms_max: 300,
        simulation_timeout_ms: 8000,
        message_loss_probability: 0.5, // 50% message loss
    };

    let result = simulate(config);
    // With high message loss, consensus might not be reached within the timeout
    // But if it is reached, it should be consistent
    if let Some((value, committed_nodes)) = result {
        assert!(committed_nodes >= 3, "Majority of nodes should commit the value");
        println!("Consensus reached with value: {} by {} nodes despite high message loss", value, committed_nodes);
    } else {
        println!("Test passed: No consensus with high message loss (which is acceptable)");
    }
}

#[test]
fn test_multiple_simulations_consistency() {
    let config = SimulationConfig {
        num_nodes: 3,
        network_delay_ms_min: 10,
        network_delay_ms_max: 50,
        timeout_ms_min: 150,
        timeout_ms_max: 300,
        simulation_timeout_ms: 5000,
        message_loss_probability: 0.1,
    };
    
    let mut results = Vec::new();
    
    // Run multiple simulations
    for _ in 0..5 {
        if let Some((value, committed_nodes)) = simulate(config.clone()) {
            results.push((value, committed_nodes));
            // Add a small delay between simulations
            thread::sleep(Duration::from_millis(100));
        }
    }
    
    // Check that we have results
    assert!(!results.is_empty(), "At least some simulations should reach consensus");
    
    // If successful, all simulations should have a majority consensus
    for (value, committed_nodes) in &results {
        assert!(*committed_nodes > config.num_nodes / 2, 
                "Each successful simulation should have majority consensus");
        println!("Simulation reached consensus with value: {} by {} nodes", value, committed_nodes);
    }
}

#[test]
fn test_unique_committed_values() {
    let config = SimulationConfig {
        num_nodes: 3,
        network_delay_ms_min: 10,
        network_delay_ms_max: 50,
        timeout_ms_min: 150,
        timeout_ms_max: 300,
        simulation_timeout_ms: 5000,
        message_loss_probability: 0.1,
    };
    
    let mut committed_values = HashSet::new();
    
    // Run multiple simulations to see if we get different committed values
    for _ in 0..10 {
        if let Some((value, _)) = simulate(config.clone()) {
            committed_values.insert(value);
        }
        // Add a small delay between simulations
        thread::sleep(Duration::from_millis(100));
    }
    
    // Check that we have results
    assert!(!committed_values.is_empty(), "At least some simulations should reach consensus");
    
    // Ideally, we'd see different values committed across runs due to randomness
    // This is not a strict requirement but indicates proper randomization
    println!("Number of unique committed values: {}", committed_values.len());
    println!("Committed values: {:?}", committed_values);
}