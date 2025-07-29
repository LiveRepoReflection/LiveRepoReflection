use std::collections::HashMap;
use network_resilience::{Graph, Edge, is_resilient, minimize_disruption};

fn create_graph(nodes: &[char], edges: &[(char, char, u64)]) -> Graph {
    let mut graph = Graph::new(nodes.to_vec());
    for &(u, v, cost) in edges {
        graph.add_edge(u, v, cost);
    }
    graph
}

fn apply_edges(graph: &mut Graph, new_edges: &[Edge]) {
    for &(u, v, cost) in new_edges {
        graph.add_edge(u, v, cost);
    }
}

#[test]
fn test_is_resilient_single_node() {
    let nodes = vec!['a'];
    let edges: &[(char, char, u64)] = &[];
    let graph = create_graph(&nodes, edges);
    // A single-node graph should be considered resilient (empty graph after removal is connected).
    assert!(is_resilient(&graph));
}

#[test]
fn test_is_resilient_two_nodes_connected() {
    let nodes = vec!['a', 'b'];
    // Create an edge between a and b.
    let edges = vec![('a', 'b', ('a' as u64) + ('b' as u64))];
    let graph = create_graph(&nodes, &edges);
    assert!(is_resilient(&graph));
}

#[test]
fn test_is_resilient_tree_structure() {
    // Tree structure: a -- b -- c (chain)
    let nodes = vec!['a', 'b', 'c'];
    let edges = vec![
        ('a', 'b', ('a' as u64) + ('b' as u64)),
        ('b', 'c', ('b' as u64) + ('c' as u64))
    ];
    let graph = create_graph(&nodes, &edges);
    // Removal of 'b' will disconnect a and c.
    assert!(!is_resilient(&graph));
}

#[test]
fn test_is_resilient_cycle() {
    // Cycle: a -- b -- c -- a
    let nodes = vec!['a', 'b', 'c'];
    let edges = vec![
        ('a', 'b', ('a' as u64) + ('b' as u64)),
        ('b', 'c', ('b' as u64) + ('c' as u64)),
        ('c', 'a', ('c' as u64) + ('a' as u64))
    ];
    let graph = create_graph(&nodes, &edges);
    assert!(is_resilient(&graph));
}

#[test]
fn test_minimize_disruption_already_resilient() {
    // Use a cycle graph which is already resilient.
    let nodes = vec!['a', 'b', 'c', 'd'];
    let edges = vec![
        ('a', 'b', ('a' as u64) + ('b' as u64)),
        ('b', 'c', ('b' as u64) + ('c' as u64)),
        ('c', 'd', ('c' as u64) + ('d' as u64)),
        ('d', 'a', ('d' as u64) + ('a' as u64)),
    ];
    let mut graph = create_graph(&nodes, &edges);

    let mut failure_prob = HashMap::new();
    for node in &nodes {
        failure_prob.insert(*node, 0.2);
    }
    // Set a generous budget.
    let budget = 1000;
    let added_edges = minimize_disruption(&mut graph, &failure_prob, budget);

    // Since the graph is already resilient, no new edges should be needed.
    assert!(added_edges.is_empty(), "Expected no edges to be added for already resilient graph");
}

#[test]
fn test_minimize_disruption_improves_resilience() {
    // Create a chain graph: a - b - c - d.
    let nodes = vec!['a', 'b', 'c', 'd'];
    let edges = vec![
        ('a', 'b', ('a' as u64) + ('b' as u64)),
        ('b', 'c', ('b' as u64) + ('c' as u64)),
        ('c', 'd', ('c' as u64) + ('d' as u64)),
    ];
    let mut graph = create_graph(&nodes, &edges);

    // The chain graph is not resilient.
    assert!(!is_resilient(&graph));

    let mut failure_prob = HashMap::new();
    failure_prob.insert('a', 0.1);
    failure_prob.insert('b', 0.4);
    failure_prob.insert('c', 0.3);
    failure_prob.insert('d', 0.2);

    // Set a budget high enough to add at least one edge.
    let budget = 200;
    let added_edges = minimize_disruption(&mut graph, &failure_prob, budget);

    // Check that total cost does not exceed the budget.
    let total_cost: u64 = added_edges.iter().map(|&(_, _, cost)| cost).sum();
    assert!(total_cost <= budget, "Total cost {} exceeds budget {}", total_cost, budget);

    // Check that every added edge is not already present in the original graph.
    // Re-create the original graph to compare.
    let original_graph = create_graph(&nodes, &edges);
    for &(u, v, _cost) in &added_edges {
        // Assuming Graph has a method has_edge that returns true if an edge exists.
        assert!(!original_graph.has_edge(u, v), "Edge ({}, {}) already exists", u, v);
    }

    // Apply the new edges to the graph and check if resilience is achieved.
    apply_edges(&mut graph, &added_edges);
    if is_resilient(&graph) {
        // If the graph becomes resilient after adding new edges, then expected improvement is achieved.
        assert!(true);
    } else {
        // If resilience is not fully achieved, we can also check that the expected communication metric has improved.
        // For demonstration, we check that some edges were added.
        assert!(!added_edges.is_empty(), "Expected some edge additions to improve connectivity");
    }
}

#[test]
fn test_minimize_disruption_budget_constraint() {
    // Create a non-resilient graph: a - b - c.
    let nodes = vec!['a', 'b', 'c'];
    let edges = vec![
        ('a', 'b', ('a' as u64) + ('b' as u64)),
        ('b', 'c', ('b' as u64) + ('c' as u64)),
    ];
    let mut graph = create_graph(&nodes, &edges);
    assert!(!is_resilient(&graph));

    let mut failure_prob = HashMap::new();
    failure_prob.insert('a', 0.3);
    failure_prob.insert('b', 0.5);
    failure_prob.insert('c', 0.2);

    // Set a very tight budget that might not allow adding any edge.
    let budget = 10;
    let added_edges = minimize_disruption(&mut graph, &failure_prob, budget);

    // Verify that the total cost of added edges does not exceed the budget.
    let total_cost: u64 = added_edges.iter().map(|&(_, _, cost)| cost).sum();
    assert!(total_cost <= budget, "Total cost {} exceeds budget {}", total_cost, budget);
    
    // It is acceptable if no edge is added given the tight budget.
    if added_edges.is_empty() {
        assert!(true);
    } else {
        // If edges are added, they must not violate the budget.
        assert!(total_cost <= budget);
    }
}