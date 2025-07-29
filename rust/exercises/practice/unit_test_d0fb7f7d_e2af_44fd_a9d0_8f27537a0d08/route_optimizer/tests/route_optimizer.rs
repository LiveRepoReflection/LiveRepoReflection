use std::u64;

use route_optimizer::find_min_travel_time;

#[test]
fn test_basic_routing_no_updates() {
    // Graph:
    // 0 -> 1: base_travel_time = 10, congestion factor = 1.0
    // 1 -> 2: base_travel_time = 15, congestion factor = 1.0
    let start_node = 0;
    let end_node = 2;
    let departure_time = 0;
    let graph = vec![
        vec![(1, 10, 1.0)],
        vec![(2, 15, 1.0)],
        vec![],
    ];
    let congestion_updates: Vec<(usize, usize, u64, f64)> = Vec::new();
    let restricted_access: Vec<(usize, Vec<(u64, u64)>)> = Vec::new();

    // Expect travel time: 10 + 15 = 25.
    let result =
        find_min_travel_time(start_node, end_node, departure_time, &graph, &congestion_updates, &restricted_access);
    assert_eq!(result, Some(25));
}

#[test]
fn test_congestion_and_restriction() {
    // Sample scenario from problem description:
    // Graph:
    // 0 -> 1: base_travel_time = 10, congestion factor = 1.0
    // 1 -> 2: base_travel_time = 15, congestion factor = 1.0
    //
    // Congestion update: For edge (0, 1) at time 5, congestion factor becomes 2.0.
    // Restricted access: Node 2 is restricted from time 20 to 30.
    let start_node = 0;
    let end_node = 2;
    let departure_time = 0;
    let graph = vec![
        vec![(1, 10, 1.0)],
        vec![(2, 15, 1.0)],
        vec![],
    ];
    let congestion_updates = vec![
        (0, 1, 5, 2.0),
    ];
    let restricted_access = vec![
        (2, vec![(20, 30)]),
    ];

    // Expected result is calculated in the problem description as 30.
    let result =
        find_min_travel_time(start_node, end_node, departure_time, &graph, &congestion_updates, &restricted_access);
    assert_eq!(result, Some(30));
}

#[test]
fn test_alternative_paths() {
    // Graph with two alternative routes:
    // Path 1: 0 -> 1 -> 3 with travel times 10 and 10 => Total = 20.
    // Path 2: 0 -> 2 -> 3 with travel times 5 and 20 => Total = 25.
    let start_node = 0;
    let end_node = 3;
    let departure_time = 0;
    let graph = vec![
        vec![(1, 10, 1.0), (2, 5, 1.0)],
        vec![(3, 10, 1.0)],
        vec![(3, 20, 1.0)],
        vec![],
    ];
    let congestion_updates: Vec<(usize, usize, u64, f64)> = Vec::new();
    let restricted_access: Vec<(usize, Vec<(u64, u64)>)> = Vec::new();

    let result =
        find_min_travel_time(start_node, end_node, departure_time, &graph, &congestion_updates, &restricted_access);
    assert_eq!(result, Some(20));
}

#[test]
fn test_unreachable_destination() {
    // Graph:
    // 0 -> 1 -> 2
    // Intersection 1 is permanently restricted, so destination is unreachable.
    let start_node = 0;
    let end_node = 2;
    let departure_time = 0;
    let graph = vec![
        vec![(1, 10, 1.0)],
        vec![(2, 10, 1.0)],
        vec![],
    ];
    let congestion_updates: Vec<(usize, usize, u64, f64)> = Vec::new();
    let restricted_access = vec![
        (1, vec![(0, u64::MAX)]),
    ];

    let result =
        find_min_travel_time(start_node, end_node, departure_time, &graph, &congestion_updates, &restricted_access);
    assert_eq!(result, None);
}

#[test]
fn test_complex_congestion_updates() {
    // Complex scenario with multiple congestion updates:
    // Graph:
    // 0 -> 1: base_travel_time = 20, initial factor = 1.0.
    // Updates on edge (0, 1): at time 10, factor becomes 2.0; at time 25, factor reverts to 1.0.
    // 1 -> 2: base_travel_time = 30, factor = 1.0.
    //
    // Simulation reasoning:
    // For 0->1:
    //   - From departure at t=0 until update at t=10, factor = 1.0.
    //   - Remaining portion of travel uses factor 2.0 until t=25 if needed.
    //   - Expected arrival at 1 is calculated as t = 60.
    // Then from 1->2: travel time = 30.
    // Total expected travel time: 60.
    let start_node = 0;
    let end_node = 2;
    let departure_time = 0;
    let graph = vec![
        vec![(1, 20, 1.0)],
        vec![(2, 30, 1.0)],
        vec![],
    ];
    let congestion_updates = vec![
        (0, 1, 10, 2.0),
        (0, 1, 25, 1.0),
    ];
    let restricted_access: Vec<(usize, Vec<(u64, u64)>)> = Vec::new();

    let result =
        find_min_travel_time(start_node, end_node, departure_time, &graph, &congestion_updates, &restricted_access);
    assert_eq!(result, Some(60));
}