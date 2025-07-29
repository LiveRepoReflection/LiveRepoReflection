use std::f64;

use network_optimizer::optimize_network;

const EPSILON: f64 = 1e-6;

#[test]
fn test_no_route() {
    let n = 2;
    // No edge exists so route from 0 to 1 is impossible.
    let edge_list: Vec<(usize, usize, u32)> = vec![];
    let requests: Vec<(usize, usize, u32)> = vec![(0, 1, 10)];
    let bandwidth = 10; // bytes per millisecond

    let result = optimize_network(n, edge_list, requests, bandwidth);
    assert!(result.is_infinite(), "Expected INFINITY when there is no route, got {}", result);
}

#[test]
fn test_single_request() {
    let n = 2;
    // Single edge from 0 to 1 with latency 10ms.
    let edge_list: Vec<(usize, usize, u32)> = vec![(0, 1, 10)];
    // One request of a 5-byte message.
    let requests: Vec<(usize, usize, u32)> = vec![(0, 1, 5)];
    let bandwidth = 10; // bytes per millisecond

    // Expected total time = path latency (10ms) + transmission time (5/10 = 0.5ms)
    let expected = 10.5;
    let result = optimize_network(n, edge_list, requests, bandwidth);
    assert!(
        (result - expected).abs() < EPSILON,
        "Expected average latency {}, got {}",
        expected,
        result
    );
}

#[test]
fn test_parallel_requests() {
    let n = 3;
    // Build a simple chain: 0 -> 1 -> 2 with latencies 5ms and 10ms respectively.
    let edge_list: Vec<(usize, usize, u32)> = vec![(0, 1, 5), (1, 2, 10)];
    // Two concurrent requests from 0 to 2, each of size 10 bytes.
    let requests: Vec<(usize, usize, u32)> = vec![(0, 2, 10), (0, 2, 10)];
    let bandwidth = 10; // bytes per millisecond

    // For each request, the path latency is 5 + 10 = 15ms.
    // When processed concurrently, the total size is 20 bytes,
    // so the transmission time required is 20/10 = 2ms for both.
    // Total time for each request: 15 + 2 = 17ms.
    // Average latency = 17ms.
    let expected = 17.0;
    let result = optimize_network(n, edge_list, requests, bandwidth);
    assert!(
        (result - expected).abs() < EPSILON,
        "Expected average latency {}, got {}",
        expected,
        result
    );
}

#[test]
fn test_multiple_requests_different_paths() {
    let n = 4;
    // Two potential paths from 0 to 3:
    // Path A: 0 -> 1 (latency 4), 1 -> 3 (latency 6) -> total 10ms.
    // Path B: 0 -> 2 (latency 3), 2 -> 3 (latency 8) -> total 11ms.
    // Optimal is Path A.
    let edge_list: Vec<(usize, usize, u32)> = vec![(0, 1, 4), (1, 3, 6), (0, 2, 3), (2, 3, 8)];
    // Two requests from 0 to 3 with different message sizes.
    let requests: Vec<(usize, usize, u32)> = vec![(0, 3, 10), (0, 3, 20)];
    let bandwidth = 10; // bytes per millisecond

    // Both requests take the optimal Path A with total path latency 10ms.
    // Combined, they require transmitting 30 bytes concurrently,
    // which takes 30/10 = 3ms.
    // Total time for each request: 10 + 3 = 13ms.
    // Average latency = 13ms.
    let expected = 13.0;
    let result = optimize_network(n, edge_list, requests, bandwidth);
    assert!(
        (result - expected).abs() < EPSILON,
        "Expected average latency {}, got {}",
        expected,
        result
    );
}