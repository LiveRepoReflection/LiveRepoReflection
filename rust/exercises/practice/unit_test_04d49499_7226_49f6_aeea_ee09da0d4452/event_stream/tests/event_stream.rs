use std::collections::HashMap;
use event_stream::{Event, Processor};

#[test]
fn test_event_ingestion() {
    let mut processor = Processor::new();
    let mut attributes = HashMap::new();
    attributes.insert("product_id".to_string(), "123".to_string());
    let event = Event::new("product_viewed", attributes);
    processor.ingest_event(event);
    let output = processor.process_events();
    // Expect the event to be routed to the default route.
    assert!(output.contains_key("default"));
    let routed_events = output.get("default").unwrap();
    assert_eq!(routed_events.len(), 1);
    assert_eq!(routed_events[0].event_type, "product_viewed");
}

#[test]
fn test_event_routing_custom_rule() {
    let mut processor = Processor::new();
    // Add a custom routing rule: route "order_placed" events with total > 1000 to "fraud_detection"
    processor.add_routing_rule(|event: &Event| {
        if event.event_type == "order_placed" {
            if let Some(total_str) = event.attributes.get("total") {
                if let Ok(total) = total_str.parse::<f64>() {
                    if total > 1000.0 {
                        return Some("fraud_detection".to_string());
                    }
                }
            }
        }
        None
    });
    let mut attributes = HashMap::new();
    attributes.insert("total".to_string(), "1500".to_string());
    let event = Event::new("order_placed", attributes);
    processor.ingest_event(event);
    let output = processor.process_events();
    // Expect the event to be in the "fraud_detection" route.
    assert!(output.contains_key("fraud_detection"));
    let routed = output.get("fraud_detection").unwrap();
    assert_eq!(routed.len(), 1);
    assert_eq!(routed[0].event_type, "order_placed");
}

#[test]
fn test_stateful_transformation_moving_average() {
    let mut processor = Processor::new();
    // Enable a stateful transformation that computes a moving average for "order_placed" events.
    processor.enable_stateful_transformation(|state: &mut HashMap<String, Vec<f64>>, event: &Event| -> Option<(String, f64)> {
        if event.event_type == "order_placed" {
            if let (Some(category), Some(value_str)) = (event.attributes.get("category"), event.attributes.get("value")) {
                if let Ok(value) = value_str.parse::<f64>() {
                    let entry = state.entry(category.clone()).or_insert_with(Vec::new);
                    entry.push(value);
                    // Calculate moving average over the last 3 events for this category.
                    let window_size = 3;
                    let sum: f64 = entry.iter().rev().take(window_size).sum();
                    let count = entry.iter().rev().take(window_size).count() as f64;
                    return Some(("moving_average".to_string(), sum / count));
                }
            }
        }
        None
    });
    // Ingest 3 events for the same category.
    let test_data = vec![
        ("electronics", "100"),
        ("electronics", "150"),
        ("electronics", "50"),
    ];
    for (category, value) in test_data.iter() {
        let mut attributes = HashMap::new();
        attributes.insert("category".to_string(), category.to_string());
        attributes.insert("value".to_string(), value.to_string());
        let event = Event::new("order_placed", attributes);
        processor.ingest_event(event);
    }
    let averages = processor.compute_stateful_transformation();
    // The expected moving average is based on the last three events.
    if let Some(avg) = averages.get("moving_average") {
        let expected = (100.0 + 150.0 + 50.0) / 3.0;
        assert!((avg - expected).abs() < 1e-6);
    } else {
        panic!("Moving average not computed");
    }
}

#[test]
fn test_ordering_guarantee() {
    let mut processor = Processor::new();
    let session_id = "session123".to_string();
    // Ingest 5 events with ascending timestamp values.
    for i in 1..=5 {
        let mut attributes = HashMap::new();
        attributes.insert("session_id".to_string(), session_id.clone());
        attributes.insert("timestamp".to_string(), (1000 + i).to_string());
        attributes.insert("order".to_string(), i.to_string());
        let event = Event::new("activity", attributes);
        processor.ingest_event(event);
    }
    let output = processor.process_events();
    // Expect the events in the default route to maintain their order.
    let routed = output.get("default").unwrap();
    let orders: Vec<u32> = routed.iter()
        .map(|e| e.attributes.get("order").unwrap().parse::<u32>().unwrap())
        .collect();
    let expected_orders: Vec<u32> = (1..=5).collect();
    assert_eq!(orders, expected_orders);
}

#[test]
fn test_fault_tolerance_event_recovery() {
    let mut processor = Processor::new();
    let mut attributes = HashMap::new();
    attributes.insert("info".to_string(), "initial".to_string());
    let event = Event::new("heartbeat", attributes);
    processor.ingest_event(event);
    // Simulate a node failure and recover pending events.
    let pending_events = processor.simulate_failure_and_recover();
    let output = processor.process_pending(pending_events);
    // Verify that the recovered event is processed correctly.
    assert!(output.contains_key("default"));
    let routed = output.get("default").unwrap();
    assert_eq!(routed.len(), 1);
    assert_eq!(routed[0].event_type, "heartbeat");
}

#[test]
fn test_scalability_under_load() {
    let mut processor = Processor::new();
    let num_events = 10000;
    for i in 0..num_events {
        let mut attributes = HashMap::new();
        attributes.insert("product_id".to_string(), (i % 100).to_string());
        let event = Event::new("product_viewed", attributes);
        processor.ingest_event(event);
    }
    let output = processor.process_events();
    let total: usize = output.values().map(|v| v.len()).sum();
    assert_eq!(total, num_events);
}