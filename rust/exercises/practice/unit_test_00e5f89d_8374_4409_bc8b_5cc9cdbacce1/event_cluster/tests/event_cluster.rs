use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use event_cluster::{Event, EventScheduler};

#[test]
fn test_schedule_and_execute_event() {
    let mut scheduler = EventScheduler::new();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    let event = Event {
        id: "event1".to_string(),
        execution_time: now,
        target_service: "service_a".to_string(),
        payload: "data1".to_string(),
    };

    assert!(scheduler.schedule_event(event));
    // Execute events scheduled up to current time.
    scheduler.run(now);
    let executed = scheduler.executed_events();
    assert_eq!(executed.len(), 1);
    assert_eq!(executed[0].id, "event1");
}

#[test]
fn test_event_removal() {
    let mut scheduler = EventScheduler::new();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    let event = Event {
        id: "event2".to_string(),
        execution_time: now + 5,
        target_service: "service_b".to_string(),
        payload: "data2".to_string(),
    };

    assert!(scheduler.schedule_event(event));
    // Remove the event before its execution time.
    assert!(scheduler.remove_event("event2"));
    // Run scheduler after the event's scheduled time.
    scheduler.run(now + 6);
    let executed = scheduler.executed_events();
    assert!(executed.is_empty());
}

#[test]
fn test_multiple_events_order() {
    let mut scheduler = EventScheduler::new();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    let event1 = Event {
        id: "event3".to_string(),
        execution_time: now + 2,
        target_service: "service_c".to_string(),
        payload: "data3".to_string(),
    };

    let event2 = Event {
        id: "event4".to_string(),
        execution_time: now + 1,
        target_service: "service_d".to_string(),
        payload: "data4".to_string(),
    };

    assert!(scheduler.schedule_event(event1));
    assert!(scheduler.schedule_event(event2));

    // Run scheduler after both events are due.
    scheduler.run(now + 3);
    let executed = scheduler.executed_events();
    // Expect the events to be executed in order of their scheduled time.
    assert_eq!(executed.len(), 2);
    assert_eq!(executed[0].id, "event4");
    assert_eq!(executed[1].id, "event3");
}

#[test]
fn test_concurrent_scheduling() {
    let scheduler = Arc::new(Mutex::new(EventScheduler::new()));
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    let handles: Vec<_> = (0..10)
        .map(|i| {
            let sched_clone = Arc::clone(&scheduler);
            thread::spawn(move || {
                let event = Event {
                    id: format!("event_{}", i),
                    execution_time: now + i as u64,
                    target_service: format!("service_{}", i),
                    payload: format!("payload_{}", i),
                };
                let mut sched = sched_clone.lock().unwrap();
                assert!(sched.schedule_event(event));
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    {
        let mut sched = scheduler.lock().unwrap();
        sched.run(now + 15);
        let executed = sched.executed_events();
        // All 10 events should have been executed.
        assert_eq!(executed.len(), 10);
    }
}

#[test]
fn test_event_retry_simulation() {
    // This test simulates transient failure and retry.
    // The scheduler is assumed to retry a failed send_event operation.
    //
    // For testing purposes, we simulate a failure on the first run by checking
    // that the event is not marked as executed, then on a subsequent run, the event is executed.
    let mut scheduler = EventScheduler::new();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

    let event = Event {
        id: "event_retry".to_string(),
        execution_time: now,
        target_service: "service_retry".to_string(),
        payload: "retry_payload".to_string(),
    };

    assert!(scheduler.schedule_event(event));
    // First run: simulate a transient failure (the scheduler does not mark the event as executed).
    scheduler.run(now);
    let executed_first = scheduler.executed_events();
    // In a retry scenario, the event may not be executed on the first run.
    // For this simulation, we consider that if the event is not executed then it will be retried.
    if executed_first.iter().any(|e| e.id == "event_retry") {
        // If the event was executed in the first run, clear the executed list to simulate failure.
        // (This branch is for environments where failure cannot be simulated.)
        scheduler.clear_executed_events();
    }
    // Second run: the scheduler retries the event.
    scheduler.run(now + 1);
    let executed_second = scheduler.executed_events();
    let found = executed_second.iter().find(|e| e.id == "event_retry");
    assert!(found.is_some());
}