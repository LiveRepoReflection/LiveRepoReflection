use std::collections::HashMap;
use traffic_flow::{simulate, RoadNetwork, Intersection, RoadSegment, SimulationResult, Phase};

fn build_simple_network() -> RoadNetwork {
    // Create a simple network with one intersection and three road segments.
    // Two road segments are incoming to the intersection (ids: 101, 102)
    // and one road segment is outgoing from the intersection (id: 201).
    let intersection = Intersection {
        id: 1,
        routing_probabilities: HashMap::from([(201, 1.0)]),
    };
    let road_segment1 = RoadSegment {
        id: 101,
        source: 0,
        destination: 1,
        capacity: 10,
        arrival_rate: 5,
    };
    let road_segment2 = RoadSegment {
        id: 102,
        source: 0,
        destination: 1,
        capacity: 8,
        arrival_rate: 3,
    };
    let road_segment3 = RoadSegment {
        id: 201,
        source: 1,
        destination: 2,
        capacity: 15,
        arrival_rate: 0,
    };
    RoadNetwork {
        intersections: vec![intersection],
        road_segments: vec![road_segment1, road_segment2, road_segment3],
    }
}

fn build_dynamic_network() -> RoadNetwork {
    // Create a network with two intersections and multiple road segments.
    let intersection1 = Intersection {
        id: 1,
        routing_probabilities: HashMap::from([(103, 0.6), (104, 0.4)]),
    };
    let intersection2 = Intersection {
        id: 2,
        routing_probabilities: HashMap::from([(201, 1.0)]),
    };
    let road_segment1 = RoadSegment {
        id: 101,
        source: 0,
        destination: 1,
        capacity: 10,
        arrival_rate: 7,
    };
    let road_segment2 = RoadSegment {
        id: 102,
        source: 0,
        destination: 1,
        capacity: 10,
        arrival_rate: 5,
    };
    let road_segment3 = RoadSegment {
        id: 103,
        source: 1,
        destination: 2,
        capacity: 12,
        arrival_rate: 0,
    };
    let road_segment4 = RoadSegment {
        id: 104,
        source: 1,
        destination: 2,
        capacity: 12,
        arrival_rate: 0,
    };
    let road_segment5 = RoadSegment {
        id: 201,
        source: 2,
        destination: 3,
        capacity: 15,
        arrival_rate: 0,
    };
    RoadNetwork {
        intersections: vec![intersection1, intersection2],
        road_segments: vec![road_segment1, road_segment2, road_segment3, road_segment4, road_segment5],
    }
}

#[test]
fn test_empty_network() {
    // Test simulation on an empty network.
    let network = RoadNetwork {
        intersections: vec![],
        road_segments: vec![],
    };
    let phase_duration = 5;
    let switching_time = 2;
    let simulation_time = 20;
    let reopt_interval = 10;

    let result: SimulationResult = simulate(&network, simulation_time, reopt_interval, phase_duration, switching_time);
    // Expect average waiting time to be zero and no phases configured.
    assert_eq!(result.average_waiting_time, 0.0);
    assert!(result.phases.is_empty());
}

#[test]
fn test_simple_network_simulation() {
    // Test simulation on a simple network.
    let network = build_simple_network();
    let phase_duration = 5;
    let switching_time = 2;
    let simulation_time = 50;
    let reopt_interval = 25;

    let result = simulate(&network, simulation_time, reopt_interval, phase_duration, switching_time);
    // Average waiting time should be non-negative.
    assert!(result.average_waiting_time >= 0.0);

    // For each intersection, ensure each incoming road segment gets a green light in at least one phase.
    for intersection in network.intersections.iter() {
        let phases_option = result.phases.get(&intersection.id);
        assert!(phases_option.is_some());
        let phases = phases_option.unwrap();
        let incoming: Vec<u32> = network.road_segments.iter()
            .filter(|rs| rs.destination == intersection.id)
            .map(|rs| rs.id)
            .collect();
        for road_id in incoming {
            let mut found = false;
            for phase in phases.iter() {
                if phase.green_road_segments.contains(&road_id) {
                    found = true;
                    break;
                }
            }
            assert!(found, "Road segment {} did not receive a green light at intersection {}", road_id, intersection.id);
        }
    }
}

