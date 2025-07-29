use dynamic_shortest_path::{Graph, Update};

#[test]
fn test_basic_path() {
    // Graph:
    // 1 -> 2 (4), 2 -> 3 (3), 1 -> 3 (8)
    let initial_edges = vec![(1, 2, 4), (2, 3, 3), (1, 3, 8)];
    let source_cities = vec![1];
    let mut graph = Graph::new(initial_edges, source_cities);

    // Query shortest path from source (1) to city 3 should be 7 via 1->2->3 (4+3)
    assert_eq!(graph.query(3), 7);
}

#[test]
fn test_multiple_sources() {
    // Graph:
    // 1 -> 2 (2), 2 -> 3 (5), 4 -> 3 (1), 1 -> 5 (10)
    let initial_edges = vec![(1, 2, 2), (2, 3, 5), (4, 3, 1), (1, 5, 10)];
    let source_cities = vec![1, 4];
    let mut graph = Graph::new(initial_edges, source_cities);

    // Query shortest path to city 3 should be 1 from source 4.
    assert_eq!(graph.query(3), 1);
}

#[test]
fn test_update_add_remove() {
    // Start with an empty graph and source 1.
    let initial_edges = vec![];
    let source_cities = vec![1];
    let mut graph = Graph::new(initial_edges, source_cities);

    // Initially, no path exists to city 3.
    assert_eq!(graph.query(3), -1);

    // Add edge 1 -> 2 (3) and 2 -> 3 (4)
    graph.update(Update::Add { source: 1, destination: 2, weight: 3 });
    graph.update(Update::Add { source: 2, destination: 3, weight: 4 });
    // Now, path from 1->2->3 should yield 7.
    assert_eq!(graph.query(3), 7);

    // Remove edge 2 -> 3, path should not exist.
    graph.update(Update::Remove { source: 2, destination: 3 });
    assert_eq!(graph.query(3), -1);

    // Add edge 1 -> 3 (10)
    graph.update(Update::Add { source: 1, destination: 3, weight: 10 });
    assert_eq!(graph.query(3), 10);

    // Update edge 1 -> 3 to weight 2.
    graph.update(Update::Update { source: 1, destination: 3, weight: 2 });
    assert_eq!(graph.query(3), 2);
}

#[test]
fn test_no_path() {
    // Graph: Only edge 2 -> 3 (5) but source is city 1.
    let initial_edges = vec![(2, 3, 5)];
    let source_cities = vec![1];
    let mut graph = Graph::new(initial_edges, source_cities);

    // No path from source 1 to 3.
    assert_eq!(graph.query(3), -1);
}

#[test]
fn test_multiple_updates() {
    // Graph:
    // 1 -> 2 (1), 2 -> 3 (2), 3 -> 4 (3), 4 -> 5 (4)
    let initial_edges = vec![(1, 2, 1), (2, 3, 2), (3, 4, 3), (4, 5, 4)];
    let source_cities = vec![1];
    let mut graph = Graph::new(initial_edges, source_cities);

    // Initial shortest path to 5 should be 1+2+3+4 = 10.
    assert_eq!(graph.query(5), 10);

    // Update: Change edge 3 -> 4 to weight 1. New shortest to 5: 1+2+1+4 = 8.
    graph.update(Update::Update { source: 3, destination: 4, weight: 1 });
    assert_eq!(graph.query(5), 8);

    // Add new direct edge: 2 -> 5 (5). Now shortest path to 5 is min(1+5 = 6, 8, 10) = 6.
    graph.update(Update::Add { source: 2, destination: 5, weight: 5 });
    assert_eq!(graph.query(5), 6);

    // Remove edge 1 -> 2. With no outgoing edge from source 1, there should be no path.
    graph.update(Update::Remove { source: 1, destination: 2 });
    assert_eq!(graph.query(5), -1);
}

#[test]
fn test_dynamic_behavior() {
    // Graph with multiple sources and dynamic changes.
    // Graph: 
    // 1 -> 2 (3), 2 -> 4 (4), 3 -> 2 (2), 3 -> 4 (10), 4 -> 5 (2)
    let initial_edges = vec![(1, 2, 3), (2, 4, 4), (3, 2, 2), (3, 4, 10), (4, 5, 2)];
    let source_cities = vec![1, 3];
    let mut graph = Graph::new(initial_edges, source_cities);

    // From source 1, path to 5: 1->2->4->5 = 3+4+2 = 9.
    // From source 3, path to 5: 3->2->4->5 = 2+4+2 = 8 (or 3->4->5 = 10+2 = 12).
    // The expected shortest path is 8.
    assert_eq!(graph.query(5), 8);

    // Remove edge 2 -> 4.
    graph.update(Update::Remove { source: 2, destination: 4 });
    // Now, from source 1 there is no path to 5, and from source 3, path is 3->4->5 = 10+2 = 12.
    assert_eq!(graph.query(5), 12);

    // Add edge 1 -> 4 with weight 5.
    graph.update(Update::Add { source: 1, destination: 4, weight: 5 });
    // Now, from source 1, 1->4->5 = 5+2 = 7, which is the new shortest path.
    assert_eq!(graph.query(5), 7);
}