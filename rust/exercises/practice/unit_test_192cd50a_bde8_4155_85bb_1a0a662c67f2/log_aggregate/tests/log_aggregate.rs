use std::sync::Arc;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use log_aggregate::*;

const WINDOW_SECONDS: u64 = 60;

#[test]
fn test_basic_aggregation() {
    let aggregator = LogAggregator::new(WINDOW_SECONDS);
    
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    
    let entries = vec![
        LogEntry {
            timestamp: now,
            server_id: "server1".to_string(),
            log_level: LogLevel::INFO,
            message: "test message".to_string(),
        }
    ];
    
    aggregator.process_batch(entries);
    
    assert_eq!(aggregator.query_count(LogLevel::INFO), 1);
    assert_eq!(aggregator.query_count(LogLevel::ERROR), 0);
}

#[test]
fn test_window_expiration() {
    let aggregator = LogAggregator::new(1); // 1 second window
    
    let old_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() - 2; // 2 seconds ago
        
    let entries = vec![
        LogEntry {
            timestamp: old_time,
            server_id: "server1".to_string(),
            log_level: LogLevel::INFO,
            message: "old message".to_string(),
        }
    ];
    
    aggregator.process_batch(entries);
    
    // After processing old entries, count should be 0 as they're outside window
    assert_eq!(aggregator.query_count(LogLevel::INFO), 0);
}

#[test]
fn test_concurrent_updates() {
    let aggregator = Arc::new(LogAggregator::new(WINDOW_SECONDS));
    let mut handles = vec![];
    
    for i in 0..10 {
        let agg_clone = Arc::clone(&aggregator);
        
        handles.push(thread::spawn(move || {
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
                
            let entries = vec![
                LogEntry {
                    timestamp: now,
                    server_id: format!("server{}", i),
                    log_level: LogLevel::WARN,
                    message: format!("message from thread {}", i),
                }
            ];
            
            agg_clone.process_batch(entries);
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    assert_eq!(aggregator.query_count(LogLevel::WARN), 10);
}

#[test]
fn test_out_of_order_entries() {
    let aggregator = LogAggregator::new(WINDOW_SECONDS);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
        
    let entries = vec![
        LogEntry {
            timestamp: now - 1,
            server_id: "server1".to_string(),
            log_level: LogLevel::ERROR,
            message: "later message".to_string(),
        },
        LogEntry {
            timestamp: now - 2,
            server_id: "server1".to_string(),
            log_level: LogLevel::ERROR,
            message: "earlier message".to_string(),
        }
    ];
    
    aggregator.process_batch(entries);
    assert_eq!(aggregator.query_count(LogLevel::ERROR), 2);
}

#[test]
fn test_multiple_log_levels() {
    let aggregator = LogAggregator::new(WINDOW_SECONDS);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
        
    let entries = vec![
        LogEntry {
            timestamp: now,
            server_id: "server1".to_string(),
            log_level: LogLevel::INFO,
            message: "info message".to_string(),
        },
        LogEntry {
            timestamp: now,
            server_id: "server1".to_string(),
            log_level: LogLevel::WARN,
            message: "warn message".to_string(),
        },
        LogEntry {
            timestamp: now,
            server_id: "server1".to_string(),
            log_level: LogLevel::ERROR,
            message: "error message".to_string(),
        }
    ];
    
    aggregator.process_batch(entries);
    
    assert_eq!(aggregator.query_count(LogLevel::INFO), 1);
    assert_eq!(aggregator.query_count(LogLevel::WARN), 1);
    assert_eq!(aggregator.query_count(LogLevel::ERROR), 1);
}

#[test]
fn test_high_volume() {
    let aggregator = LogAggregator::new(WINDOW_SECONDS);
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
        
    let mut entries = Vec::with_capacity(10000);
    
    for i in 0..10000 {
        entries.push(LogEntry {
            timestamp: now,
            server_id: format!("server{}", i % 100),
            log_level: LogLevel::INFO,
            message: format!("message {}", i),
        });
    }
    
    aggregator.process_batch(entries);
    assert_eq!(aggregator.query_count(LogLevel::INFO), 10000);
}

#[test]
fn test_concurrent_queries() {
    let aggregator = Arc::new(LogAggregator::new(WINDOW_SECONDS));
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
        
    let entries = vec![
        LogEntry {
            timestamp: now,
            server_id: "server1".to_string(),
            log_level: LogLevel::INFO,
            message: "test message".to_string(),
        }
    ];
    
    aggregator.process_batch(entries);
    
    let mut handles = vec![];
    
    for _ in 0..10 {
        let agg_clone = Arc::clone(&aggregator);
        handles.push(thread::spawn(move || {
            assert_eq!(agg_clone.query_count(LogLevel::INFO), 1);
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_stress_concurrent_updates_and_queries() {
    let aggregator = Arc::new(LogAggregator::new(WINDOW_SECONDS));
    let mut handles = vec![];
    
    // Spawn update threads
    for _ in 0..5 {
        let agg_clone = Arc::clone(&aggregator);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                    
                let entries = vec![
                    LogEntry {
                        timestamp: now,
                        server_id: "server1".to_string(),
                        log_level: LogLevel::INFO,
                        message: "test message".to_string(),
                    }
                ];
                
                agg_clone.process_batch(entries);
                thread::sleep(Duration::from_micros(1));
            }
        }));
    }
    
    // Spawn query threads
    for _ in 0..5 {
        let agg_clone = Arc::clone(&aggregator);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                let _ = agg_clone.query_count(LogLevel::INFO);
                thread::sleep(Duration::from_micros(1));
            }
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    assert!(aggregator.query_count(LogLevel::INFO) > 0);
}