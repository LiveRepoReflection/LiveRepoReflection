use net_route::optimal_route;

#[test]
fn test_basic_route() {
    // Single packet from 0 to 2 through path 0->1->2.
    // Expected cost: packet_size * (edge cost 0->1 + edge cost 1->2)
    // Here: 10 * (5 + 10) = 150.
    let n = 3;
    let edges = vec![(0, 1, 5), (1, 2, 10)];
    let capacities = vec![100, 100, 100];
    let packets = vec![(0, 2, 10, 50)]; // (source, destination, size, priority)
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, Some(150));
}

#[test]
fn test_alternative_paths() {
    // Graph with two alternative paths:
    // Path A: 0->1->3 with cost (5+5)=10; Path B: 0->2->3 with cost (7+3)=10.
    // Single packet from 0 to 3, size 10.
    // The optimal cost is 10 * 10 = 100.
    let n = 4;
    let edges = vec![(0, 1, 5), (1, 3, 5), (0, 2, 7), (2, 3, 3)];
    let capacities = vec![100, 100, 100, 100];
    let packets = vec![(0, 3, 10, 50)];
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, Some(100));
}

#[test]
fn test_unreachable_destination() {
    // Destination 2 is unreachable from source 0.
    let n = 3;
    let edges = vec![(0, 1, 10)]; // No edge towards node 2.
    let capacities = vec![100, 100, 100];
    let packets = vec![(0, 2, 10, 50)];
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, None);
}

#[test]
fn test_capacity_failure() {
    // Even though there is a route from 0 to 2, node 1's capacity isn't enough.
    // Route: 0->1->2. Node 1 capacity is 10, but packet size is 15.
    let n = 3;
    let edges = vec![(0, 1, 5), (1, 2, 5)];
    let capacities = vec![20, 10, 20];
    let packets = vec![(0, 2, 15, 50)];
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, None);
}

#[test]
fn test_multiple_packets() {
    // Two packets from 0 to 3 sharing the same network.
    // Graph:
    //   0 -> 1 (cost 2), 1 -> 3 (cost 2)
    //   0 -> 2 (cost 3), 2 -> 3 (cost 1)
    // Packets:
    //   High priority: (0, 3, 10, 80)
    //   Low priority:  (0, 3, 5, 20)
    // Both packets can be routed using their optimal costs:
    //   For both, the cheapest route has cost 2+2 = 4 (or 3+1 = 4).
    // Total cost = 10*4 + 5*4 = 40 + 20 = 60.
    let n = 4;
    let edges = vec![(0, 1, 2), (1, 3, 2), (0, 2, 3), (2, 3, 1)];
    let capacities = vec![100, 100, 100, 100];
    let packets = vec![(0, 3, 10, 80), (0, 3, 5, 20)];
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, Some(60));
}

#[test]
fn test_packet_splitting() {
    // Test where optimal routing may require splitting a packet among two paths
    // to satisfy an intermediate node's capacity constraint.
    // Graph:
    //   0 -> 1 (cost 4), 1 -> 3 (cost 4)
    //   0 -> 2 (cost 6), 2 -> 3 (cost 2)
    // Node 1 has limited capacity, so part of the flow has to be rerouted through node 2.
    // Capacities: node0: 100, node1: 8, node2: 100, node3: 100.
    // Packet: (0, 3, 10, 50)
    // Option:
    //   Send 8 units via 0->1->3: cost = 8 * (4+4) = 64.
    //   Send 2 units via 0->2->3: cost = 2 * (6+2) = 16.
    // Total expected cost = 64 + 16 = 80.
    let n = 4;
    let edges = vec![(0, 1, 4), (1, 3, 4), (0, 2, 6), (2, 3, 2)];
    let capacities = vec![100, 8, 100, 100];
    let packets = vec![(0, 3, 10, 50)];
    let result = optimal_route(n, edges, capacities, packets);
    assert_eq!(result, Some(80));
}