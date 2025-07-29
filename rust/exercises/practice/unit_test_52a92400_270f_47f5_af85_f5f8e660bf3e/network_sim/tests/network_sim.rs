use std::str::FromStr;
use std::f64;

use network_sim::simulate;

#[test]
fn test_basic_transmission() {
    let input = vec![
        "connect 0 1 100".to_string(),
        "connect 1 2 50".to_string(),
        "transmit 0 2 75".to_string(),
    ];
    let outputs = simulate(input.into_iter());
    // There should be only one output corresponding to the transmit command.
    assert_eq!(outputs.len(), 1);
    let parts: Vec<&str> = outputs[0].split_whitespace().collect();
    // Expected output format: "success <path> <transmission_time>"
    assert_eq!(parts[0], "success");
    // Expected path: nodes "0 1 2"
    assert_eq!(parts[1], "0");
    assert_eq!(parts[2], "1");
    assert_eq!(parts[3], "2");
    // The transmission time (last field) should be a positive number.
    let transmission_time = f64::from_str(parts[4]).expect("Unable to parse transmission time");
    assert!(transmission_time > 0.0);
}

#[test]
fn test_failure_after_removal() {
    let input = vec![
        "connect 0 1 100".to_string(),
        "connect 1 2 50".to_string(),
        "transmit 0 2 75".to_string(),
        "remove 1 2".to_string(),
        "transmit 0 2 75".to_string(),
    ];
    let outputs = simulate(input.into_iter());
    // Two transmit events should yield two outputs.
    assert_eq!(outputs.len(), 2);
    // The first transmit should be successful.
    let success_parts: Vec<&str> = outputs[0].split_whitespace().collect();
    assert_eq!(success_parts[0], "success");
    // The second transmit should fail because the required connection was removed.
    let failure_parts: Vec<&str> = outputs[1].split_whitespace().collect();
    assert_eq!(failure_parts[0], "failure");
    // Check that failure reason is "no path"
    let reason = failure_parts[1..].join(" ");
    assert_eq!(reason, "no path");
}

#[test]
fn test_packet_splitting() {
    // This test verifies that when packet size exceeds the bandwidth available in a single transmission,
    // the simulator splits the packet into chunks and still returns a successful transmission.
    let input = vec![
        "connect 0 1 30".to_string(),
        "connect 1 2 30".to_string(),
        "transmit 0 2 80".to_string(), // Packet size 80 > available bandwidth 30 on each edge.
    ];
    let outputs = simulate(input.into_iter());
    assert_eq!(outputs.len(), 1);
    let parts: Vec<&str> = outputs[0].split_whitespace().collect();
    assert_eq!(parts[0], "success");
    // Expected path: 0, 1, 2.
    assert_eq!(parts[1], "0");
    assert_eq!(parts[2], "1");
    assert_eq!(parts[3], "2");
    // Transmission time should be calculated from the split transmissions.
    let transmission_time = f64::from_str(parts[4]).expect("Unable to parse transmission time");
    assert!(transmission_time > 0.0);
}

#[test]
fn test_multiple_paths() {
    // Multiple potential paths exist between source and destination.
    // The simulator should choose the path with the highest effective bandwidth.
    // In this test, there are two paths:
    //   Path 1: 0 -> 1 -> 2 with bandwidths 40 and 40 (effective bandwidth = 40).
    //   Path 2: 0 -> 3 -> 2 with bandwidths 50 and 30 (effective bandwidth = 30).
    // Therefore, the correct path is 0-1-2.
    let input = vec![
        "connect 0 1 40".to_string(),
        "connect 1 2 40".to_string(),
        "connect 0 3 50".to_string(),
        "connect 3 2 30".to_string(),
        "transmit 0 2 60".to_string(),
    ];
    let outputs = simulate(input.into_iter());
    assert_eq!(outputs.len(), 1);
    let parts: Vec<&str> = outputs[0].split_whitespace().collect();
    assert_eq!(parts[0], "success");
    assert_eq!(parts[1], "0");
    assert_eq!(parts[2], "1");
    assert_eq!(parts[3], "2");
    let transmission_time = f64::from_str(parts[4]).expect("Unable to parse transmission time");
    assert!(transmission_time > 0.0);
}

#[test]
fn test_non_sequential_commands() {
    // This test simulates a real-world scenario where connections and transmissions occur in a non-sequential order.
    // After establishing a chain of connections, one is removed, causing a subsequent transmission to fail.
    let input = vec![
        "connect 2 4 100".to_string(),
        "connect 4 8 100".to_string(),
        "connect 8 16 100".to_string(),
        "connect 16 32 100".to_string(),
        "transmit 2 32 50".to_string(),
        "remove 8 16".to_string(),
        "transmit 2 32 50".to_string(),
    ];
    let outputs = simulate(input.into_iter());
    // Expecting two outputs: one success and one failure.
    assert_eq!(outputs.len(), 2);
    let success_parts: Vec<&str> = outputs[0].split_whitespace().collect();
    assert_eq!(success_parts[0], "success");
    // The expected path is "2 4 8 16 32". Check each node.
    assert_eq!(success_parts[1], "2");
    assert_eq!(success_parts[2], "4");
    assert_eq!(success_parts[3], "8");
    assert_eq!(success_parts[4], "16");
    assert_eq!(success_parts[5], "32");
    let transmission_time = f64::from_str(success_parts[6]).expect("Unable to parse transmission time");
    assert!(transmission_time > 0.0);
    
    let failure_parts: Vec<&str> = outputs[1].split_whitespace().collect();
    assert_eq!(failure_parts[0], "failure");
    let reason = failure_parts[1..].join(" ");
    assert_eq!(reason, "no path");
}