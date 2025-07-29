use network_latency::optimize_network_latency;

#[test]
fn test_single_request_direct_path() {
    let servers = vec![
        (0, 40.7128, -74.0060, 2),  // New York
        (1, 34.0522, -118.2437, 5), // Los Angeles
        (2, 51.5074, 0.1278, 1),    // London
    ];
    let requests = vec![(0, 2, 10000)]; // NY to London
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}

#[test]
fn test_multiple_requests_with_congestion() {
    let servers = vec![
        (0, 40.7128, -74.0060, 0),  // New York
        (1, 34.0522, -118.2437, 0), // Los Angeles
        (2, 51.5074, 0.1278, 0),    // London
        (3, 35.6762, 139.6503, 0), // Tokyo
    ];
    let requests = vec![
        (0, 2, 50000), // NY to London
        (1, 3, 30000), // LA to Tokyo
        (2, 0, 20000), // London to NY
    ];
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}

#[test]
fn test_high_congestion_rerouting() {
    let servers = vec![
        (0, 40.7128, -74.0060, 9),  // New York (high congestion)
        (1, 34.0522, -118.2437, 1), // Los Angeles
        (2, 51.5074, 0.1278, 1),    // London
        (3, 48.8566, 2.3522, 0),    // Paris
    ];
    let requests = vec![
        (0, 2, 100000), // NY to London
        (1, 3, 50000),  // LA to Paris
    ];
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}

#[test]
fn test_max_congestion_handling() {
    let servers = vec![
        (0, 40.7128, -74.0060, 10), // New York (max congestion)
        (1, 34.0522, -118.2437, 10), // Los Angeles
        (2, 51.5074, 0.1278, 10),   // London
    ];
    let requests = vec![
        (0, 1, 5000),
        (1, 2, 5000),
        (2, 0, 5000),
    ];
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}

#[test]
fn test_small_data_transfer() {
    let servers = vec![
        (0, 40.7128, -74.0060, 0),
        (1, 34.0522, -118.2437, 0),
    ];
    let requests = vec![(0, 1, 1)]; // Minimal data transfer
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}

#[test]
fn test_large_network() {
    let servers = vec![
        (0, 40.7128, -74.0060, 0),  // New York
        (1, 34.0522, -118.2437, 0), // Los Angeles
        (2, 51.5074, 0.1278, 0),    // London
        (3, 48.8566, 2.3522, 0),    // Paris
        (4, 35.6762, 139.6503, 0),  // Tokyo
        (5, -33.8688, 151.2093, 0), // Sydney
        (6, 55.7558, 37.6173, 0),   // Moscow
        (7, 19.4326, -99.1332, 0),  // Mexico City
        (8, -23.5505, -46.6333, 0), // São Paulo
        (9, 28.6139, 77.2090, 0),   // New Delhi
    ];
    let requests = vec![
        (0, 9, 100000),
        (1, 5, 50000),
        (2, 7, 75000),
        (3, 4, 30000),
        (8, 6, 25000),
    ];
    let result = optimize_network_latency(&servers, &requests);
    assert!(result > 0);
}