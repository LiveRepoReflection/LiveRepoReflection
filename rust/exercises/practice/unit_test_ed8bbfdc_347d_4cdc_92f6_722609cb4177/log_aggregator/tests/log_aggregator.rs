use std::collections::HashSet;
use std::sync::{Arc, Mutex};
use std::thread;
use log_aggregator::{aggregate_logs, LogEntry};

#[test]
fn test_empty_input() {
    let logs: Vec<LogEntry> = vec![];
    let current_time = 1_000_000;
    let result = aggregate_logs(logs, current_time);
    assert!(result.is_empty());
}

#[test]
fn test_ordering() {
    // Create logs in unsorted order.
    let current_time = 10_000;
    let logs = vec![
        LogEntry {
            timestamp: 2000,
            service_id: 1,
            transaction_id: 100,
            log_message: "message1".to_string(),
        },
        LogEntry {
            timestamp: 1000,
            service_id: 2,
            transaction_id: 101,
            log_message: "message2".to_string(),
        },
        LogEntry {
            timestamp: 3000,
            service_id: 1,
            transaction_id: 102,
            log_message: "message3".to_string(),
        },
    ];
    let result = aggregate_logs(logs, current_time);
    assert_eq!(result.len(), 3);
    // Ensure the logs are in ascending order by timestamp.
    for i in 1..result.len() {
        assert!(result[i - 1].timestamp <= result[i].timestamp);
    }
}

#[test]
fn test_duplicates() {
    // Create logs with duplicate transaction_id entries.
    let current_time = 10_000;
    let logs = vec![
        LogEntry {
            timestamp: 1500,
            service_id: 1,
            transaction_id: 200,
            log_message: "first entry".to_string(),
        },
        LogEntry {
            timestamp: 1000,
            service_id: 2,
            transaction_id: 200,
            log_message: "duplicate entry".to_string(),
        },
        LogEntry {
            timestamp: 2000,
            service_id: 3,
            transaction_id: 201,
            log_message: "unique entry".to_string(),
        },
    ];
    let result = aggregate_logs(logs, current_time);
    let mut seen = HashSet::new();
    for log in &result {
        assert!(seen.insert(log.transaction_id));
    }
    // Only two unique transaction ids should be present.
    assert_eq!(seen.len(), 2);
}

#[test]
fn test_bounded_delay() {
    // Assuming logs arriving more than 1 hour (3600000 ms) late are discarded.
    let current_time = 5_000_000;
    // Valid log: timestamp is exactly on the boundary (current_time - 3600000).
    let valid_timestamp = current_time - 3600000;
    // Invalid log: timestamp is more than 1 hour older than current_time.
    let invalid_timestamp = current_time - 3600001;
    let logs = vec![
        LogEntry {
            timestamp: valid_timestamp,
            service_id: 1,
            transaction_id: 300,
            log_message: "valid log".to_string(),
        },
        LogEntry {
            timestamp: invalid_timestamp,
            service_id: 2,
            transaction_id: 301,
            log_message: "stale log".to_string(),
        },
    ];
    let result = aggregate_logs(logs, current_time);
    // Only the valid log should remain.
    assert_eq!(result.len(), 1);
    assert_eq!(result[0].transaction_id, 300);
}

#[test]
fn test_concurrent_entries() {
    // Simulate concurrent generation of log entries.
    let base_current_time = 10_000;
    let thread_count = 10;
    let logs_per_thread = 100;
    let logs_arc = Arc::new(Mutex::new(Vec::new()));
    let mut handles = Vec::new();

    for i in 0..thread_count {
        let logs_arc_clone = Arc::clone(&logs_arc);
        let handle = thread::spawn(move || {
            let mut local_logs = Vec::new();
            for j in 0..logs_per_thread {
                let ts = base_current_time + (i as u64 * 10) + j as u64;
                local_logs.push(LogEntry {
                    timestamp: ts,
                    service_id: i as u32,
                    transaction_id: (i * 1000 + j) as u64,
                    log_message: format!("Log from thread {} entry {}", i, j),
                });
            }
            let mut guard = logs_arc_clone.lock().unwrap();
            guard.extend(local_logs);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let concurrent_logs = {
        let guard = logs_arc.lock().unwrap();
        guard.clone()
    };

    // Update current time to allow all logs to be within allowed delay.
    let updated_current_time = base_current_time + 5000;
    let result = aggregate_logs(concurrent_logs, updated_current_time);
    // Expecting thread_count * logs_per_thread unique logs.
    assert_eq!(result.len(), thread_count * logs_per_thread);
    // Check that the result is sorted by timestamp.
    for i in 1..result.len() {
        assert!(result[i - 1].timestamp <= result[i].timestamp);
    }
}