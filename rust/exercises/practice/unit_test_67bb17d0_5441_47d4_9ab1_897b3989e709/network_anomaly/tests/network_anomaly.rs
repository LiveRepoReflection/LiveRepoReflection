use network_anomaly::{ConnectionRecord, detect_anomalies};

fn new_record(
    timestamp: u64,
    source_ip: &str,
    destination_ip: &str,
    source_port: u16,
    destination_port: u16,
    protocol: &str,
    packet_size: u32,
) -> ConnectionRecord {
    ConnectionRecord {
        timestamp,
        source_ip: source_ip.to_string(),
        destination_ip: destination_ip.to_string(),
        source_port,
        destination_port,
        protocol: protocol.to_string(),
        packet_size,
    }
}

#[test]
fn test_no_detection_for_baseline_only() {
    let records = vec![
        new_record(1, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1000),
        new_record(2, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1100),
        new_record(3, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 900),
    ];
    // Since there are only baseline records, no anomaly detection is performed.
    let anomalies = detect_anomalies(records, 3, 2.0);
    assert_eq!(anomalies.len(), 0);
}

#[test]
fn test_detect_normal_and_anomaly() {
    // Baseline records for combination ("192.168.0.1", "10.0.0.1", "TCP")
    let records = vec![
        new_record(1, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1000),
        new_record(2, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1100),
        new_record(3, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 900),
        // Post-baseline records:
        // Record 4: within expected variance (packet size 950)
        new_record(4, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 950),
        // Record 5: anomalous (packet size 1200, deviation > 2 * std dev)
        new_record(5, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1200),
    ];
    let anomalies = detect_anomalies(records, 3, 2.0);
    // For records post-baseline, we expect:
    // Record 4 -> false, Record 5 -> true.
    assert_eq!(anomalies, vec![false, true]);
}

#[test]
fn test_cold_start_new_combination() {
    // Baseline is built for one combination.
    let records = vec![
        new_record(1, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1000),
        new_record(2, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 1050),
        new_record(3, "192.168.0.1", "10.0.0.1", 80, 8080, "TCP", 995),
        // New combination ("192.168.0.1", "10.0.0.1", "UDP") not seen in baseline.
        new_record(4, "192.168.0.1", "10.0.0.1", 80, 8080, "UDP", 2000),
    ];
    let anomalies = detect_anomalies(records, 3, 2.0);
    // For cold start combinations, assume the record is not anomalous until enough data is collected.
    // Only one post-baseline record exists; it should be treated as normal.
    assert_eq!(anomalies.len(), 1);
    assert_eq!(anomalies[0], false);
}

#[test]
fn test_adaptive_update() {
    // This test checks the sliding window update over time.
    let records = vec![
        // Baseline for combination ("192.168.1.1", "10.0.0.2", "TCP")
        new_record(1, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 100),
        new_record(2, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 105),
        new_record(3, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 95),
        // Post-baseline records:
        // Record 4: Slight deviation, should be normal.
        new_record(4, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 102),
        // Sliding window now updates to records 2,3,4. Record 5 has packet_size that deviates significantly.
        new_record(5, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 90),
        // With updated window, record 6 falls back into normal range.
        new_record(6, "192.168.1.1", "10.0.0.2", 443, 80, "TCP", 101),
    ];
    let anomalies = detect_anomalies(records, 3, 2.0);
    // Expected anomalies vector for records 4, 5, and 6:
    // Record 4 -> false, Record 5 -> true, Record 6 -> false.
    assert_eq!(anomalies, vec![false, true, false]);
}

#[test]
fn test_zero_stddev() {
    // Test edge case where all baseline records have the same packet_size, leading to zero standard deviation.
    // For subsequent records, any deviation from the baseline should be flagged as anomalous.
    let records = vec![
        new_record(1, "10.0.0.1", "10.0.0.2", 1000, 2000, "TCP", 500),
        new_record(2, "10.0.0.1", "10.0.0.2", 1000, 2000, "TCP", 500),
        new_record(3, "10.0.0.1", "10.0.0.2", 1000, 2000, "TCP", 500),
        // Record 4: same as baseline, should be normal.
        new_record(4, "10.0.0.1", "10.0.0.2", 1000, 2000, "TCP", 500),
        // Record 5: slight deviation should be flagged as anomalous.
        new_record(5, "10.0.0.1", "10.0.0.2", 1000, 2000, "TCP", 501),
    ];
    let anomalies = detect_anomalies(records, 3, 2.0);
    // Expected: Record 4 -> false, Record 5 -> true.
    assert_eq!(anomalies, vec![false, true]);
}