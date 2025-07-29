use std::collections::HashMap;
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use distributed_logs::{LogAggregator, LogAnalyzer, LogMessage};

fn current_time_millis() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_millis() as i64
}

#[test]
fn test_aggregator_filters_valid_messages() {
    // Create a channel for the aggregator to send batches of log messages to the analyzer.
    let (tx, rx) = mpsc::channel();

    // Create an aggregator with required field "level", time window of 2000 ms,
    // a batch size of 2, and maximum delay of 100 ms.
    let mut aggregator = LogAggregator::new(vec!["level".to_string()], 2000, 2, 100, tx);

    let now = current_time_millis();

    // Valid message: has "level" field and timestamp within window.
    let msg1 = format!(
        r#"{{"timestamp": {}, "message": "Test1", "level": "INFO"}}"#,
        now
    );
    // Invalid message: missing the required "level" field.
    let msg2 = format!(r#"{{"timestamp": {}, "message": "Test2"}}"#, now);
    // Invalid message: timestamp outside the allowed window.
    let invalid_time = now - 5000;
    let msg3 = format!(
        r#"{{"timestamp": {}, "message": "Test3", "level": "DEBUG"}}"#,
        invalid_time
    );
    // Malformed JSON message.
    let msg4 = r#"{"timestamp": "not_a_number", "message": "Bad", "level": "WARN""#;

    aggregator.process_message(&msg1);
    aggregator.process_message(&msg2);
    aggregator.process_message(&msg3);
    aggregator.process_message(&msg4);

    // Allow some time for the batch to be sent.
    thread::sleep(Duration::from_millis(150));
    aggregator.flush();

    let mut received_msgs = Vec::new();
    while let Ok(batch) = rx.try_recv() {
        received_msgs.extend(batch);
    }

    // Only msg1 should have been forwarded.
    assert_eq!(received_msgs.len(), 1);
    let forwarded = &received_msgs[0];
    assert_eq!(forwarded.message, "Test1");
    assert_eq!(forwarded.fields.get("level").unwrap(), "INFO");
}

#[test]
fn test_analyzer_count_query() {
    // Create a new LogAnalyzer.
    let mut analyzer = LogAnalyzer::new();
    let now = current_time_millis();

    // Create log messages manually.
    let messages = vec![
        LogMessage {
            timestamp: now - 1000,
            message: "First message".to_string(),
            fields: {
                let mut map = HashMap::new();
                map.insert("level".to_string(), "INFO".to_string());
                map
            },
        },
        LogMessage {
            timestamp: now,
            message: "Second message".to_string(),
            fields: {
                let mut map = HashMap::new();
                map.insert("level".to_string(), "INFO".to_string());
                map
            },
        },
        LogMessage {
            timestamp: now + 1000,
            message: "Third message".to_string(),
            fields: {
                let mut map = HashMap::new();
                map.insert("level".to_string(), "ERROR".to_string());
                map
            },
        },
    ];

    analyzer.ingest(messages);

    let count_info = analyzer.count("level", "INFO", now - 1500, now + 500);
    assert_eq!(count_info, 2);

    let count_error = analyzer.count("level", "ERROR", now - 1500, now + 1500);
    assert_eq!(count_error, 1);
}

#[test]
fn test_aggregator_batching_behavior() {
    // Create a channel for batching.
    let (tx, rx) = mpsc::channel();
    // Set up the aggregator with required field "type", time window of 3000 ms,
    // a batch size of 3, and maximum delay of 200 ms.
    let mut aggregator = LogAggregator::new(vec!["type".to_string()], 3000, 3, 200, tx);
    let now = current_time_millis();

    // Create three valid messages.
    let messages: Vec<String> = (0..3)
        .map(|i| format!(r#"{{"timestamp": {}, "message": "Msg{}", "type": "A"}}"#, now, i))
        .collect();

    for msg in messages {
        aggregator.process_message(&msg);
    }

    // The batch should be flushed automatically when the batch size is reached.
    let batch = rx
        .recv_timeout(Duration::from_millis(300))
        .expect("Did not receive a batch in time");
    assert_eq!(batch.len(), 3);
}

#[test]
fn test_concurrent_processing() {
    // Create a channel for communication.
    let (tx, rx) = mpsc::channel();
    // Set up the aggregator with required field "key", time window of 2000 ms,
    // a batch size of 5, and maximum delay of 100 ms.
    let aggregator = Arc::new(Mutex::new(LogAggregator::new(
        vec!["key".to_string()],
        2000,
        5,
        100,
        tx,
    )));
    let now = current_time_millis();

    // Generate 20 valid messages concurrently.
    let messages: Vec<String> = (0..20)
        .map(|i| format!(r#"{{"timestamp": {}, "message": "Concurrent{}", "key": "VAL"}}"#, now, i))
        .collect();

    let mut handles = Vec::new();
    for msg in messages {
        let aggregator_clone = Arc::clone(&aggregator);
        handles.push(thread::spawn(move || {
            aggregator_clone.lock().unwrap().process_message(&msg);
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
    // Allow time for potential batching.
    thread::sleep(Duration::from_millis(150));
    aggregator.lock().unwrap().flush();

    let mut total_msgs = 0;
    while let Ok(batch) = rx.try_recv() {
        total_msgs += batch.len();
    }
    assert_eq!(total_msgs, 20);
}