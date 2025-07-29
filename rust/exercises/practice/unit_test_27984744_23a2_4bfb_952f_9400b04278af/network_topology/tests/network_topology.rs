use network_topology::NetworkTopology;

#[test]
fn test_add_and_remove_node() {
    let mut net = NetworkTopology::new();
    // Initially the network should not contain node 1.
    assert!(!net.contains_node(1));
    // Add node 1 and ensure it exists.
    net.add_node(1);
    assert!(net.contains_node(1));
    // Adding a duplicate node should not affect the network.
    net.add_node(1);
    assert!(net.contains_node(1));
    // Remove node 1 and check it is removed.
    net.remove_node(1);
    assert!(!net.contains_node(1));
}

#[test]
fn test_add_and_remove_link() {
    let mut net = NetworkTopology::new();
    net.add_node(1);
    net.add_node(2);
    // Initially, there is no link so shortest path should be None.
    assert_eq!(net.shortest_path(1, 2), None);
    // Add a link from 1 -> 2 with latency 10.
    net.add_link(1, 2, 10);
    assert_eq!(net.shortest_path(1, 2), Some(10));
    // Removing the link should clear the path.
    net.remove_link(1, 2);
    assert_eq!(net.shortest_path(1, 2), None);
}

#[test]
fn test_shortest_path() {
    let mut net = NetworkTopology::new();
    // Create nodes 1 to 5.
    for i in 1..=5 {
        net.add_node(i);
    }
    // Construct the graph:
    // 1 -> 2 (latency 3)
    // 2 -> 3 (latency 4)
    // 1 -> 3 (latency 10)
    // 3 -> 4 (latency 2)
    // 4 -> 5 (latency 1)
    net.add_link(1, 2, 3);
    net.add_link(2, 3, 4);
    net.add_link(1, 3, 10);
    net.add_link(3, 4, 2);
    net.add_link(4, 5, 1);
    // The shortest path from 1 to 3 should follow 1 -> 2 -> 3 with total latency 7.
    assert_eq!(net.shortest_path(1, 3), Some(7));
    // The shortest path from 1 to 5 should be 1->2->3->4->5 with total latency 10.
    assert_eq!(net.shortest_path(1, 5), Some(10));
}

#[test]
fn test_strongly_connected_empty_and_single() {
    let mut net = NetworkTopology::new();
    // An empty network is by definition strongly connected.
    assert!(net.is_strongly_connected());
    // A single node network is also strongly connected.
    net.add_node(42);
    assert!(net.is_strongly_connected());
}

#[test]
fn test_is_strongly_connected() {
    let mut net = NetworkTopology::new();
    // Build a strongly connected graph with nodes 1 to 4.
    for i in 1..=4 {
        net.add_node(i);
    }
    // Create a circular connection:
    // 1 -> 2, 2 -> 3, 3 -> 4, 4 -> 1.
    net.add_link(1, 2, 1);
    net.add_link(2, 3, 1);
    net.add_link(3, 4, 1);
    net.add_link(4, 1, 1);
    assert!(net.is_strongly_connected());
    // Adding an extra link should not break strong connectivity.
    net.add_link(1, 3, 2);
    assert!(net.is_strongly_connected());
    // Removing a link from the circle that disconnects the cycle should cause failure.
    net.remove_link(4, 1);
    assert!(!net.is_strongly_connected());
}

#[test]
fn test_find_critical_links() {
    let mut net = NetworkTopology::new();
    // Build a graph with nodes 1, 2, and 3.
    for i in 1..=3 {
        net.add_node(i);
    }
    // Add links:
    // 1 -> 2 (latency 1)
    // 2 -> 3 (latency 1)
    // 1 -> 3 (latency 3)
    net.add_link(1, 2, 1);
    net.add_link(2, 3, 1);
    net.add_link(1, 3, 3);
    // The shortest path from 1 to 3 is via 1->2->3 (latency 2).
    // Removing link 1->2 or 2->3 would increase latency, making them critical.
    // Removing link 1->3 would not affect the shortest path.
    let critical_links = net.find_critical_links();
    assert!(critical_links.contains(&(1, 2)));
    assert!(critical_links.contains(&(2, 3)));
    assert!(!critical_links.contains(&(1, 3)));
}

#[test]
fn test_edge_cases() {
    let mut net = NetworkTopology::new();
    // Operations on non-existent nodes and links should be gracefully ignored.
    net.remove_node(10);
    net.remove_link(1, 2);
    net.add_link(1, 2, 5);
    // Since nodes haven't been added, there is no valid path.
    assert_eq!(net.shortest_path(1, 2), None);
    // Add required nodes.
    net.add_node(1);
    net.add_node(2);
    // Test self-loop, which should yield a zero latency path.
    net.add_link(1, 1, 0);
    assert_eq!(net.shortest_path(1, 1), Some(0));
    // Remove non-existent link should be a no-op.
    net.remove_link(2, 1);
    // Test proper removal of links upon node removal.
    net.add_link(1, 2, 5);
    assert_eq!(net.shortest_path(1, 2), Some(5));
    net.remove_node(1);
    assert_eq!(net.shortest_path(1, 2), None);
}