use std::collections::HashSet;
use dynamic_partition::Network;

#[test]
fn test_single_partition() {
    // Test with K = 1 where all nodes should be in one sub-network.
    let mut network = Network::new(5, 1);
    // Connect nodes in a chain: 0-1-2-3-4.
    network.connect(0, 1);
    network.connect(1, 2);
    network.connect(2, 3);
    network.connect(3, 4);

    let parts = network.partition();
    assert_eq!(parts.len(), 1);
    let mut all_nodes = HashSet::new();
    for part in parts.iter() {
        all_nodes.extend(part.iter());
    }
    let expected: HashSet<usize> = (0..5).collect();
    assert_eq!(all_nodes, expected);
}

#[test]
fn test_multiple_partitions_disconnected() {
    // Test for a network with disconnected components.
    let mut network = Network::new(6, 3);
    // Create two connected components and isolated nodes.
    network.connect(0, 1);   // Component 1: nodes 0, 1.
    network.connect(2, 3);   // Component 2: nodes 2, 3.
    // Nodes 4 and 5 remain isolated.

    let parts = network.partition();
    assert_eq!(parts.len(), 3);
    let mut union: HashSet<usize> = HashSet::new();
    for part in parts.iter() {
        for &node in part.iter() {
            union.insert(node);
        }
    }
    let expected: HashSet<usize> = (0..6).collect();
    assert_eq!(union, expected);
}

#[test]
fn test_add_remove_nodes() {
    // Test the addition and removal of nodes.
    let mut network = Network::new(3, 2);
    // Initial nodes: 0, 1, 2.
    network.connect(0, 1);
    network.connect(1, 2);

    // Add a new node with id 3.
    network.add_node(3);
    network.connect(2, 3);

    // Remove node 1.
    network.remove_node(1);

    let parts = network.partition();
    assert_eq!(parts.len(), 2);
    let mut union: HashSet<usize> = HashSet::new();
    for part in parts.iter() {
        union.extend(part.iter().cloned());
    }
    // Expect nodes: 0, 2, 3 (node 1 is removed).
    let expected: HashSet<usize> = [0, 2, 3].iter().cloned().collect();
    assert_eq!(union, expected);
}

#[test]
fn test_connect_disconnect() {
    // Test the connect and disconnect operations.
    let mut network = Network::new(4, 2);
    network.connect(0, 1);
    network.connect(1, 2);
    network.connect(2, 3);

    let parts_initial = network.partition();
    assert_eq!(parts_initial.len(), 2);
    // Disconnect a connection to change graph topology.
    network.disconnect(1, 2);

    let parts_after = network.partition();
    assert_eq!(parts_after.len(), 2);
    // Ensure that the union of nodes before and after remains the same.
    let union_initial: HashSet<usize> =
        parts_initial.iter().flat_map(|s| s.iter()).cloned().collect();
    let union_after: HashSet<usize> =
        parts_after.iter().flat_map(|s| s.iter()).cloned().collect();
    let expected: HashSet<usize> = (0..4).collect();
    assert_eq!(union_initial, expected);
    assert_eq!(union_after, expected);
}

#[test]
fn test_partition_remains_stable() {
    // Test that consecutive partition calls preserve the network structure.
    let mut network = Network::new(7, 3);
    // Create multiple clusters.
    network.connect(0, 1);
    network.connect(1, 2);
    network.connect(2, 0);
    network.connect(3, 4);
    network.connect(4, 5);
    network.connect(5, 3);
    network.connect(5, 6);

    let parts_first = network.partition();
    let union_first: HashSet<usize> =
        parts_first.iter().flat_map(|s| s.iter()).cloned().collect();
    let expected: HashSet<usize> = (0..7).collect();
    assert_eq!(union_first, expected);

    // Call partition again and verify that the structure remains intact.
    let parts_second = network.partition();
    let union_second: HashSet<usize> =
        parts_second.iter().flat_map(|s| s.iter()).cloned().collect();
    assert_eq!(union_second, expected);
}

#[test]
fn test_n_less_than_k() {
    // Test when the number of nodes is less than the number of desired partitions.
    let mut network = Network::new(2, 5);
    network.connect(0, 1);

    let parts = network.partition();
    assert_eq!(parts.len(), 5);
    let union: HashSet<usize> =
        parts.iter().flat_map(|s| s.iter()).cloned().collect();
    let expected: HashSet<usize> = (0..2).collect();
    assert_eq!(union, expected);

    // Check that at least some partitions are empty.
    let empty_parts = parts.iter().filter(|p| p.is_empty()).count();
    assert!(empty_parts > 0);
}