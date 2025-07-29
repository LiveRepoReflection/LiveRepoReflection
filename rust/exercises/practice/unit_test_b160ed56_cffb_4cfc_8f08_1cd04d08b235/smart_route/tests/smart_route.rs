use smart_route::*;
use std::collections::HashMap;

// Helper function to build a simple network
fn build_simple_network() -> Network {
    let mut network = HashMap::new();
    
    // Router 1 connected to 2 and 3
    network.insert(1, vec![
        (2, 100.0, 50.0),  // Link to router 2: capacity 100, utilization 50
        (3, 150.0, 75.0),  // Link to router 3: capacity 150, utilization 75
    ]);
    
    // Router 2 connected to 1 and 4
    network.insert(2, vec![
        (1, 100.0, 50.0),  // Link to router 1: capacity 100, utilization 50
        (4, 80.0, 40.0),   // Link to router 4: capacity 80, utilization 40
    ]);
    
    // Router 3 connected to 1 and 4
    network.insert(3, vec![
        (1, 150.0, 75.0),  // Link to router 1: capacity 150, utilization 75
        (4, 120.0, 90.0),  // Link to router 4: capacity 120, utilization 90
    ]);
    
    // Router 4 connected to 2 and 3
    network.insert(4, vec![
        (2, 80.0, 40.0),   // Link to router 2: capacity 80, utilization 40
        (3, 120.0, 90.0),  // Link to router 3: capacity 120, utilization 90
    ]);
    
    network
}

// Helper function to build a larger network
fn build_complex_network() -> Network {
    let mut network = HashMap::new();
    
    // Create a more complex network with 10 routers
    for i in 1..=10 {
        let mut connections = Vec::new();
        
        // Each router connects to up to 3 other routers
        for j in 1..=10 {
            if i != j && (i + j) % 3 == 0 {
                let capacity = 100.0 + (i * j) as f64;
                let utilization = capacity * 0.5 + (i + j) as f64;
                connections.push((j, capacity, utilization));
            }
        }
        
        network.insert(i, connections);
    }
    
    // Add some additional connections to ensure connectivity
    for i in 1..10 {
        if let Some(connections) = network.get_mut(&i) {
            connections.push((i + 1, 200.0, 100.0));
        }
        
        if let Some(connections) = network.get_mut(&(i + 1)) {
            connections.push((i, 200.0, 100.0));
        }
    }
    
    network
}

// Network simulator that increases utilization on all links
fn simulate_network_updates_increase(network: Network) -> Network {
    let mut updated_network = HashMap::new();
    
    for (router_id, connections) in network {
        let mut updated_connections = Vec::new();
        
        for (dest, capacity, utilization) in connections {
            // Increase utilization by 10% of available capacity, but don't exceed capacity
            let new_utilization = (utilization + (capacity - utilization) * 0.1).min(capacity * 0.99);
            updated_connections.push((dest, capacity, new_utilization));
        }
        
        updated_network.insert(router_id, updated_connections);
    }
    
    updated_network
}

// Network simulator that decreases utilization on all links
fn simulate_network_updates_decrease(network: Network) -> Network {
    let mut updated_network = HashMap::new();
    
    for (router_id, connections) in network {
        let mut updated_connections = Vec::new();
        
        for (dest, capacity, utilization) in connections {
            // Decrease utilization by 10%
            let new_utilization = utilization * 0.9;
            updated_connections.push((dest, capacity, new_utilization));
        }
        
        updated_network.insert(router_id, updated_connections);
    }
    
    updated_network
}

// Network simulator that randomly changes utilization
fn simulate_network_updates_random(network: Network) -> Network {
    let mut updated_network = HashMap::new();
    
    for (router_id, connections) in network {
        let mut updated_connections = Vec::new();
        
        for (dest, capacity, utilization) in connections {
            // Use router_id and dest to deterministically generate a change factor
            let change_factor = ((router_id * 17 + dest * 31) % 20) as f64 / 10.0 - 1.0; // -1.0 to +1.0
            let new_utilization = (utilization + change_factor * 10.0).max(0.0).min(capacity * 0.99);
            updated_connections.push((dest, capacity, new_utilization));
        }
        
        updated_network.insert(router_id, updated_connections);
    }
    
    updated_network
}

// Test for basic functionality with a simple network
#[test]
fn test_simple_network_basic_routing() {
    let network = build_simple_network();
    let source = 1;
    let destination = 4;
    let data_size = 10.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_increase);
    
    assert!(!route.is_empty(), "Should find a route between 1 and 4");
    assert_eq!(route[0], 1, "Route should start at source router 1");
    assert_eq!(*route.last().unwrap(), 4, "Route should end at destination router 4");
    
    // Check that the route is valid (each node is connected to the next one)
    let network = build_simple_network();
    for i in 0..route.len() - 1 {
        let current = route[i];
        let next = route[i + 1];
        let connections = network.get(&current).unwrap();
        let connected = connections.iter().any(|(dest, _, _)| *dest == next);
        assert!(connected, "Router {} is not connected to router {}", current, next);
    }
}

