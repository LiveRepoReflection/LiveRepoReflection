use wormhole_path::shortest_path;

#[test]
fn test_same_planet() {
    // When the start and end planet are the same, the latency should be 0.
    let n = 1;
    let hub_counts = vec![3];
    let intra_planet_connections = vec![(0, 1), (1, 2)];
    let inter_planet_connections: Vec<(usize, usize, u64, u64)> = Vec::new();
    let gravitational_sensitivities = vec![5];
    let start_planet = 0;
    let end_planet = 0;
    assert_eq!(shortest_path(n, hub_counts, intra_planet_connections, inter_planet_connections, gravitational_sensitivities, start_planet, end_planet), Some(0));
}

#[test]
fn test_two_planets_single_connection() {
    // Two planets: Planet 0 has hubs 0 and 1; Planet 1 has hubs 2 and 3.
    // Intra-planet connections connect hubs within a planet.
    // There is a wormhole from hub 1 (planet 0) to hub 2 (planet 1) with latency 10 and bandwidth 100.
    // Planet 0 gravitational sensitivity = 0, Planet 1 gravitational sensitivity = 1.
    // Wormhole effective latency: 10 + 1*100 = 110.
    let n = 2;
    let hub_counts = vec![2, 2];
    let intra_planet_connections = vec![(0, 1), (2, 3)];
    let inter_planet_connections = vec![(1, 2, 10, 100)];
    let gravitational_sensitivities = vec![0, 1];
    let start_planet = 0;
    let end_planet = 1;
    assert_eq!(shortest_path(n, hub_counts, intra_planet_connections, inter_planet_connections, gravitational_sensitivities, start_planet, end_planet), Some(110));
}

#[test]
fn test_three_planets_multiple_connections() {
    // Three planets, each with a single hub:
    // Planet 0: hub 0, Planet 1: hub 1, Planet 2: hub 2.
    // Two potential routes:
    // Route 1: 0->1 and then 1->2.
    //    0->1: latency = 20 + (planet1 gravitational sensitivity 2 * 10) = 20 + 20 = 40.
    //    1->2: latency = 30 + (planet2 gravitational sensitivity 3 * 5) = 30 + 15 = 45.
    //    Total = 40 + 45 = 85.
    // Route 2: Direct from 0->2: latency = 50 + (planet2 gravitational sensitivity 3 * 20) = 50 + 60 = 110.
    let n = 3;
    let hub_counts = vec![1, 1, 1];
    let intra_planet_connections: Vec<(usize, usize)> = Vec::new();
    let inter_planet_connections = vec![
        (0, 1, 20, 10),
        (1, 2, 30, 5),
        (0, 2, 50, 20)
    ];
    let gravitational_sensitivities = vec![1, 2, 3];
    let start_planet = 0;
    let end_planet = 2;
    assert_eq!(shortest_path(n, hub_counts, intra_planet_connections, inter_planet_connections, gravitational_sensitivities, start_planet, end_planet), Some(85));
}

#[test]
fn test_no_path_available() {
    // Two planets with multiple hubs but no inter-planet wormholes.
    // Decision: When there is no wormhole connecting the two planets,
    // the result should be None.
    let n = 2;
    let hub_counts = vec![3, 2];
    let intra_planet_connections = vec![(0, 1), (1, 2), (3, 4)];
    let inter_planet_connections: Vec<(usize, usize, u64, u64)> = Vec::new();
    let gravitational_sensitivities = vec![2, 3];
    let start_planet = 0;
    let end_planet = 1;
    assert_eq!(shortest_path(n, hub_counts, intra_planet_connections, inter_planet_connections, gravitational_sensitivities, start_planet, end_planet), None);
}

#[test]
fn test_complex_network() {
    // Complex network with multiple hubs per planet and several inter-planet wormholes.
    // Planet layout:
    // Planet 0: hubs 0, 1, 2
    // Planet 1: hubs 3, 4
    // Planet 2: hubs 5, 6, 7
    // Intra-planet connections ensure all hubs on the same planet are reachable with 0 latency.
    let n = 3;
    let hub_counts = vec![3, 2, 3];
    let intra_planet_connections = vec![
        (0, 1), (1, 2),    // Planet 0
        (3, 4),            // Planet 1
        (5, 6), (6, 7)     // Planet 2
    ];
    // Inter-planet wormholes:
    // Wormhole from hub 2 (Planet 0) -> hub 3 (Planet 1): latency = 15, bandwidth = 10.
    //    Effective latency = 15 + (planet1 gravitational sensitivity * 10).
    // Wormhole from hub 4 (Planet 1) -> hub 5 (Planet 2): latency = 20, bandwidth = 5.
    //    Effective latency = 20 + (planet2 gravitational sensitivity * 5).
    // Wormhole from hub 0 (Planet 0) -> hub 7 (Planet 2): latency = 40, bandwidth = 2.
    //    Effective latency = 40 + (planet2 gravitational sensitivity * 2).
    let inter_planet_connections = vec![
        (2, 3, 15, 10),
        (4, 5, 20, 5),
        (0, 7, 40, 2)
    ];
    // Gravitational sensitivities for each planet.
    let gravitational_sensitivities = vec![1, 2, 3];
    let start_planet = 0;
    let end_planet = 2;
    // Compute expected route:
    // Route 1: 0 -> (intra transit on Planet 0) -> hub 2 -> wormhole to hub 3 on Planet 1.
    //    Latency = 15 + (planet1 grav 2 * 10) = 15 + 20 = 35.
    // Then intra transit on Planet 1: hub 3 to hub 4 = 0.
    // Then wormhole from hub 4 to hub 5 on Planet 2.
    //    Latency = 20 + (planet2 grav 3 * 5) = 20 + 15 = 35.
    // Total = 35 + 35 = 70.
    // Route 2: Direct wormhole from hub 0 to hub 7 on Planet 2.
    //    Latency = 40 + (planet2 grav 3 * 2) = 40 + 6 = 46.
    // However, intra-planet connectivity on Planet 0 may require hub 0 is already available.
    // The best route is the direct one with total latency = 46.
    assert_eq!(shortest_path(n, hub_counts, intra_planet_connections, inter_planet_connections, gravitational_sensitivities, start_planet, end_planet), Some(46));
}