use log_aggregate::{DistributedLogSystem, LogEntry};
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

#[test]
fn test_basic_log_ingestion_and_query() {
    let system = DistributedLogSystem::new(5);
    
    // Add logs from different machines
    system.add_log(0, 1000, "First log from machine 0".to_string());
    system.add_log(1, 1001, "Log from machine 1".to_string());
    system.add_log(0, 1002, "Second log from machine 0".to_string());

    let logs = system.query(999, 1003);
    assert_eq!(logs.len(), 3);
    assert_eq!(logs[0], "First log from machine 0");
    assert_eq!(logs[1], "Log from machine 1");
    assert_eq!(logs[2], "Second log from machine 0");
}

#[test]
fn test_out_of_order_logs() {
    let system = DistributedLogSystem::new(3);
    
    system.add_log(0, 2000, "Later log".to_string());
    system.add_log(0, 1000, "Earlier log".to_string());
    system.add_log(1, 1500, "Middle log".to_string());

    let logs = system.query(0, 3000);
    assert_eq!(logs.len(), 3);
    assert_eq!(logs[0], "Earlier log");
    assert_eq!(logs[1], "Later log");
    assert_eq!(logs[2], "Middle log");
}

#[test]
fn test_concurrent_log_ingestion() {
    let system = DistributedLogSystem::new(10);
    let system_arc = std::sync::Arc::new(system);
    let mut handles = vec![];

    for i in 0..10 {
        let system_clone = system_arc.clone();
        handles.push(thread::spawn(move || {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            system_clone.add_log(
                i,
                timestamp,
                format!("Concurrent log from machine {}", i),
            );
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    let logs = system_arc.query(0, now);
    assert_eq!(logs.len(), 10);
}

#[test]
fn test_empty_time_window() {
    let system = DistributedLogSystem::new(2);
    
    system.add_log(0, 1000, "Test log".to_string());
    let logs = system.query(2000, 3000);
    assert!(logs.is_empty());
}

#[test]
fn test_machine_bounds() {
    let system = DistributedLogSystem::new(3);
    
    // This should not panic
    system.add_log(2, 1000, "Valid machine".to_string());
    
    // These should be ignored or handled gracefully
    system.add_log(3, 1000, "Invalid machine".to_string());
    system.add_log(999, 1000, "Invalid machine".to_string());
    
    let logs = system.query(0, 2000);
    assert_eq!(logs.len(), 1);
    assert_eq!(logs[0], "Valid machine");
}

#[test]
fn test_duplicate_timestamps() {
    let system = DistributedLogSystem::new(2);
    
    system.add_log(0, 1000, "First log".to_string());
    system.add_log(1, 1000, "Second log".to_string());
    system.add_log(0, 1000, "Third log".to_string());

    let logs = system.query(1000, 1000);
    assert_eq!(logs.len(), 3);
}

#[test]
fn test_large_time_window() {
    let system = DistributedLogSystem::new(1);
    
    system.add_log(0, 1, "Ancient log".to_string());
    system.add_log(0, u64::MAX - 1, "Future log".to_string());

    let logs = system.query(0, u64::MAX);
    assert_eq!(logs.len(), 2);
}

#[test]
fn test_maximum_message_length() {
    let system = DistributedLogSystem::new(1);
    let long_message = "a".repeat(256);
    let too_long_message = "a".repeat(257);
    
    // Should accept
    system.add_log(0, 1000, long_message);
    
    // Should reject or truncate
    system.add_log(0, 1001, too_long_message);
    
    let logs = system.query(0, 2000);
    assert!(logs[0].len() <= 256);
}

#[test]
fn test_lexicographical_ordering() {
    let system = DistributedLogSystem::new(1);
    
    system.add_log(0, 1000, "zebra".to_string());
    system.add_log(0, 1001, "alpha".to_string());
    system.add_log(0, 1002, "beta".to_string());

    let logs = system.query(0, 2000);
    assert_eq!(logs[0], "alpha");
    assert_eq!(logs[1], "beta");
    assert_eq!(logs[2], "zebra");
}