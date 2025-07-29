use std::collections::HashMap;
use network_congestion::minimize_congestion;

#[test]
fn test_single_route() {
    // Simple network with a single packet route.
    let n = 3;
    let edges = vec![(0, 1, 100), (1, 2, 100)];
    let packet_routes = vec![(0, 2, 50)];
    let mut routing_table = HashMap::new();
    routing_table.insert((0, 2), vec![0, 1, 2]);
    
    let result = minimize_congestion(n, edges, packet_routes, routing_table);
    assert_eq!(result, 50);
}

#[test]
fn test_multiple_routes() {
    // Network with multiple packet routes crossing different nodes.
    let n = 4;
    let edges = vec![(0, 1, 10), (1, 2, 10), (2, 3, 10), (0, 2, 15)];
    let packet_routes = vec![
        (0, 3, 10),  // This will go through 0,1,2,3
        (0, 2, 15),  // This will go through 0,2
        (1, 3, 5),   // This will go through 1,2,3
    ];
    let mut routing_table = HashMap::new();
    routing_table.insert((0, 3), vec![0, 1, 2, 3]);
    routing_table.insert((0, 2), vec![0, 2]);
    routing_table.insert((1, 3), vec![1, 2, 3]);
    
    // Node congestions:
    // Node 0: 10 (from 0->3) + 15 (from 0->2) = 25
    // Node 1: 10 (from 0->3) + 5 (from 1->3) = 15
    // Node 2: 10 (from 0->3) + 15 (from 0->2) + 5 (from 1->3) = 30
    // Node 3: 10 (from 0->3) + 5 (from 1->3) = 15
    // Maximum congestion is 30.
    let result = minimize_congestion(n, edges, packet_routes, routing_table);
    assert_eq!(result, 30);
}

#[test]
fn test_disconnected_graph() {
    // Graph is disconnected; the provided route should trigger a -1.
    let n = 4;
    let edges = vec![(0, 1, 10)]; // Only nodes 0 and 1 are connected.
    let packet_routes = vec![(0, 3, 10)];
    let mut routing_table = HashMap::new();
    // Even though routing table provides a route, the underlying graph is disconnected.
    routing_table.insert((0, 3), vec![0, 1, 3]);
    
    let result = minimize_congestion(n, edges, packet_routes, routing_table);
    assert_eq!(result, -1);
}

#[test]
fn test_complex_network() {
    // A more complex network with several overlapping packet routes.
    let n = 6;
    let edges = vec![
        (0, 1, 10),
        (1, 2, 10),
        (2, 3, 10),
        (3, 4, 10),
        (4, 5, 10),
        (0, 5, 15),
        (1, 4, 15),
        (2, 5, 20),
    ];
    let packet_routes = vec![
        (0, 3, 5),   // Route: 0, 1, 2, 3
        (0, 5, 10),  // Route: 0, 1, 4, 5
        (1, 3, 10),  // Route: 1, 2, 3
        (2, 5, 20),  // Route: 2, 3, 4, 5
    ];
    let mut routing_table = HashMap::new();
    routing_table.insert((0, 3), vec![0, 1, 2, 3]);
    routing_table.insert((0, 5), vec![0, 1, 4, 5]);
    routing_table.insert((1, 3), vec![1, 2, 3]);
    routing_table.insert((2, 5), vec![2, 3, 4, 5]);
    
    // Expected congestion:
    // Node 0: 5 (from 0->3) + 10 (from 0->5) = 15
    // Node 1: 5 (from 0->3) + 10 (from 0->5) + 10 (from 1->3) = 25
    // Node 2: 5 (from 0->3) + 10 (from 1->3) + 20 (from 2->5) = 35
    // Node 3: 5 (from 0->3) + 10 (from 1->3) + 20 (from 2->5) = 35
    // Node 4: 10 (from 0->5) + 20 (from 2->5) = 30
    // Node 5: 10 (from 0->5) + 20 (from 2->5) = 30
    // Maximum congestion is 35.
    let result = minimize_congestion(n, edges, packet_routes, routing_table);
    assert_eq!(result, 35);
}