use std::collections::HashMap;
use optimal_placement::allocate;

#[test]
fn test_basic_allocation() {
    let data_size = 100;
    let replication_factor = 2;
    let max_latency = 100;
    // Three data centers with sufficient capacity and low latencies.
    let data_centers = vec![
        (1, 200, 10), // (id, capacity, cost)
        (2, 150, 5),
        (3, 300, 20),
    ];
    let network_links = vec![
        (1, 2, 50),
        (2, 3, 60),
        (1, 3, 70),
    ];
    let result = allocate(data_size, replication_factor, max_latency, data_centers.clone(), network_links.clone());
    assert!(result.is_some(), "Expected valid allocation");
    let allocation = result.unwrap();

    // Check that the total allocated amount equals replication_factor * data_size.
    let total_alloc: f64 = allocation.values().sum();
    let required = (replication_factor as f64) * (data_size as f64);
    assert!((total_alloc - required).abs() < 1e-6, "Total allocation {} does not match required {}", total_alloc, required);

    // Check that no data center exceeds its capacity.
    for (id, amount) in allocation.iter() {
        let capacity = data_centers.iter().find(|&&(dc_id, _, _)| dc_id == *id).unwrap().1 as f64;
        assert!(*amount <= capacity + 1e-6, "Data center {} allocation {} exceeds capacity {}", id, amount, capacity);
    }
}

#[test]
fn test_insufficient_capacity() {
    let data_size = 100;
    let replication_factor = 3;
    let max_latency = 200;
    // Total required storage = 300 TB, but overall capacity is less.
    let data_centers = vec![
        (1, 50, 10),
        (2, 100, 5),
        (3, 70, 20),
    ];
    let network_links = vec![
        (1, 2, 50),
        (2, 3, 60),
        (1, 3, 80),
    ];
    let result = allocate(data_size, replication_factor, max_latency, data_centers, network_links);
    assert!(result.is_none(), "Expected allocation failure due to insufficient capacity");
}

#[test]
fn test_latency_constraint_failure() {
    let data_size = 50;
    let replication_factor = 2;
    // Set max_latency too low relative to network latencies.
    let max_latency = 30;
    let data_centers = vec![
        (1, 100, 10),
        (2, 100, 20),
        (3, 100, 15),
    ];
    let network_links = vec![
        (1, 2, 40),
        (2, 3, 50),
        (1, 3, 60),
    ];
    let result = allocate(data_size, replication_factor, max_latency, data_centers, network_links);
    assert!(result.is_none(), "Expected allocation failure due to latency constraint violations");
}

#[test]
fn test_complex_allocation() {
    let data_size = 250;
    let replication_factor = 3;
    let max_latency = 100;
    let data_centers = vec![
        (1, 300, 8),
        (2, 200, 12),
        (3, 250, 5),
        (4, 400, 10),
        (5, 150, 7),
    ];
    let network_links = vec![
        (1, 2, 30),
        (1, 3, 40),
        (1, 4, 50),
        (1, 5, 60),
        (2, 3, 35),
        (2, 4, 45),
        (2, 5, 55),
        (3, 4, 25),
        (3, 5, 65),
        (4, 5, 45),
    ];
    let result = allocate(data_size, replication_factor, max_latency, data_centers.clone(), network_links.clone());
    assert!(result.is_some(), "Expected valid allocation for complex scenario");
    let allocation = result.unwrap();

    // Check that the total allocated equals replication_factor * data_size.
    let total_alloc: f64 = allocation.values().sum();
    let required = (replication_factor as f64) * (data_size as f64);
    assert!((total_alloc - required).abs() < 1e-6, "Total allocation {} does not match required {}", total_alloc, required);

    // Validate that each allocation does not exceed the respective data center capacity.
    for (id, amount) in allocation.iter() {
        let capacity = data_centers.iter().find(|&&(dc_id, _, _)| dc_id == *id).unwrap().1 as f64;
        assert!(*amount <= capacity + 1e-6, "Data center {} allocation {} exceeds capacity {}", id, amount, capacity);
    }
}