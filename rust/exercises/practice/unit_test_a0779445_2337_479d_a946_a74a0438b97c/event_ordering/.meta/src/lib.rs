use std::collections::HashMap;

pub type Event = (String, String, u64, u64, String);

pub fn order_events(events: Vec<Event>) -> HashMap<String, Vec<Event>> {
    let mut txn_map: HashMap<String, Vec<Event>> = HashMap::new();
    
    // Group events by transaction_id
    for event in events {
        txn_map
            .entry(event.0.clone())
            .or_insert_with(Vec::new)
            .push(event);
    }
    
    // For each transaction, sort the events using the specified rules:
    // 1. If events from the same service_id, order by event_id (ascending).
    // 2. Otherwise, order primarily by timestamp (ascending).
    // 3. If timestamps are equal, order by service_id (alphabetically).
    for events in txn_map.values_mut() {
        events.sort_by(|a, b| {
            if a.1 == b.1 {
                // Same service id: enforce event_id ordering
                a.2.cmp(&b.2)
            } else if a.3 == b.3 {
                // Different service, but same timestamp: compare service_id alphabetically.
                a.1.cmp(&b.1)
            } else {
                // Different services: order by timestamp.
                a.3.cmp(&b.3)
            }
        });
    }
    
    txn_map
}