// Test route with network utilization increase
#[test]
fn test_route_with_utilization_increase() {
    let network = build_simple_network();
    let source = 1;
    let destination = 4;
    let data_size = 20.0;
    
    let route = find_optimal_route(network.clone(), source, destination, data_size, simulate_network_updates_increase);
    
    assert!(!route.is_empty(), "Should find a route despite utilization increase");
    
    // The route should likely prefer the path with more available bandwidth
    // In our network, the path 1->2->4 has more available bandwidth than 1->3->4
    // But this might change after simulation, so we just check it's valid
    let updated_network = simulate_network_updates_increase(network);
    for i in 0..route.len() - 1 {
        let current = route[i];
        let next = route[i + 1];
        let connections = updated_network.get(&current).unwrap();
        let link = connections.iter().find(|(dest, _, _)| *dest == next).unwrap();
        assert!(link.1 > link.2, "Link capacity should be greater than utilization");
    }
}

// Test route with network utilization decrease
#[test]
fn test_route_with_utilization_decrease() {
    let network = build_simple_network();
    let source = 1;
    let destination = 4;
    let data_size = 30.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_decrease);
    
    assert!(!route.is_empty(), "Should find a route with utilization decrease");
}

// Test with complex network
#[test]
fn test_complex_network_routing() {
    let network = build_complex_network();
    let source = 1;
    let destination = 10;
    let data_size = 50.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_random);
    
    assert!(!route.is_empty(), "Should find a route in complex network");
    assert_eq!(route[0], 1, "Route should start at source router 1");
    assert_eq!(*route.last().unwrap(), 10, "Route should end at destination router 10");
}

// Test with no possible route
#[test]
fn test_no_route_available() {
    let mut network = HashMap::new();
    
    // Two disconnected nodes
    network.insert(1, vec![]);
    network.insert(2, vec![]);
    
    let source = 1;
    let destination = 2;
    let data_size = 10.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_random);
    
    assert!(route.is_empty(), "Should return empty route when no path exists");
}

// Test with all links at full capacity
#[test]
fn test_congested_network() {
    let mut network = build_simple_network();
    
    // Modify network to make all links nearly congested
    for connections in network.values_mut() {
        for (_, capacity, utilization) in connections.iter_mut() {
            *utilization = *capacity * 0.99; // 99% utilization
        }
    }
    
    let source = 1;
    let destination = 4;
    let data_size = 5.0; // Small data size that might still work
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_decrease);
    
    // With a decreasing utilization simulator, we might still find a route
    if !route.is_empty() {
        assert_eq!(route[0], 1);
        assert_eq!(*route.last().unwrap(), 4);
    }
    // If no route is found, that's also acceptable for this test
}

// Test large data transfer
#[test]
fn test_large_data_transfer() {
    let network = build_complex_network();
    let source = 1;
    let destination = 10;
    let data_size = 500.0; // Large data size
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_random);
    
    // This test is more about not crashing with large data
    if !route.is_empty() {
        assert_eq!(route[0], 1);
        assert_eq!(*route.last().unwrap(), 10);
    }
}

// Test multiple possible routes
#[test]
fn test_multiple_route_options() {
    let mut network = HashMap::new();
    
    // Create a diamond-shaped network with multiple paths
    network.insert(1, vec![
        (2, 100.0, 50.0),
        (3, 100.0, 50.0),
    ]);
    network.insert(2, vec![
        (1, 100.0, 50.0),
        (4, 100.0, 50.0),
    ]);
    network.insert(3, vec![
        (1, 100.0, 50.0),
        (4, 100.0, 50.0),
    ]);
    network.insert(4, vec![
        (2, 100.0, 50.0),
        (3, 100.0, 50.0),
    ]);
    
    let source = 1;
    let destination = 4;
    let data_size = 10.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_random);
    
    assert!(!route.is_empty(), "Should find a route in diamond network");
    assert_eq!(route[0], 1);
    assert_eq!(*route.last().unwrap(), 4);
    
    // Should be either 1->2->4 or 1->3->4
    assert!(
        (route.len() == 3 && (route[1] == 2 || route[1] == 3)),
        "Route should use one of the two possible paths"
    );
}

// Test performance with a large network
#[test]
fn test_large_network_performance() {
    let mut network = HashMap::new();
    let num_routers = 100; // Using 100 instead of 1000 for faster tests
    
    // Create a grid-like network
    for i in 1..=num_routers {
        let mut connections = Vec::new();
        
        // Connect to neighbors (at most 4)
        let row = (i - 1) / 10 + 1;
        let col = (i - 1) % 10 + 1;
        
        // Connect to left neighbor
        if col > 1 {
            connections.push((i - 1, 100.0, 50.0));
        }
        
        // Connect to right neighbor
        if col < 10 {
            connections.push((i + 1, 100.0, 50.0));
        }
        
        // Connect to top neighbor
        if row > 1 {
            connections.push((i - 10, 100.0, 50.0));
        }
        
        // Connect to bottom neighbor
        if row < 10 {
            connections.push((i + 10, 100.0, 50.0));
        }
        
        network.insert(i, connections);
    }
    
    let source = 1;
    let destination = num_routers;
    let data_size = 20.0;
    
    let route = find_optimal_route(network, source, destination, data_size, simulate_network_updates_random);
    
    assert!(!route.is_empty(), "Should find a route in large network");
    assert_eq!(route[0], 1);
    assert_eq!(*route.last().unwrap(), num_routers);
}