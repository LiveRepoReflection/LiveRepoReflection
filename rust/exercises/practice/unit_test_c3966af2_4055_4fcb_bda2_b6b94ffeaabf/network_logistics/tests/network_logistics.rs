use network_logistics::{optimize_network, Warehouse, Customer, Route};

#[test]
fn test_basic_network() {
    // One warehouse and one customer, directly connected.
    let warehouses = vec![
        Warehouse { id: 1, x: 0, y: 0, capacity: 100 }
    ];
    let customers = vec![
        Customer { id: 101, x: 10, y: 10, demand: 50 }
    ];
    let routes = vec![
        // Connect warehouse 1 to customer 101
        Route { from: 1, to: 101, cost: 5.0 },
        // Also add reverse edge since routes are bidirectional.
        Route { from: 101, to: 1, cost: 5.0 },
    ];

    // Use a disruption probability of 0 for the basic test.
    let disruption_prob = 0.0;
    let simulations = 100;

    let result = optimize_network(&warehouses, &customers, &routes, disruption_prob, simulations);
    assert!(result.is_ok(), "Expected a valid optimal flow solution.");

    let (optimal_flow, total_cost, resilience_score) = result.unwrap();

    // Check that total cost is non-negative.
    assert!(total_cost >= 0.0, "Total cost should be non-negative.");
    // Resilience score must be between 0 and 1.
    assert!(resilience_score >= 0.0 && resilience_score <= 1.0, "Resilience score should be between 0 and 1.");

    // Verify that the optimal flow satisfies demand from warehouse to customer.
    // This simple test expects a single route flow from warehouse 1 to customer 101 of 50 units.
    let mut found_flow = false;
    for (from, to, flow) in optimal_flow {
        if from == 1 && to == 101 {
            assert_eq!(flow, 50, "The flow along route 1->101 should equal the customer demand.");
            found_flow = true;
        }
    }
    assert!(found_flow, "Expected to find a valid flow from warehouse 1 to customer 101.");
}

#[test]
fn test_disconnected_network() {
    // Create a scenario where the customer is not reachable from the warehouse.
    let warehouses = vec![
        Warehouse { id: 1, x: 0, y: 0, capacity: 100 }
    ];
    let customers = vec![
        Customer { id: 201, x: 100, y: 100, demand: 30 }
    ];
    let routes = vec![
        // No route connecting warehouse 1 to customer 201 directly or indirectly.
        Route { from: 2, to: 201, cost: 10.0 },
        Route { from: 201, to: 2, cost: 10.0 },
    ];

    let disruption_prob = 0.0;
    let simulations = 50;

    let result = optimize_network(&warehouses, &customers, &routes, disruption_prob, simulations);
    assert!(result.is_err(), "Expected an error due to disconnected network.");
}

#[test]
fn test_complex_network_multiple_paths() {
    // Create a more complex network with two warehouses and two customers.
    // There are redundant routes to allow for optimization and resilience.
    let warehouses = vec![
        Warehouse { id: 1, x: 0, y: 0, capacity: 80 },
        Warehouse { id: 2, x: 5, y: 5, capacity: 70 }
    ];
    let customers = vec![
        Customer { id: 101, x: 10, y: 0, demand: 60 },
        Customer { id: 102, x: 0, y: 10, demand: 50 }
    ];
    let routes = vec![
        // Routes from warehouses to customers with different costs.
        Route { from: 1, to: 101, cost: 4.0 },
        Route { from: 101, to: 1, cost: 4.0 },
        Route { from: 1, to: 102, cost: 6.0 },
        Route { from: 102, to: 1, cost: 6.0 },
        Route { from: 2, to: 101, cost: 5.0 },
        Route { from: 101, to: 2, cost: 5.0 },
        Route { from: 2, to: 102, cost: 3.0 },
        Route { from: 102, to: 2, cost: 3.0 },
        // Route between warehouses (redundancy)
        Route { from: 1, to: 2, cost: 2.0 },
        Route { from: 2, to: 1, cost: 2.0 },
        // Route between customers (potential redirection)
        Route { from: 101, to: 102, cost: 7.0 },
        Route { from: 102, to: 101, cost: 7.0 },
    ];

    let disruption_prob = 0.1;
    let simulations = 150;

    let result = optimize_network(&warehouses, &customers, &routes, disruption_prob, simulations);
    assert!(result.is_ok(), "Expected a valid optimal flow solution in a complex network.");

    let (optimal_flow, total_cost, resilience_score) = result.unwrap();
    // Check basic constraints: total cost and resilience score bounds.
    assert!(total_cost >= 0.0, "Total cost should be non-negative.");
    assert!(resilience_score >= 0.0 && resilience_score <= 1.0, "Resilience score should be between 0 and 1.");

    // Verify that flows are assigned properly by checking aggregate flows for each customer.
    let mut demand_map = std::collections::HashMap::new();
    for cust in &customers {
        demand_map.insert(cust.id, cust.demand);
    }
    for &(_, to, flow) in &optimal_flow {
        if let Some(demand) = demand_map.get_mut(&to) {
            // Subtract satisfied flow from demand
            if *demand >= flow {
                *demand -= flow;
            } else {
                *demand = 0;
            }
        }
    }
    for (cust_id, remaining_demand) in demand_map {
        assert_eq!(remaining_demand, 0, "Customer {} should have full demand satisfied.", cust_id);
    }
}

