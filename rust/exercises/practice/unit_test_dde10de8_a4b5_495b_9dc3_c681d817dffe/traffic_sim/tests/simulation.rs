use std::collections::HashMap;
use traffic_sim::{simulate, CityGraph, Vehicle};

#[test]
fn test_single_vehicle_reaches_destination() {
    // Create a simple city graph with 3 intersections: 0, 1, 2.
    let mut graph = CityGraph::new();
    // Add roads: 0->1: capacity 2, speed_limit 60.0, length 60.0 (should take 1 second if effective speed is 60.0)
    //           1->2: capacity 2, speed_limit 60.0, length 60.0
    graph.add_road(0, 1, 2, 60.0, 60.0);
    graph.add_road(1, 2, 2, 60.0, 60.0);

    // Create a vehicle with route [0, 1, 2]
    let vehicle = Vehicle {
        id: 1,
        route: vec![0, 1, 2],
        max_speed: 80.0,
        entry_time: 0.0,
    };

    let vehicles = vec![vehicle];
    let result = simulate(&graph, vehicles, 10);

    // Expect travel time approximately 2 seconds.
    let travel_time = result.get(&1).unwrap();
    assert!((travel_time - 2.0).abs() < 1e-6, "Expected 2.0 seconds, got {}", travel_time);
}

#[test]
fn test_invalid_route_vehicle() {
    // Create a graph with one road: 0 -> 1.
    let mut graph = CityGraph::new();
    graph.add_road(0, 1, 1, 50.0, 50.0);

    // Vehicle route is invalid: 0 -> 2 where intersection 2 does not exist.
    let vehicle = Vehicle {
        id: 2,
        route: vec![0, 2],
        max_speed: 70.0,
        entry_time: 0.0,
    };

    let vehicles = vec![vehicle];
    let result = simulate(&graph, vehicles, 10);

    // Expect travel time to be INFINITY for an invalid route.
    let travel_time = result.get(&2).unwrap();
    assert!(travel_time.is_infinite(), "Expected INFINITY for invalid route, got {}", travel_time);
}

#[test]
fn test_vehicle_waiting_due_to_capacity() {
    // Create a graph with capacity constraint on the first road.
    let mut graph = CityGraph::new();
    // Road from 0->1 with capacity 1.
    graph.add_road(0, 1, 1, 60.0, 60.0);
    // Road from 1->2 with higher capacity.
    graph.add_road(1, 2, 2, 60.0, 60.0);

    // Create two vehicles with the same route: 0->1->2.
    let vehicle1 = Vehicle {
        id: 3,
        route: vec![0, 1, 2],
        max_speed: 80.0,
        entry_time: 0.0,
    };
    let vehicle2 = Vehicle {
        id: 4,
        route: vec![0, 1, 2],
        max_speed: 80.0,
        entry_time: 0.0,
    };

    let vehicles = vec![vehicle1, vehicle2];
    let result = simulate(&graph, vehicles, 20);

    // At least one vehicle should finish in roughly 2 seconds,
    // while the other may experience a delay.
    let time3 = result.get(&3).unwrap();
    let time4 = result.get(&4).unwrap();
    assert!(*time3 > 0.0 && *time4 > 0.0, "Travel times should be positive.");
    assert!(
        (*time3 - 2.0).abs() < 1e-6 || (*time4 - 2.0).abs() < 1e-6,
        "One vehicle should have travel time approximately 2.0 seconds; got {} and {}",
        time3,
        time4
    );
}

#[test]
fn test_multiple_vehicles_concurrent() {
    // Create a graph with 4 intersections: 0, 1, 2, 3.
    let mut graph = CityGraph::new();
    graph.add_road(0, 1, 5, 100.0, 100.0);
    graph.add_road(1, 2, 5, 80.0, 80.0);
    graph.add_road(2, 3, 5, 60.0, 60.0);
    graph.add_road(0, 2, 3, 70.0, 70.0); // alternative route

    // Create multiple vehicles with different routes and entry times.
    let vehicles = vec![
        Vehicle { id: 5, route: vec![0, 1, 2, 3], max_speed: 120.0, entry_time: 0.0 },
        Vehicle { id: 6, route: vec![0, 2, 3], max_speed: 90.0, entry_time: 1.0 },
        Vehicle { id: 7, route: vec![0, 1, 2, 3], max_speed: 100.0, entry_time: 2.0 },
    ];

    let result = simulate(&graph, vehicles, 50);

    // All vehicles should eventually complete their routes.
    for &vehicle_id in &[5, 6, 7] {
        let time = result.get(&vehicle_id).unwrap();
        assert!(!time.is_infinite(), "Vehicle {} did not reach its destination", vehicle_id);
    }
}

#[test]
fn test_max_steps_exceeded() {
    // Create a graph that forces delays, potentially exceeding max_steps.
    let mut graph = CityGraph::new();
    // Road from 0->1 with capacity 1 and long length causing delay.
    graph.add_road(0, 1, 1, 50.0, 500.0);
    graph.add_road(1, 2, 1, 50.0, 500.0);

    // Vehicle with route 0->1->2.
    let vehicle = Vehicle {
        id: 8,
        route: vec![0, 1, 2],
        max_speed: 70.0,
        entry_time: 0.0,
    };

    let vehicles = vec![vehicle];
    // Set max_steps lower than required for a complete traversal.
    let result = simulate(&graph, vehicles, 15);

    let time = result.get(&8).unwrap();
    // Since max_steps is insufficient, travel time should be INFINITY.
    assert!(time.is_infinite(), "Expected INFINITY when max_steps is exceeded, got {}", time);
}