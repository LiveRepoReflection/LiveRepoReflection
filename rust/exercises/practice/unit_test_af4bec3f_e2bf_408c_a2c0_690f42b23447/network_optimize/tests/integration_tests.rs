use std::collections::HashMap;
use network_optimize::optimize_network;

#[test]
fn test_single_node() {
    // For a single node, there are no pairs, so average latency is defined as 0.0.
    let n = 1;
    let edge_costs = HashMap::new();
    let edge_capacities = HashMap::new();
    let max_total_cost = 0;
    let fault_tolerance = 1;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    match result {
        Some(latency) => assert!((latency - 0.0).abs() < 1e-6, "Expected latency 0.0, got {}", latency),
        None => panic!("Expected Some(0.0) for a single node."),
    }
}

#[test]
fn test_two_nodes_valid() {
    // Two nodes must be connected by a single edge.
    let n = 2;
    let mut edge_costs = HashMap::new();
    let mut edge_capacities = HashMap::new();
    // Define an edge between node 0 and node 1.
    edge_costs.insert((0, 1), 5);
    edge_costs.insert((1, 0), 5);
    edge_capacities.insert((0, 1), 10);
    edge_capacities.insert((1, 0), 10);
    let max_total_cost = 5; // Budget allows the single edge.
    let fault_tolerance = 1;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    // The only edge has a latency of 1/10 = 0.1. There is only one pair (0,1).
    match result {
        Some(latency) => assert!((latency - 0.1).abs() < 1e-6, "Expected latency 0.1, got {}", latency),
        None => panic!("Expected valid configuration for two nodes."),
    }
}

#[test]
fn test_two_nodes_invalid_due_to_cost() {
    // Two nodes but the maximum cost is too low to afford the single connecting edge.
    let n = 2;
    let mut edge_costs = HashMap::new();
    let mut edge_capacities = HashMap::new();
    edge_costs.insert((0, 1), 5);
    edge_costs.insert((1, 0), 5);
    edge_capacities.insert((0, 1), 10);
    edge_capacities.insert((1, 0), 10);
    let max_total_cost = 4; // Budget is insufficient.
    let fault_tolerance = 1;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    assert!(result.is_none(), "Expected None due to insufficient cost budget.");
}

#[test]
fn test_three_nodes_fault_tolerance_met_tree() {
    // For fault_tolerance = 1, a spanning tree is acceptable.
    let n = 3;
    let mut edge_costs = HashMap::new();
    let mut edge_capacities = HashMap::new();
    // Provide edges for a tree: edges (0,1) and (1,2) form a spanning tree.
    edge_costs.insert((0, 1), 2);
    edge_costs.insert((1, 0), 2);
    edge_costs.insert((1, 2), 2);
    edge_costs.insert((2, 1), 2);
    // Extra edge offered but expensive (not chosen in optimal solution if spanning tree is used).
    edge_costs.insert((0, 2), 10);
    edge_costs.insert((2, 0), 10);
    edge_capacities.insert((0, 1), 5);
    edge_capacities.insert((1, 0), 5);
    edge_capacities.insert((1, 2), 5);
    edge_capacities.insert((2, 1), 5);
    edge_capacities.insert((0, 2), 20);
    edge_capacities.insert((2, 0), 20);
    let max_total_cost = 4; // Only enough for the spanning tree (2 + 2 = 4).
    let fault_tolerance = 1;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    // In the spanning tree:
    // (0,1): latency = 1/5 = 0.2, (1,2): latency = 0.2, and (0,2): 0.2 + 0.2 = 0.4.
    // Average latency = (0.2 + 0.2 + 0.4) / 3 ≈ 0.26666667.
    match result {
        Some(latency) => assert!((latency - 0.26666667).abs() < 1e-6, "Expected latency ≈0.26666667, got {}", latency),
        None => panic!("Expected valid configuration for three nodes with fault_tolerance=1."),
    }
}

#[test]
fn test_three_nodes_fault_tolerance_not_met() {
    // When fault_tolerance = 2, a spanning tree is insufficient.
    let n = 3;
    let mut edge_costs = HashMap::new();
    let mut edge_capacities = HashMap::new();
    edge_costs.insert((0, 1), 2);
    edge_costs.insert((1, 0), 2);
    edge_costs.insert((1, 2), 2);
    edge_costs.insert((2, 1), 2);
    edge_costs.insert((0, 2), 10);
    edge_costs.insert((2, 0), 10);
    edge_capacities.insert((0, 1), 5);
    edge_capacities.insert((1, 0), 5);
    edge_capacities.insert((1, 2), 5);
    edge_capacities.insert((2, 1), 5);
    edge_capacities.insert((0, 2), 20);
    edge_capacities.insert((2, 0), 20);
    let max_total_cost = 4; // Forces the spanning tree selection.
    let fault_tolerance = 2;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    assert!(result.is_none(), "Expected None because fault_tolerance requirement is not met with the available cost budget.");
}

#[test]
fn test_complete_graph_three_nodes_fault_tolerance_met() {
    // A complete graph on three nodes with fault_tolerance = 2.
    let n = 3;
    let mut edge_costs = HashMap::new();
    let mut edge_capacities = HashMap::new();
    // Define a complete graph: every possible edge exists.
    let edges = [(0, 1), (1, 0), (1, 2), (2, 1), (0, 2), (2, 0)];
    for &(u, v) in &edges {
        edge_costs.insert((u, v), 3);
        edge_capacities.insert((u, v), 3);
    }
    let max_total_cost = 9; // Sufficient budget for selecting edges from the complete graph.
    let fault_tolerance = 2;
    let result = optimize_network(n, &edge_costs, &edge_capacities, max_total_cost, fault_tolerance);
    // In the complete graph the shortest path between any two nodes is the direct edge with latency = 1/3 ≈ 0.33333333.
    match result {
        Some(latency) => assert!((latency - 0.33333333).abs() < 1e-6, "Expected latency ≈0.33333333, got {}", latency),
        None => panic!("Expected valid configuration for complete graph with fault_tolerance=2."),
    }
}