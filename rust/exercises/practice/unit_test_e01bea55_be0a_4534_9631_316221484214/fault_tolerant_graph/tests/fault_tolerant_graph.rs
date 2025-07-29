use std::sync::{Arc, Barrier};
use std::thread;
use fault_tolerant_graph::*;

#[test]
fn test_add_nodes_and_edges() {
    let mut graph = FaultTolerantGraph::new();
    // Add nodes with unique ids and payloads.
    assert!(graph.add_node(1, "Alice".to_string()).is_ok());
    assert!(graph.add_node(2, "Bob".to_string()).is_ok());
    assert!(graph.add_node(3, "Charlie".to_string()).is_ok());

    // Add edges: 1 -> 2, 2 -> 3, and an alternative edge 1 -> 3.
    assert!(graph.add_edge(1, 2, "friend".to_string()).is_ok());
    assert!(graph.add_edge(2, 3, "colleague".to_string()).is_ok());
    assert!(graph.add_edge(1, 3, "neighbor".to_string()).is_ok());

    // Check approximate path from 1 to 3. The returned path should start with 1, end with 3,
    // and have a length between 2 and the specified max hop count.
    let path = graph.approximate_shortest_path(1, 3, 3);
    assert!(path.is_some());
    let path = path.unwrap();
    assert_eq!(path.first(), Some(&1));
    assert_eq!(path.last(), Some(&3));
    assert!(path.len() <= 3 && path.len() >= 2);
}

#[test]
fn test_node_unavailability() {
    let mut graph = FaultTolerantGraph::new();
    // Build a simple chain graph: 1 -> 2 -> 3 -> 4.
    for node in 1..=4 {
        let payload = format!("Node{}", node);
        assert!(graph.add_node(node, payload).is_ok());
    }
    assert!(graph.add_edge(1, 2, "edge12".to_string()).is_ok());
    assert!(graph.add_edge(2, 3, "edge23".to_string()).is_ok());
    assert!(graph.add_edge(3, 4, "edge34".to_string()).is_ok());

    // Mark node 2 as unavailable.
    assert!(graph.mark_unavailable(2).is_ok());
    // With node 2 unavailable, there is no valid path from 1 to 4.
    let path = graph.approximate_shortest_path(1, 4, 4);
    assert!(path.is_none());

    // Restore node 2.
    assert!(graph.mark_available(2).is_ok());
    let path = graph.approximate_shortest_path(1, 4, 4);
    assert!(path.is_some());
    let route = path.unwrap();
    assert_eq!(route.first(), Some(&1));
    assert_eq!(route.last(), Some(&4));
}

#[test]
fn test_remove_node() {
    let mut graph = FaultTolerantGraph::new();
    // Create nodes and edges: 1 -> 2 and 2 -> 3.
    assert!(graph.add_node(1, "A".to_string()).is_ok());
    assert!(graph.add_node(2, "B".to_string()).is_ok());
    assert!(graph.add_node(3, "C".to_string()).is_ok());
    assert!(graph.add_edge(1, 2, "edge".to_string()).is_ok());
    assert!(graph.add_edge(2, 3, "edge".to_string()).is_ok());

    // Remove node 2.
    assert!(graph.remove_node(2).is_ok());
    // After removal, any path involving node 2 should not be found.
    let path = graph.approximate_shortest_path(1, 3, 3);
    assert!(path.is_none());
}

#[test]
fn test_remove_edge() {
    let mut graph = FaultTolerantGraph::new();
    // Add two nodes.
    assert!(graph.add_node(1, "X".to_string()).is_ok());
    assert!(graph.add_node(2, "Y".to_string()).is_ok());
    // Add multiple edges from node 1 to node 2.
    assert!(graph.add_edge(1, 2, "edge1".to_string()).is_ok());
    assert!(graph.add_edge(1, 2, "edge2".to_string()).is_ok());
    
    // Remove one specific edge by matching its payload.
    assert!(graph.remove_edge(1, 2, Some("edge1".to_string())).is_ok());
    // The path from 1 to 2 should still be available via the remaining edge.
    let path = graph.approximate_shortest_path(1, 2, 2);
    assert!(path.is_some());
    
    // Remove the remaining edge.
    assert!(graph.remove_edge(1, 2, Some("edge2".to_string())).is_ok());
    let path = graph.approximate_shortest_path(1, 2, 2);
    assert!(path.is_none());
}

#[test]
fn test_same_node_path() {
    let mut graph = FaultTolerantGraph::new();
    // Create a node.
    assert!(graph.add_node(10, "Self".to_string()).is_ok());
    // The trivial path from a node to itself should return a vector containing just that node.
    let path = graph.approximate_shortest_path(10, 10, 1);
    assert_eq!(path, Some(vec![10]));
}

#[test]
fn test_nonexistent_nodes() {
    let mut graph = FaultTolerantGraph::new();
    // Try adding an edge where neither node exists.
    assert!(graph.add_edge(100, 200, "nonexistent edge".to_string()).is_err());
    // Try removing a node that doesn't exist.
    assert!(graph.remove_node(300).is_err());
    // Marking non-existent nodes as unavailable or available should return errors.
    assert!(graph.mark_unavailable(400).is_err());
    assert!(graph.mark_available(500).is_err());
}

#[test]
fn test_concurrent_reads() {
    let mut graph = FaultTolerantGraph::new();
    // Build a small linear graph: 1 -> 2 -> 3 -> 4 -> 5.
    for i in 1..=5 {
        assert!(graph.add_node(i, format!("Node{}", i)).is_ok());
    }
    for i in 1..5 {
        assert!(graph.add_edge(i, i + 1, format!("edge{}{}", i, i + 1)).is_ok());
    }
    let graph_arc = Arc::new(graph);
    let barrier = Arc::new(Barrier::new(5));
    let mut handles = Vec::new();
    // Launch multiple threads to perform concurrent read operations.
    for _ in 0..5 {
        let graph_clone = Arc::clone(&graph_arc);
        let barrier_clone = Arc::clone(&barrier);
        let handle = thread::spawn(move || {
            barrier_clone.wait();
            let res = graph_clone.approximate_shortest_path(1, 5, 5);
            assert!(res.is_some());
            let path = res.unwrap();
            assert_eq!(path.first(), Some(&1));
            assert_eq!(path.last(), Some(&5));
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().expect("Thread panicked");
    }
}