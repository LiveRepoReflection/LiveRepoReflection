use network_control::{simulate_network, NetworkConfig, Link, TrafficDemand};

fn get_example_config() -> NetworkConfig {
    let n = 4; // Nodes 0, 1, 2, 3
    let links = vec![
        Link { from: 0, to: 1, capacity: 500 },
        Link { from: 0, to: 2, capacity: 300 },
        Link { from: 1, to: 3, capacity: 400 },
        Link { from: 2, to: 3, capacity: 600 },
    ];
    
    let traffic_demands = vec![
        TrafficDemand { source: 0, destination: 3, initial_rate: 50 },
        TrafficDemand { source: 1, destination: 3, initial_rate: 70 },
    ];
    
    NetworkConfig {
        n,
        links,
        traffic_demands,
        time_units: 50,
        alpha: 1.0,
        beta: 0.5,
    }
}

#[test]
fn test_basic_example() {
    let config = get_example_config();
    let final_rates = simulate_network(&config);
    
    // After 50 time units, the rates should converge to some stable values
    // The exact values depend on the implementation details, but we can check
    // that we got the right number of rates and they're all positive
    assert_eq!(final_rates.len(), 2);
    for rate in final_rates {
        assert!(rate > 0.0);
    }
}

#[test]
fn test_node_with_no_outgoing_links() {
    let mut config = get_example_config();
    // Add a node with no outgoing links
    config.n = 5;
    config.traffic_demands.push(TrafficDemand { source: 4, destination: 3, initial_rate: 30 });
    
    let final_rates = simulate_network(&config);
    
    // We should still get 3 rates, but the last one should be 0.0 (dropped)
    assert_eq!(final_rates.len(), 3);
    assert_eq!(final_rates[2], 0.0);
}

#[test]
fn test_self_loop_flow() {
    let mut config = get_example_config();
    // Add a self-loop demand
    config.traffic_demands.push(TrafficDemand { source: 1, destination: 1, initial_rate: 40 });
    
    let final_rates = simulate_network(&config);
    
    // We should still get 3 rates, but the last one should be 0.0 (dropped)
    assert_eq!(final_rates.len(), 3);
    assert_eq!(final_rates[2], 0.0);
}

#[test]
fn test_congestion_and_rate_adjustment() {
    let mut config = get_example_config();
    // Modify links to create congestion
    config.links[2].capacity = 60; // Link 1->3 has low capacity
    
    let final_rates = simulate_network(&config);
    
    // We have congestion on link 1->3, so the second flow should be limited
    assert_eq!(final_rates.len(), 2);
    assert!(final_rates[1] <= 60.0); // Rate for flow 1->3 shouldn't exceed capacity
}

#[test]
fn test_multiple_paths() {
    let n = 5;
    let links = vec![
        Link { from: 0, to: 1, capacity: 100 },
        Link { from: 0, to: 2, capacity: 100 },
        Link { from: 1, to: 3, capacity: 100 },
        Link { from: 2, to: 3, capacity: 100 },
        Link { from: 3, to: 4, capacity: 100 },
    ];
    
    let traffic_demands = vec![
        TrafficDemand { source: 0, destination: 4, initial_rate: 50 },
    ];
    
    let config = NetworkConfig {
        n,
        links,
        traffic_demands,
        time_units: 30,
        alpha: 1.0,
        beta: 0.5,
    };
    
    let final_rates = simulate_network(&config);
    
    // We should get one rate, and it should be positive
    assert_eq!(final_rates.len(), 1);
    assert!(final_rates[0] > 0.0);
}

#[test]
fn test_no_path_flow() {
    let mut config = get_example_config();
    // Remove links between node 1 and 3, breaking the path for the second flow
    config.links.remove(2);
    
    let final_rates = simulate_network(&config);
    
    // We should still get 2 rates, but the second one should be 0.0 (dropped)
    assert_eq!(final_rates.len(), 2);
    assert_eq!(final_rates[1], 0.0);
}

#[test]
fn test_alpha_beta_impact() {
    let mut config1 = get_example_config();
    config1.alpha = 0.1; // Slow increase
    config1.beta = 0.9;  // Mild decrease
    
    let mut config2 = get_example_config();
    config2.alpha = 1.0; // Fast increase
    config2.beta = 0.5;  // Aggressive decrease
    
    let final_rates1 = simulate_network(&config1);
    let final_rates2 = simulate_network(&config2);
    
    // Both should have 2 rates
    assert_eq!(final_rates1.len(), 2);
    assert_eq!(final_rates2.len(), 2);
    
    // The rates should be different due to different alpha and beta values
    // This is not a strict test, but the rates should be positive
    for rate in final_rates1.iter().chain(final_rates2.iter()) {
        assert!(*rate > 0.0);
    }
}

#[test]
fn test_large_network() {
    let n = 10;
    let mut links = Vec::new();
    
    // Create a more complex network
    for i in 0..9 {
        links.push(Link { from: i, to: i+1, capacity: 200 });
    }
    
    // Add some cross links
    links.push(Link { from: 0, to: 5, capacity: 300 });
    links.push(Link { from: 3, to: 8, capacity: 300 });
    
    let traffic_demands = vec![
        TrafficDemand { source: 0, destination: 9, initial_rate: 50 },
        TrafficDemand { source: 2, destination: 7, initial_rate: 60 },
        TrafficDemand { source: 4, destination: 9, initial_rate: 70 },
    ];
    
    let config = NetworkConfig {
        n,
        links,
        traffic_demands,
        time_units: 40,
        alpha: 0.5,
        beta: 0.7,
    };
    
    let final_rates = simulate_network(&config);
    
    // We should get 3 rates
    assert_eq!(final_rates.len(), 3);
    for rate in final_rates {
        assert!(rate >= 0.0);
    }
}

#[test]
fn test_single_node_network() {
    let n = 1;
    let links = vec![];
    let traffic_demands = vec![
        TrafficDemand { source: 0, destination: 0, initial_rate: 50 },
    ];
    
    let config = NetworkConfig {
        n,
        links,
        traffic_demands,
        time_units: 10,
        alpha: 1.0,
        beta: 0.5,
    };
    
    let final_rates = simulate_network(&config);
    
    // We should get one rate, and it should be 0.0 (self-loop is dropped)
    assert_eq!(final_rates.len(), 1);
    assert_eq!(final_rates[0], 0.0);
}

#[test]
fn test_edge_cases() {
    // Test with zero time units
    let mut config = get_example_config();
    config.time_units = 0;
    
    let final_rates = simulate_network(&config);
    
    // We should get back the initial rates
    assert_eq!(final_rates.len(), 2);
    assert_eq!(final_rates[0], 50.0);
    assert_eq!(final_rates[1], 70.0);
    
    // Test with very low capacity that causes immediate congestion
    let mut config = get_example_config();
    config.links[2].capacity = 10; // Link 1->3 has very low capacity
    
    let final_rates = simulate_network(&config);
    
    // The second flow should be severely limited
    assert_eq!(final_rates.len(), 2);
    assert!(final_rates[1] <= 10.0);
}