#[test]
fn test_dynamic_arrival_rate_and_reoptimization() {
    // Test that dynamic changes in arrival rates result in re-optimization of traffic light phases.
    let mut network = build_dynamic_network();
    let phase_duration = 5;
    let switching_time = 2;
    let simulation_time = 100;
    let reopt_interval = 20;

    // Run simulation with initial arrival rates.
    let result_initial = simulate(&network, simulation_time, reopt_interval, phase_duration, switching_time);
    let avg_waiting_initial = result_initial.average_waiting_time;

    // Update arrival rates for incoming road segments.
    for rs in network.road_segments.iter_mut() {
        if rs.arrival_rate > 0 {
            rs.arrival_rate += 3;
        }
    }

    let result_updated = simulate(&network, simulation_time, reopt_interval, phase_duration, switching_time);
    let avg_waiting_updated = result_updated.average_waiting_time;

    // Expect the average waiting time to increase with higher arrival rates.
    assert!(avg_waiting_updated >= avg_waiting_initial);

    // Check phase validity for each intersection after dynamic update.
    for intersection in network.intersections.iter() {
        let phases_option = result_updated.phases.get(&intersection.id);
        assert!(phases_option.is_some());
        let phases = phases_option.unwrap();
        let incoming: Vec<u32> = network.road_segments.iter()
            .filter(|rs| rs.destination == intersection.id)
            .map(|rs| rs.id)
            .collect();
        for road_id in incoming {
            let mut found = false;
            for phase in phases.iter() {
                if phase.green_road_segments.contains(&road_id) {
                    found = true;
                    break;
                }
            }
            assert!(found, "Road segment {} did not receive a green light at intersection {} in dynamic simulation", road_id, intersection.id);
        }
    }
}

#[test]
fn test_deadlock_prevention() {
    // Test that the simulation configuration prevents deadlocks.
    let intersection1 = Intersection {
        id: 1,
        routing_probabilities: HashMap::from([(102, 0.5), (103, 0.5)]),
    };
    let intersection2 = Intersection {
        id: 2,
        routing_probabilities: HashMap::from([(201, 1.0)]),
    };
    let road_segment1 = RoadSegment {
        id: 101,
        source: 0,
        destination: 1,
        capacity: 8,
        arrival_rate: 6,
    };
    let road_segment2 = RoadSegment {
        id: 102,
        source: 0,
        destination: 1,
        capacity: 8,
        arrival_rate: 4,
    };
    let road_segment3 = RoadSegment {
        id: 103,
        source: 1,
        destination: 2,
        capacity: 10,
        arrival_rate: 0,
    };
    let road_segment4 = RoadSegment {
        id: 201,
        source: 2,
        destination: 3,
        capacity: 12,
        arrival_rate: 0,
    };
    let network = RoadNetwork {
        intersections: vec![intersection1, intersection2],
        road_segments: vec![road_segment1, road_segment2, road_segment3, road_segment4],
    };
    let phase_duration = 5;
    let switching_time = 2;
    let simulation_time = 60;
    let reopt_interval = 15;

    let result = simulate(&network, simulation_time, reopt_interval, phase_duration, switching_time);

    // Ensure that average waiting time is non-negative.
    assert!(result.average_waiting_time >= 0.0);

    // For each intersection, every incoming road segment should receive a green light in at least one phase.
    for intersection in network.intersections.iter() {
        let phases_option = result.phases.get(&intersection.id);
        assert!(phases_option.is_some());
        let phases = phases_option.unwrap();
        let incoming: Vec<u32> = network.road_segments.iter()
            .filter(|rs| rs.destination == intersection.id)
            .map(|rs| rs.id)
            .collect();
        for road_id in incoming {
            let mut found = false;
            for phase in phases.iter() {
                if phase.green_road_segments.contains(&road_id) {
                    found = true;
                    break;
                }
            }
            assert!(found, "Deadlock: Road segment {} did not receive a green light at intersection {}", road_id, intersection.id);
        }
    }
}