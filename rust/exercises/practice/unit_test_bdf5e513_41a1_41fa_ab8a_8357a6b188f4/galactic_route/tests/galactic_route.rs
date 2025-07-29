use galactic_route::{Edge, Node, find_max_reliability};

#[test]
fn test_direct_route_valid() {
    let nodes = vec![
        Node { id: 1, resource: 100, security: 5 },
        Node { id: 2, resource: 80, security: 3 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 10, stability: 0.9 },
    ];
    let result = find_max_reliability(&nodes, &edges, 1, 2, 80, 10);
    assert!((result - 0.9).abs() < 1e-6);
}

#[test]
fn test_direct_route_invalid_resource() {
    let nodes = vec![
        Node { id: 1, resource: 100, security: 5 },
        Node { id: 2, resource: 80, security: 3 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 10, stability: 0.9 },
    ];
    let result = find_max_reliability(&nodes, &edges, 1, 2, 90, 10);
    assert!((result - 0.0).abs() < 1e-6);
}

#[test]
fn test_alternative_routes() {
    let nodes = vec![
        Node { id: 1, resource: 100, security: 5 },
        Node { id: 2, resource: 90, security: 2 },
        Node { id: 3, resource: 95, security: 4 },
        Node { id: 4, resource: 100, security: 3 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 10, stability: 0.9 },
        Edge { source: 2, destination: 4, cost: 10, stability: 0.8 },
        Edge { source: 1, destination: 3, cost: 15, stability: 0.85 },
        Edge { source: 3, destination: 4, cost: 10, stability: 0.95 },
    ];
    // For min_resource = 90 and max_security = 15:
    // Route 1->2->4: min_resource = 90, security = 5+2+3 = 10, reliability = 0.9 * 0.8 = 0.72
    // Route 1->3->4: min_resource = 95, security = 5+4+3 = 12, reliability = 0.85 * 0.95 = 0.8075
    let result = find_max_reliability(&nodes, &edges, 1, 4, 90, 15);
    assert!((result - 0.8075).abs() < 1e-6);
}

#[test]
fn test_security_risk_threshold() {
    let nodes = vec![
        Node { id: 1, resource: 100, security: 5 },
        Node { id: 2, resource: 90, security: 2 },
        Node { id: 3, resource: 95, security: 4 },
        Node { id: 4, resource: 100, security: 3 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 10, stability: 0.9 },
        Edge { source: 2, destination: 4, cost: 10, stability: 0.8 },
        Edge { source: 1, destination: 3, cost: 15, stability: 0.85 },
        Edge { source: 3, destination: 4, cost: 10, stability: 0.95 },
    ];
    // For min_resource = 90 and max_security = 10:
    // Route 1->2->4 is valid (security = 5+2+3 = 10; reliability = 0.9 * 0.8 = 0.72)
    // Route 1->3->4 exceeds the security threshold (security = 5+4+3 = 12)
    let result = find_max_reliability(&nodes, &edges, 1, 4, 90, 10);
    assert!((result - 0.72).abs() < 1e-6);
}

#[test]
fn test_no_valid_route() {
    let nodes = vec![
        Node { id: 1, resource: 50, security: 5 },
        Node { id: 2, resource: 45, security: 3 },
        Node { id: 3, resource: 60, security: 4 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 10, stability: 0.8 },
        Edge { source: 2, destination: 3, cost: 10, stability: 0.7 },
    ];
    // The minimum resource required is higher than the production of at least one node in any route.
    let result = find_max_reliability(&nodes, &edges, 1, 3, 55, 15);
    assert!((result - 0.0).abs() < 1e-6);
}

#[test]
fn test_route_with_cycle() {
    let nodes = vec![
        Node { id: 1, resource: 100, security: 1 },
        Node { id: 2, resource: 100, security: 1 },
        Node { id: 3, resource: 100, security: 10 },
    ];
    let edges = vec![
        Edge { source: 1, destination: 2, cost: 5, stability: 0.9 },
        Edge { source: 2, destination: 3, cost: 5, stability: 0.8 },
        Edge { source: 1, destination: 3, cost: 12, stability: 0.5 },
        // Cycle edge (should not be reused in any route)
        Edge { source: 2, destination: 1, cost: 5, stability: 0.9 },
    ];
    // For min_resource = 100 and max_security = 12:
    // Valid routes:
    // Direct: 1->3 with security = 1+10 = 11, reliability = 0.5
    // Alternative: 1->2->3 with security = 1+1+10 = 12, reliability = 0.9 * 0.8 = 0.72
    let result = find_max_reliability(&nodes, &edges, 1, 3, 100, 12);
    assert!((result - 0.72).abs() < 1e-6);
}