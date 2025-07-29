use std::time::Instant;
use traffic_sync::{TrafficNetwork, optimize_traffic_lights};
use traffic_sync::tests_helper::check_duration_within_range;

#[test]
fn test_output_length_and_ranges() {
    let network = TrafficNetwork {
        n: 3,
        m: 3,
        edges: vec![
            (0, 1, 10),
            (1, 2, 15),
            (0, 2, 30),
        ],
        duration_ranges: vec![
            (10, 20, 5, 10, 15, 25),
            (12, 22, 6, 11, 16, 26),
            (8, 18, 4, 9, 14, 24),
        ],
        k: 2,
        source_destination_pairs: vec![
            (0, 2),
            (1, 2),
        ],
        time_limit: 5,
    };

    let result = optimize_traffic_lights(&network);
    // Check that the output length is exactly 3 * n
    assert_eq!(result.len(), network.n * 3, "Output length must be 3 * n");
    // Check that each duration is within the specified ranges.
    assert!(check_duration_within_range(&result, &network.duration_ranges), "One or more durations are out of the valid range");
}

#[test]
fn test_multiple_input_scenarios() {
    let test_cases = vec![
        TrafficNetwork {
            n: 2,
            m: 1,
            edges: vec![(0, 1, 20)],
            duration_ranges: vec![
                (5, 10, 3, 8, 7, 12),
                (6, 11, 4, 9, 8, 13)
            ],
            k: 1,
            source_destination_pairs: vec![(0, 1)],
            time_limit: 3,
        },
        TrafficNetwork {
            n: 4,
            m: 5,
            edges: vec![
                (0, 1, 10),
                (1, 2, 15),
                (2, 3, 20),
                (0, 2, 25),
                (1, 3, 30)
            ],
            duration_ranges: vec![
                (10, 15, 5, 10, 15, 20),
                (12, 18, 6, 12, 16, 22),
                (8, 14, 4, 9, 14, 19),
                (11, 17, 7, 13, 17, 23),
            ],
            k: 2,
            source_destination_pairs: vec![(0, 3), (1, 3)],
            time_limit: 5,
        },
    ];

    for network in test_cases {
        let result = optimize_traffic_lights(&network);
        // Validate the output length.
        assert_eq!(result.len(), network.n * 3, "Output length must be 3 * n for n = {}", network.n);
        // Validate durations are within the specified ranges.
        assert!(check_duration_within_range(&result, &network.duration_ranges), "Durations out of range for network with n = {}", network.n);
    }
}

#[test]
fn test_edge_case_minimal_input() {
    // Minimal graph: one intersection, no edges, and no source-destination pairs.
    let network = TrafficNetwork {
        n: 1,
        m: 0,
        edges: vec![],
        duration_ranges: vec![(1, 1, 1, 1, 1, 1)],
        k: 0,
        source_destination_pairs: vec![],
        time_limit: 1,
    };

    let result = optimize_traffic_lights(&network);
    // The output should have exactly 3 numbers.
    assert_eq!(result.len(), 3, "Output length must be 3 for a single intersection");
    let (min_red, max_red, min_yellow, max_yellow, min_green, max_green) = network.duration_ranges[0];
    assert!(result[0] >= min_red && result[0] <= max_red, "Red duration is out of valid range");
    assert!(result[1] >= min_yellow && result[1] <= max_yellow, "Yellow duration is out of valid range");
    assert!(result[2] >= min_green && result[2] <= max_green, "Green duration is out of valid range");
}

#[test]
fn test_time_limit_adherence() {
    let network = TrafficNetwork {
        n: 5,
        m: 7,
        edges: vec![
            (0, 1, 12),
            (1, 2, 15),
            (2, 3, 18),
            (3, 4, 20),
            (0, 2, 30),
            (1, 3, 25),
            (2, 4, 22),
        ],
        duration_ranges: vec![
            (10, 20, 5, 10, 15, 25),
            (10, 20, 5, 10, 15, 25),
            (10, 20, 5, 10, 15, 25),
            (10, 20, 5, 10, 15, 25),
            (10, 20, 5, 10, 15, 25),
        ],
        k: 2,
        source_destination_pairs: vec![(0, 4), (1, 4)],
        time_limit: 2, // Very short time limit.
    };

    let start = Instant::now();
    let result = optimize_traffic_lights(&network);
    let elapsed = start.elapsed().as_secs();
    // Ensure the algorithm finishes within the given time limit.
    assert!(elapsed <= network.time_limit as u64, "Algorithm exceeded the time limit");
    // Validate the output.
    assert_eq!(result.len(), network.n * 3, "Output length must be 3 * n");
    assert!(check_duration_within_range(&result, &network.duration_ranges), "Durations are out of range");
}