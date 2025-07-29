use std::collections::HashMap;
use network_opt::optimize_network;

#[test]
fn test_empty_servers() {
    let servers = vec![];
    let traffic_demands = HashMap::new();
    let link_costs = HashMap::new();
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_err());
}

#[test]
fn test_single_server() {
    let servers = vec![(1, 100)];
    let traffic_demands = HashMap::new();
    let link_costs = HashMap::new();
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_ok());
    assert!(result.unwrap().is_empty());
}

#[test]
fn test_minimal_network() {
    let servers = vec![(1, 100), (2, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 5);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 10);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_ok());
    let network = result.unwrap();
    assert_eq!(network.len(), 1);
    assert!(network.contains(&(1, 2)));
}

#[test]
fn test_insufficient_capacity() {
    let servers = vec![(1, 5), (2, 5)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 10);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 10);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_err());
}

#[test]
fn test_insufficient_bandwidth() {
    let servers = vec![(1, 100), (2, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 15);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 10);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_err());
}

#[test]
fn test_multiple_paths() {
    let servers = vec![(1, 100), (2, 100), (3, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 5);
    traffic_demands.insert((1, 3), 5);
    traffic_demands.insert((2, 3), 5);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 10);
    link_costs.insert((1, 3), 15);
    link_costs.insert((2, 3), 10);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_ok());
    let network = result.unwrap();
    assert_eq!(network.len(), 2);
    assert!(network.contains(&(1, 2)));
    assert!(network.contains(&(2, 3)));
}

#[test]
fn test_complex_network() {
    let servers = vec![(1, 50), (2, 50), (3, 50), (4, 50), (5, 50)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 10);
    traffic_demands.insert((1, 3), 5);
    traffic_demands.insert((2, 4), 8);
    traffic_demands.insert((3, 4), 7);
    traffic_demands.insert((4, 5), 12);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 5);
    link_costs.insert((1, 3), 10);
    link_costs.insert((2, 3), 8);
    link_costs.insert((2, 4), 7);
    link_costs.insert((3, 4), 5);
    link_costs.insert((4, 5), 6);
    
    let bandwidth = 15;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_ok());
    let network = result.unwrap();
    assert!(network.len() >= 4);  // Minimum spanning tree would have 4 edges
}

#[test]
fn test_disconnected_network() {
    let servers = vec![(1, 100), (2, 100), (3, 100), (4, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 5);
    traffic_demands.insert((3, 4), 5);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 10);
    link_costs.insert((3, 4), 10);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_err());
}

#[test]
fn test_no_possible_links() {
    let servers = vec![(1, 100), (2, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 2), 5);
    
    let link_costs = HashMap::new();
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_err());
}

#[test]
fn test_optimal_path_selection() {
    let servers = vec![(1, 100), (2, 100), (3, 100), (4, 100)];
    let mut traffic_demands = HashMap::new();
    traffic_demands.insert((1, 4), 5);
    
    let mut link_costs = HashMap::new();
    link_costs.insert((1, 2), 1);
    link_costs.insert((2, 3), 1);
    link_costs.insert((3, 4), 1);
    link_costs.insert((1, 4), 5);
    
    let bandwidth = 10;
    
    let result = optimize_network(&servers, &traffic_demands, &link_costs, bandwidth);
    assert!(result.is_ok());
    let network = result.unwrap();
    assert_eq!(network.len(), 3);
    assert!(network.contains(&(1, 2)));
    assert!(network.contains(&(2, 3)));
    assert!(network.contains(&(3, 4)));
}