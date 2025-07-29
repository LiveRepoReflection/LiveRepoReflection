use dynamic_routing::{Graph, Event, find_path};

fn compute_cost(graph: &Graph, path: &Vec<String>, penalty: u32, events: &Vec<Event>) -> u32 {
    let mut total = 0;
    use std::collections::HashMap;
    let mut blocked = HashMap::new();
    for event in events {
        blocked.insert(event.node.clone(), event.is_blocked);
    }
    for i in 0..path.len() - 1 {
        let cost = graph.get_edge_cost(&path[i], &path[i + 1]);
        let mut add_penalty = 0;
        if *blocked.get(&path[i]).unwrap_or(&false) {
            add_penalty += penalty;
        }
        if *blocked.get(&path[i + 1]).unwrap_or(&false) {
            add_penalty += penalty;
        }
        total += cost + add_penalty;
    }
    total
}

#[test]
fn test_static_graph() {
    // Graph with nodes: A, B, C.
    // Edges: A->B (1), B->C (1).
    // No dynamic obstacle events.
    let mut graph = Graph::new();
    graph.add_edge("A", "B", 1);
    graph.add_edge("B", "C", 1);
    let events: Vec<Event> = Vec::new();
    let penalty = 100; // Penalty is irrelevant in this test.
    let path = find_path(&mut graph, "A".to_string(), "C".to_string(), events.clone(), penalty);
    assert_eq!(path, vec!["A".to_string(), "B".to_string(), "C".to_string()]);
}

#[test]
fn test_obstacle_reroute() {
    // Graph: A, B, C, D.
    // Edges: A->B (1), A->C (2), B->D (1), C->D (1).
    // Dynamic event: at time 5, node B becomes blocked.
    let mut graph = Graph::new();
    graph.add_edge("A", "B", 1);
    graph.add_edge("A", "C", 2);
    graph.add_edge("B", "D", 1);
    graph.add_edge("C", "D", 1);
    let events = vec![Event {
        time: 5,
        node: "B".to_string(),
        is_blocked: true,
    }];
    let penalty = 100;
    // With a high penalty on blocked node B, the expected best route is A -> C -> D.
    let path = find_path(&mut graph, "A".to_string(), "D".to_string(), events.clone(), penalty);
    assert_eq!(path, vec!["A".to_string(), "C".to_string(), "D".to_string()]);
}

#[test]
fn test_cycle_graph() {
    // Graph with cycle:
    // Nodes: A, B, C, D.
    // Edges: A->B (2), B->C (2), C->A (1), B->D (3), C->D (1).
    // No obstacles.
    let mut graph = Graph::new();
    graph.add_edge("A", "B", 2);
    graph.add_edge("B", "C", 2);
    graph.add_edge("C", "A", 1);
    graph.add_edge("B", "D", 3);
    graph.add_edge("C", "D", 1);
    let events: Vec<Event> = Vec::new();
    let penalty = 50;
    let path = find_path(&mut graph, "A".to_string(), "D".to_string(), events.clone(), penalty);
    let cost = compute_cost(&graph, &path, penalty, &events);
    // The expected optimal cost is 5 (either via A->B->C->D or A->B->D).
    assert_eq!(cost, 5);
}

#[test]
fn test_dynamic_obstacle_toggle() {
    // Graph: A, B, C, D.
    // Edges: A->B (2), A->C (4), B->D (3), C->D (1).
    // Dynamic events: at time 3, node D becomes blocked; at time 6, node D becomes unblocked.
    let mut graph = Graph::new();
    graph.add_edge("A", "B", 2);
    graph.add_edge("A", "C", 4);
    graph.add_edge("B", "D", 3);
    graph.add_edge("C", "D", 1);
    let events = vec![
        Event {
            time: 3,
            node: "D".to_string(),
            is_blocked: true,
        },
        Event {
            time: 6,
            node: "D".to_string(),
            is_blocked: false,
        },
    ];
    let penalty = 100;
    // After all events have been processed, node D is unblocked.
    // Expected optimal route should be A -> B -> D.
    let path = find_path(&mut graph, "A".to_string(), "D".to_string(), events.clone(), penalty);
    assert_eq!(path, vec!["A".to_string(), "B".to_string(), "D".to_string()]);
}