#[test]
fn test_resilience_under_high_disruption() {
    // Test the resilience score under a high disruption probability.
    let warehouses = vec![
        Warehouse { id: 1, x: 0, y: 0, capacity: 150 }
    ];
    let customers = vec![
        Customer { id: 101, x: 20, y: 20, demand: 70 },
        Customer { id: 102, x: 25, y: 25, demand: 60 }
    ];
    let routes = vec![
        Route { from: 1, to: 101, cost: 5.0 },
        Route { from: 101, to: 1, cost: 5.0 },
        Route { from: 1, to: 102, cost: 5.0 },
        Route { from: 102, to: 1, cost: 5.0 },
        // Add an inter-customer route
        Route { from: 101, to: 102, cost: 8.0 },
        Route { from: 102, to: 101, cost: 8.0 },
    ];

    // Set a high disruption probability.
    let disruption_prob = 0.5;
    let simulations = 200;

    let result = optimize_network(&warehouses, &customers, &routes, disruption_prob, simulations);
    assert!(result.is_ok(), "Expected a valid solution even under high disruption.");

    let (_, _, resilience_score) = result.unwrap();
    // With high disruption, resilience_score can be lower, but still should be in [0,1]
    assert!(resilience_score >= 0.0 && resilience_score <= 1.0, "Resilience score should be between 0 and 1.");
}

#[test]
fn test_warehouse_capacity_constraint() {
    // Create a scenario where one warehouse cannot supply all customers due to capacity limit.
    let warehouses = vec![
        Warehouse { id: 1, x: 0, y: 0, capacity: 80 },
        Warehouse { id: 2, x: 10, y: 0, capacity: 50 },
    ];
    let customers = vec![
        Customer { id: 101, x: 5, y: 5, demand: 70 },
        Customer { id: 102, x: 15, y: 5, demand: 50 },
    ];
    let routes = vec![
        // Routes from warehouse 1
        Route { from: 1, to: 101, cost: 4.0 },
        Route { from: 101, to: 1, cost: 4.0 },
        Route { from: 1, to: 102, cost: 6.0 },
        Route { from: 102, to: 1, cost: 6.0 },
        // Routes from warehouse 2
        Route { from: 2, to: 101, cost: 5.0 },
        Route { from: 101, to: 2, cost: 5.0 },
        Route { from: 2, to: 102, cost: 3.0 },
        Route { from: 102, to: 2, cost: 3.0 },
        // Inter-warehouse connection
        Route { from: 1, to: 2, cost: 2.0 },
        Route { from: 2, to: 1, cost: 2.0 },
    ];

    let disruption_prob = 0.05;
    let simulations = 100;

    let result = optimize_network(&warehouses, &customers, &routes, disruption_prob, simulations);
    assert!(result.is_ok(), "Expected a valid optimal flow that respects warehouse capacities.");

    let (optimal_flow, _, _) = result.unwrap();

    // Verify that no warehouse sends more than its capacity.
    let mut warehouse_sent: std::collections::HashMap<usize, u32> = std::collections::HashMap::new();
    for (from, _to, flow) in &optimal_flow {
        *warehouse_sent.entry(*from).or_insert(0) += *flow;
    }
    for wh in &warehouses {
        if let Some(sent) = warehouse_sent.get(&wh.id) {
            assert!(*sent <= wh.capacity, "Warehouse {} exceeded its capacity.", wh.id);
        }
    }
}