use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use event_ledger::*;

// Helper to get current timestamp in milliseconds.
fn current_time_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_millis() as u64
}

// Create a sample event.
fn create_event(
    timestamp: u64,
    institution_id: &str,
    account_id: &str,
    event_type: EventType,
    amount: i64,
    transfer_id: Option<&str>,
) -> Event {
    Event {
        timestamp,
        institution_id: institution_id.to_string(),
        account_id: account_id.to_string(),
        event_type,
        amount,
        transfer_id: transfer_id.map(|s| s.to_string()),
    }
}

#[test]
fn test_single_event_ingestion() {
    // Clear the store to ensure isolated test.
    clear_store();

    let ts = current_time_ms();
    let event = create_event(ts, "bank_a", "acct_1", EventType::Deposit, 1000, None);

    let res = ingest_event(event.clone());
    assert!(res.is_ok(), "Failed to ingest event");

    // Query all events.
    let result = query_events(None, None, None, None, 0, 10).expect("Query failed");
    assert_eq!(result.len(), 1);
    assert_eq!(result[0], event);
}

#[test]
fn test_event_ordering_within_account() {
    clear_store();

    let account_id = "acct_order";
    let institution_id = "bank_order";

    // Create events out-of-order by timestamp.
    let event1 = create_event(3000, institution_id, account_id, EventType::Withdrawal, 500, None);
    let event2 = create_event(1000, institution_id, account_id, EventType::Deposit, 1500, None);
    let event3 = create_event(2000, institution_id, account_id, EventType::TransferIn, 700, Some("tx_1"));

    // Ingest events in non-chronological order.
    assert!(ingest_event(event1.clone()).is_ok());
    assert!(ingest_event(event2.clone()).is_ok());
    assert!(ingest_event(event3.clone()).is_ok());

    // Query events filtered by institution and account.
    let events = query_events(Some(institution_id), Some(account_id), None, None, 0, 10)
        .expect("Query failed");
    assert_eq!(events.len(), 3);

    // Verify that events are ordered by timestamp ascending.
    assert!(events[0].timestamp <= events[1].timestamp);
    assert!(events[1].timestamp <= events[2].timestamp);
    assert_eq!(events[0], event2);
    assert_eq!(events[1], event3);
    assert_eq!(events[2], event1);
}

#[test]
fn test_query_filters() {
    clear_store();

    let base_ts = current_time_ms();
    // Ingest events for two institutions and different accounts.
    let e1 = create_event(base_ts + 100, "bank_a", "acct_1", EventType::Deposit, 2000, None);
    let e2 = create_event(base_ts + 200, "bank_a", "acct_2", EventType::Withdrawal, 500, None);
    let e3 = create_event(base_ts + 300, "bank_b", "acct_1", EventType::TransferOut, 700, Some("tx_A"));
    let e4 = create_event(base_ts + 400, "bank_b", "acct_3", EventType::Deposit, 3000, None);

    for event in &[e1.clone(), e2.clone(), e3.clone(), e4.clone()] {
        assert!(ingest_event(event.clone()).is_ok());
    }

    // Filter by institution_id "bank_a"
    let result_a = query_events(Some("bank_a"), None, None, None, 0, 10).expect("Query failed");
    assert_eq!(result_a.len(), 2);
    assert!(result_a.contains(&e1));
    assert!(result_a.contains(&e2));

    // Filter by account_id "acct_1"
    let result_b = query_events(None, Some("acct_1"), None, None, 0, 10).expect("Query failed");
    assert_eq!(result_b.len(), 2);
    assert!(result_b.contains(&e1));
    assert!(result_b.contains(&e3));

    // Filter by time range.
    let start_time = base_ts + 250;
    let end_time = base_ts + 450;
    let result_time =
        query_events(None, None, Some(start_time), Some(end_time), 0, 10).expect("Query failed");
    assert_eq!(result_time.len(), 2);
    assert!(result_time.contains(&e3));
    assert!(result_time.contains(&e4));
}

#[test]
fn test_pagination() {
    clear_store();

    let institution_id = "bank_paginate";
    let account_id = "acct_paginate";
    let base_ts = current_time_ms();

    // Ingest 10 events.
    let mut events = Vec::new();
    for i in 0..10 {
        let event = create_event(
            base_ts + i * 100,
            institution_id,
            account_id,
            EventType::Deposit,
            100 * (i as i64 + 1),
            None,
        );
        events.push(event.clone());
        assert!(ingest_event(event).is_ok());
    }

    // Query events with page_size = 3.
    let mut all_events = Vec::new();
    let mut page = 0;
    loop {
        let page_events =
            query_events(Some(institution_id), Some(account_id), None, None, page, 3).expect("Query failed");
        if page_events.is_empty() {
            break;
        }
        all_events.extend(page_events);
        page += 1;
    }
    assert_eq!(all_events.len(), events.len());
    // Ensure events are returned in order.
    for (a, b) in all_events.windows(2).map(|w| (&w[0], &w[1])) {
        assert!(a.timestamp <= b.timestamp);
    }
}

#[test]
fn test_concurrent_ingestion() {
    clear_store();

    let num_threads = 8;
    let events_per_thread = 50;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::new();

    for t in 0..num_threads {
        let c = barrier.clone();
        let thread_institution = format!("bank_concurrent");
        let thread_account = format!("acct_thread_{}", t);
        handles.push(thread::spawn(move || {
            // wait for all threads to be ready
            c.wait();
            let base_ts = current_time_ms();
            for i in 0..events_per_thread {
                let event = create_event(
                    base_ts + i as u64,
                    &thread_institution,
                    &thread_account,
                    EventType::Deposit,
                    100 + i as i64,
                    None,
                );
                let res = ingest_event(event);
                assert!(res.is_ok());
            }
        }));
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    // Verify total events across all threads.
    let result = query_events(Some("bank_concurrent"), None, None, None, 0, num_threads * events_per_thread)
        .expect("Query failed");
    assert_eq!(result.len(), num_threads * events_per_thread);
}

#[test]
fn test_fault_tolerance_simulation() {
    clear_store();

    // Simulate an institution going offline by not immediately ingesting events.
    let institution_id = "bank_offline";
    let account_id = "acct_offline";
    let base_ts = current_time_ms();

    // Collect events in a temporary buffer (simulate offline queue).
    let offline_events: Vec<Event> = (0..5)
        .map(|i| {
            create_event(
                base_ts + i * 100,
                institution_id,
                account_id,
                if i % 2 == 0 { EventType::Deposit } else { EventType::Withdrawal },
                500 + i as i64 * 10,
                None,
            )
        })
        .collect();

    // Initially, the global store should not have these events.
    let initial_query = query_events(Some(institution_id), Some(account_id), None, None, 0, 10)
        .expect("Query failed");
    assert_eq!(initial_query.len(), 0);

    // Simulate the institution coming back online: ingest all offline events.
    for event in offline_events.iter() {
        let res = ingest_event(event.clone());
        assert!(res.is_ok());
    }

    // Query after recovery: events should be present and ordered.
    let recovered_events =
        query_events(Some(institution_id), Some(account_id), None, None, 0, 10).expect("Query failed");
    assert_eq!(recovered_events.len(), 5);
    for (i, event) in recovered_events.iter().enumerate() {
        assert_eq!(event.amount, 500 + i as i64 * 10);
    }
}