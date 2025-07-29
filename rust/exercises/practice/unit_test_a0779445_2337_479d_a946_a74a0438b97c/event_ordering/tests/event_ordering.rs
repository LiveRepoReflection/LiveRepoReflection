#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use event_ordering::order_events;

    type Event = (String, String, u64, u64, String);

    #[test]
    fn test_empty_input() {
        let events: Vec<Event> = vec![];
        let result = order_events(events);
        let expected: HashMap<String, Vec<Event>> = HashMap::new();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_single_transaction_order_by_timestamp() {
        let events = vec![
            ("txn1".to_string(), "svcA".to_string(), 2, 200, "event2".to_string()),
            ("txn1".to_string(), "svcB".to_string(), 1, 100, "event1".to_string()),
            ("txn1".to_string(), "svcA".to_string(), 3, 300, "event3".to_string()),
        ];
        let result = order_events(events);
        let ordered = result.get("txn1").expect("txn1 should exist");
        let expected = vec![
            ("txn1".to_string(), "svcB".to_string(), 1, 100, "event1".to_string()),
            ("txn1".to_string(), "svcA".to_string(), 2, 200, "event2".to_string()),
            ("txn1".to_string(), "svcA".to_string(), 3, 300, "event3".to_string()),
        ];
        assert_eq!(ordered, &expected);
    }

    #[test]
    fn test_single_transaction_order_same_timestamp() {
        // Two events with same timestamp, different service_ids
        let events = vec![
            ("txn2".to_string(), "svcB".to_string(), 1, 500, "eventB1".to_string()),
            ("txn2".to_string(), "svcA".to_string(), 1, 500, "eventA1".to_string()),
        ];
        let result = order_events(events);
        let ordered = result.get("txn2").expect("txn2 should exist");
        let expected = vec![
            ("txn2".to_string(), "svcA".to_string(), 1, 500, "eventA1".to_string()),
            ("txn2".to_string(), "svcB".to_string(), 1, 500, "eventB1".to_string()),
        ];
        assert_eq!(ordered, &expected);
    }

    #[test]
    fn test_multiple_transactions() {
        let events = vec![
            ("txn1".to_string(), "svcA".to_string(), 2, 200, "txn1-event2".to_string()),
            ("txn2".to_string(), "svcA".to_string(), 1, 150, "txn2-event1".to_string()),
            ("txn1".to_string(), "svcB".to_string(), 1, 100, "txn1-event1".to_string()),
            ("txn2".to_string(), "svcB".to_string(), 1, 250, "txn2-event2".to_string()),
        ];
        let result = order_events(events);
        let expected_txn1 = vec![
            ("txn1".to_string(), "svcB".to_string(), 1, 100, "txn1-event1".to_string()),
            ("txn1".to_string(), "svcA".to_string(), 2, 200, "txn1-event2".to_string()),
        ];
        let expected_txn2 = vec![
            ("txn2".to_string(), "svcA".to_string(), 1, 150, "txn2-event1".to_string()),
            ("txn2".to_string(), "svcB".to_string(), 1, 250, "txn2-event2".to_string()),
        ];
        let txn1_events = result.get("txn1").expect("txn1 should exist");
        let txn2_events = result.get("txn2").expect("txn2 should exist");
        assert_eq!(txn1_events, &expected_txn1);
        assert_eq!(txn2_events, &expected_txn2);
    }

    #[test]
    fn test_events_order_within_same_service_id_sequential() {
        // Test ordering within the same service_id: events with sequential event_ids must be ordered by event_id.
        let events = vec![
            ("txn3".to_string(), "svcC".to_string(), 10, 1000, "event10".to_string()),
            ("txn3".to_string(), "svcC".to_string(), 9, 900, "event9".to_string()),
            ("txn3".to_string(), "svcC".to_string(), 11, 1100, "event11".to_string()),
        ];
        let result = order_events(events);
        let ordered = result.get("txn3").expect("txn3 should exist");
        let expected = vec![
            ("txn3".to_string(), "svcC".to_string(), 9, 900, "event9".to_string()),
            ("txn3".to_string(), "svcC".to_string(), 10, 1000, "event10".to_string()),
            ("txn3".to_string(), "svcC".to_string(), 11, 1100, "event11".to_string()),
        ];
        assert_eq!(ordered, &expected);
    }

    #[test]
    fn test_edge_same_timestamp_and_event_id() {
        // Test multiple events with the same timestamp but different service_ids,
        // ensuring that when timestamps are equal, sorting falls back to alphabetical order of service_id.
        let events = vec![
            ("txn4".to_string(), "svcA".to_string(), 5, 1000, "A-event5".to_string()),
            ("txn4".to_string(), "svcB".to_string(), 2, 1000, "B-event2".to_string()),
            ("txn4".to_string(), "svcA".to_string(), 6, 1000, "A-event6".to_string()),
            ("txn4".to_string(), "svcC".to_string(), 1, 1000, "C-event1".to_string()),
        ];
        let result = order_events(events);
        let ordered = result.get("txn4").expect("txn4 should exist");
        let expected = vec![
            ("txn4".to_string(), "svcA".to_string(), 5, 1000, "A-event5".to_string()),
            ("txn4".to_string(), "svcA".to_string(), 6, 1000, "A-event6".to_string()),
            ("txn4".to_string(), "svcB".to_string(), 2, 1000, "B-event2".to_string()),
            ("txn4".to_string(), "svcC".to_string(), 1, 1000, "C-event1".to_string()),
        ];
        assert_eq!(ordered, &expected);
    }

    #[test]
    fn test_complex_combination() {
        // In a complex scenario, transactions have many events from multiple services with out-of-order arrivals.
        // Ordering must consider both timestamp precedence and within same service the event_id sequence.
        let events = vec![
            ("txn5".to_string(), "svcX".to_string(), 3, 3000, "X-event3".to_string()),
            ("txn5".to_string(), "svcY".to_string(), 1, 1000, "Y-event1".to_string()),
            ("txn5".to_string(), "svcX".to_string(), 2, 2000, "X-event2".to_string()),
            ("txn5".to_string(), "svcY".to_string(), 2, 2500, "Y-event2".to_string()),
            ("txn5".to_string(), "svcZ".to_string(), 1, 1500, "Z-event1".to_string()),
            ("txn5".to_string(), "svcX".to_string(), 4, 4000, "X-event4".to_string()),
            ("txn5".to_string(), "svcZ".to_string(), 2, 3500, "Z-event2".to_string()),
        ];
        let result = order_events(events);
        let ordered = result.get("txn5").expect("txn5 should exist");
        let expected = vec![
            ("txn5".to_string(), "svcY".to_string(), 1, 1000, "Y-event1".to_string()),
            ("txn5".to_string(), "svcZ".to_string(), 1, 1500, "Z-event1".to_string()),
            ("txn5".to_string(), "svcX".to_string(), 2, 2000, "X-event2".to_string()),
            ("txn5".to_string(), "svcY".to_string(), 2, 2500, "Y-event2".to_string()),
            ("txn5".to_string(), "svcX".to_string(), 3, 3000, "X-event3".to_string()),
            ("txn5".to_string(), "svcZ".to_string(), 2, 3500, "Z-event2".to_string()),
            ("txn5".to_string(), "svcX".to_string(), 4, 4000, "X-event4".to_string()),
        ];
        assert_eq!(ordered, &expected);
    }
}