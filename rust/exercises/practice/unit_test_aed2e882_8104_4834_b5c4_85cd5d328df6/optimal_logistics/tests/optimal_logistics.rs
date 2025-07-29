use optimal_logistics::{optimize_logistics, DeliveryRequest, Edge, Network};

#[test]
fn test_basic_delivery() {
    // Single delivery that can be fulfilled on one edge.
    let network = Network {
        num_warehouses: 2,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 5,
                capacity: 10,
                time: 2,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 1,
                quantity: 5,
                deadline: 3,
            },
        ],
    };
    // Expected cost: 5 units * cost 5 = 25.
    let result = optimize_logistics(&network);
    assert_eq!(result, Some(25));
}

#[test]
fn test_insufficient_capacity() {
    // Delivery request quantity exceeds the available capacity on the only edge.
    let network = Network {
        num_warehouses: 2,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 10,
                capacity: 5,
                time: 1,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 1,
                quantity: 8,
                deadline: 5,
            },
        ],
    };
    let result = optimize_logistics(&network);
    assert_eq!(result, None);
}

#[test]
fn test_deadline_violation() {
    // Even though capacity is available, the transit times force the delivery past the deadline.
    let network = Network {
        num_warehouses: 2,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 4,
                capacity: 10,
                time: 5,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 1,
                quantity: 3,
                deadline: 4,
            },
        ],
    };
    let result = optimize_logistics(&network);
    assert_eq!(result, None);
}

#[test]
fn test_multiple_routes() {
    // A network where two different paths exist from origin to destination.
    // Path 1: Direct 0->1 costs 7 per unit, capacity 5, time 1.
    // Path 2: 0->2->1 costs 3+3 = 6 per unit, capacity min(10,10)=10, time 2.
    // Request: deliver 8 units from 0 to 1 with deadline 3.
    // Optimal: use path 2 for all units at total cost = 8 * 6 = 48.
    let network = Network {
        num_warehouses: 3,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 7,
                capacity: 5,
                time: 1,
            },
            Edge {
                from: 0,
                to: 2,
                cost: 3,
                capacity: 10,
                time: 1,
            },
            Edge {
                from: 2,
                to: 1,
                cost: 3,
                capacity: 10,
                time: 1,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 1,
                quantity: 8,
                deadline: 3,
            },
        ],
    };
    let result = optimize_logistics(&network);
    assert_eq!(result, Some(48));
}

#[test]
fn test_multiple_requests() {
    // A network with multiple requests that may share some routes.
    // Network structure:
    //   0 -> 1: cost 1, capacity 10, time 1
    //   1 -> 3: cost 1, capacity 10, time 1
    //   0 -> 2: cost 2, capacity 5, time 1
    //   2 -> 3: cost 2, capacity 5, time 1
    // There are two requests:
    //   Request A: from 0 to 3, quantity 8, deadline 3.
    //   Request B: from 0 to 2, quantity 4, deadline 2.
    //
    // Optimal assignment:
    //   For Request A, use path 0->1->3 with cost = 1 + 1 = 2 per unit, total = 16.
    //   For Request B, use direct path 0->2 with cost = 2 per unit, total = 8.
    // Combined total expected cost = 16 + 8 = 24.
    let network = Network {
        num_warehouses: 4,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 1,
                capacity: 10,
                time: 1,
            },
            Edge {
                from: 1,
                to: 3,
                cost: 1,
                capacity: 10,
                time: 1,
            },
            Edge {
                from: 0,
                to: 2,
                cost: 2,
                capacity: 5,
                time: 1,
            },
            Edge {
                from: 2,
                to: 3,
                cost: 2,
                capacity: 5,
                time: 1,
            },
            // Additional edge to allow alternative routing if needed.
            Edge {
                from: 1,
                to: 2,
                cost: 1,
                capacity: 5,
                time: 1,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 3,
                quantity: 8,
                deadline: 3,
            },
            DeliveryRequest {
                origin: 0,
                destination: 2,
                quantity: 4,
                deadline: 2,
            },
        ],
    };
    let result = optimize_logistics(&network);
    assert_eq!(result, Some(24));
}

#[test]
fn test_zero_quantity_request() {
    // A request with zero quantity should incur no cost.
    let network = Network {
        num_warehouses: 2,
        edges: vec![
            Edge {
                from: 0,
                to: 1,
                cost: 10,
                capacity: 5,
                time: 1,
            },
        ],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 1,
                quantity: 0,
                deadline: 5,
            },
        ],
    };
    let result = optimize_logistics(&network);
    // Since no units need to be transported, cost is zero.
    assert_eq!(result, Some(0));
}

#[test]
fn test_empty_network() {
    // An empty network with a nonzero delivery request should result in failure.
    let network = Network {
        num_warehouses: 0,
        edges: vec![],
        requests: vec![
            DeliveryRequest {
                origin: 0,
                destination: 0,
                quantity: 5,
                deadline: 5,
            },
        ],
    };
    let result = optimize_logistics(&network);
    assert_eq!(result, None);
}