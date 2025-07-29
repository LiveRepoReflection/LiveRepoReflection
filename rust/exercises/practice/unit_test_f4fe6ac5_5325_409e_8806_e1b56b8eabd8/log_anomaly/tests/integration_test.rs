use std::collections::HashMap;
use std::error::Error;

use log_anomaly::{parse_log_entry, worker_aggregate, coordinator_detect, LogEntry, AnomalyReport};

#[test]
fn test_parse_valid_log_entry() {
    let log_str = "1678886400,server123,ERROR,Disk space is critically low";
    let entry: LogEntry = parse_log_entry(log_str).expect("Failed to parse valid log entry");
    assert_eq!(entry.timestamp, 1678886400);
    assert_eq!(entry.server_id, "server123");
    assert_eq!(entry.log_level, "ERROR");
    assert_eq!(entry.message, "Disk space is critically low");
}

#[test]
fn test_parse_invalid_log_entry() {
    // An entry without enough separators should fail parsing.
    let invalid_log = "invalid log entry";
    let result = parse_log_entry(invalid_log);
    assert!(result.is_err(), "Expected error when parsing an invalid log entry");
}

#[test]
fn test_worker_aggregate_counts() -> Result<(), Box<dyn Error>> {
    // Simulate a series of log entries collected by a worker node.
    let logs = vec![
        "100,serverA,INFO,Operation completed",
        "110,serverA,INFO,Operation completed",
        "115,serverA,ERROR,Operation failed",
        "125,serverA,INFO,Operation completed",
        "130,serverB,WARN,Resource usage high",
        "135,serverB,WARN,Resource usage high"
    ];
    let log_entries: Vec<String> = logs.into_iter().map(String::from).collect();

    // Consider a time_window of 50 seconds and an aggregation_interval of 50 seconds.
    // The worker_aggregate function is expected to compute the average count for each (server_id, log_level) pair.
    let aggregated: HashMap<(String, String), f64> = worker_aggregate(&log_entries, 50, 50);

    let key_a_info = (String::from("serverA"), String::from("INFO"));
    let key_a_error = (String::from("serverA"), String::from("ERROR"));
    let key_b_warn = (String::from("serverB"), String::from("WARN"));

    // Expected counts based on provided logs:
    // serverA, INFO: 3 entries; serverA, ERROR: 1 entry; serverB, WARN: 2 entries.
    assert_eq!(aggregated.get(&key_a_info).copied().unwrap_or(0.0), 3.0);
    assert_eq!(aggregated.get(&key_a_error).copied().unwrap_or(0.0), 1.0);
    assert_eq!(aggregated.get(&key_b_warn).copied().unwrap_or(0.0), 2.0);
    Ok(())
}

#[test]
fn test_coordinator_detect_anomalies() {
    // Simulate aggregated statistics from two worker nodes.
    let mut worker0_stats: HashMap<(String, String), f64> = HashMap::new();
    let mut worker1_stats: HashMap<(String, String), f64> = HashMap::new();

    // Both workers have statistics for the same (server_id, log_level) pairs.
    // Worker 0 always reports higher counts.
    worker0_stats.insert((String::from("serverA"), String::from("INFO")), 10.0);
    worker0_stats.insert((String::from("serverB"), String::from("ERROR")), 5.0);

    // Worker 1 reports a significantly lower count for serverA INFO, which should trigger an anomaly.
    worker1_stats.insert((String::from("serverA"), String::from("INFO")), 2.0);
    worker1_stats.insert((String::from("serverB"), String::from("ERROR")), 5.0);

    let workers_stats = vec![worker0_stats, worker1_stats];

    // Set a threshold multiplier such that a deviation beyond this multiplier is considered anomalous.
    let anomaly_threshold = 2.0;
    let anomalies: Vec<AnomalyReport> = coordinator_detect(&workers_stats, anomaly_threshold);

    // For serverA INFO:
    // Global average = (10.0 + 2.0) / 2 = 6.0. Worker 1's count, 2.0, deviates from the average by a factor > 2.0.
    // For serverB ERROR, both workers report 5.0. No anomaly is expected.
    assert_eq!(anomalies.len(), 1, "Expected a single anomaly due to deviation in serverA INFO");
    let anomaly = &anomalies[0];
    assert_eq!(anomaly.server_id, "serverA");
    assert_eq!(anomaly.log_level, "INFO");
    // Assuming worker_id corresponds to the index in the workers_stats vector.
    assert_eq!(anomaly.worker_id, 1);
    assert!((anomaly.current_count - 2.0).abs() < f64::EPSILON);
    assert!((anomaly.global_avg - 6.0).abs() < f64::EPSILON);
}

#[test]
fn test_fault_tolerance_no_worker_data() {
    // Simulate a scenario where the coordinator receives no data from any worker nodes.
    let workers_stats: Vec<HashMap<(String, String), f64>> = Vec::new();
    let anomaly_threshold = 2.0;
    let anomalies: Vec<AnomalyReport> = coordinator_detect(&workers_stats, anomaly_threshold);
    // With no worker data, no anomalies should be reported.
    assert!(anomalies.is_empty(), "No anomalies should be detected when there is no data");
}

#[test]
fn test_real_time_processing_simulation() -> Result<(), Box<dyn Error>> {
    // Simulate a real-time processing scenario with a stream of log entries.
    let logs = vec![
        "1000,serverX,INFO,Start process",
        "1005,serverX,INFO,Process step 1",
        "1010,serverX,INFO,Process step 2",
        "1020,serverY,ERROR,Process failed",
        "1025,serverY,ERROR,Retrying process",
        "1030,serverX,INFO,Process complete"
    ];
    let log_entries: Vec<String> = logs.into_iter().map(String::from).collect();

    // Assume a time window of 40 seconds and an aggregation interval of 30 seconds.
    let aggregated: HashMap<(String, String), f64> = worker_aggregate(&log_entries, 40, 30);

    // Expected aggregated counts:
    // For serverX INFO: 4 entries (from all log entries with serverX INFO).
    // For serverY ERROR: 2 entries.
    let key_x_info = (String::from("serverX"), String::from("INFO"));
    let key_y_error = (String::from("serverY"), String::from("ERROR"));

    assert_eq!(aggregated.get(&key_x_info).copied().unwrap_or(0.0), 4.0);
    assert_eq!(aggregated.get(&key_y_error).copied().unwrap_or(0.0), 2.0);
    Ok(())
}