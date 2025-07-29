use network_flow::{Edge, min_cost_flow};

#[test]
fn test_simple_linear() {
    let edges = vec![
        Edge {
            from: 0,
            to: 1,
            capacity: 10.0,
            cost: Box::new(|flow: f64| flow * 2.0),
        },
    ];
    let result = min_cost_flow(2, edges, 0, 1, 5.0);
    match result {
        Ok(cost) => assert!((cost - 10.0).abs() < 1e-6),
        Err(_) => panic!("Expected feasible flow, got error"),
    }
}

#[test]
fn test_multiple_routes() {
    let edges = vec![
        // Path 0 -> 1 -> 3
        Edge {
            from: 0,
            to: 1,
            capacity: 4.0,
            cost: Box::new(|flow: f64| flow * 1.0),
        },
        Edge {
            from: 1,
            to: 3,
            capacity: 4.0,
            cost: Box::new(|flow: f64| flow * 2.0),
        },
        // Path 0 -> 2 -> 3
        Edge {
            from: 0,
            to: 2,
            capacity: 8.0,
            cost: Box::new(|flow: f64| flow * 2.0),
        },
        Edge {
            from: 2,
            to: 3,
            capacity: 8.0,
            cost: Box::new(|flow: f64| flow * 1.0),
        },
    ];
    let result = min_cost_flow(4, edges, 0, 3, 8.0);
    match result {
        Ok(cost) => assert!((cost - 24.0).abs() < 1e-6),
        Err(_) => panic!("Expected feasible flow, got error"),
    }
}

#[test]
fn test_infeasible_flow() {
    let edges = vec![
        Edge {
            from: 0,
            to: 1,
            capacity: 3.0,
            cost: Box::new(|flow: f64| flow * 1.0),
        },
    ];
    let result = min_cost_flow(2, edges, 0, 1, 5.0);
    assert!(result.is_err());
}

#[test]
fn test_cycle_handling() {
    let edges = vec![
        Edge {
            from: 0,
            to: 1,
            capacity: 10.0,
            cost: Box::new(|flow: f64| flow * 1.0),
        },
        Edge {
            from: 1,
            to: 2,
            capacity: 10.0,
            cost: Box::new(|flow: f64| flow * 1.0),
        },
        // Introduce a cycle with a back edge
        Edge {
            from: 2,
            to: 1,
            capacity: 5.0,
            cost: Box::new(|flow: f64| flow * 0.5),
        },
    ];
    let result = min_cost_flow(3, edges, 0, 2, 6.0);
    match result {
        Ok(cost) => assert!((cost - 12.0).abs() < 1e-6),
        Err(_) => panic!("Expected feasible flow, got error"),
    }
}

#[test]
fn test_nonlinear_cost() {
    let edges = vec![
        Edge {
            from: 0,
            to: 1,
            capacity: 10.0,
            cost: Box::new(|flow: f64| flow * flow),
        },
    ];
    let result = min_cost_flow(2, edges, 0, 1, 3.0);
    match result {
        Ok(cost) => assert!((cost - 9.0).abs() < 1e-6),
        Err(_) => panic!("Expected feasible flow, got error"),
    }
}