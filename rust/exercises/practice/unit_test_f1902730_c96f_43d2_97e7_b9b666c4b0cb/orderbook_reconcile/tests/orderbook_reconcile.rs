use orderbook_reconcile::{reconcile_order_books, Order, Message};
use std::time::{Duration, Instant};

fn create_instant_offset(base: Instant, offset_millis: u64) -> Instant {
    base + Duration::from_millis(offset_millis)
}

#[test]
fn test_no_gossip_messages() {
    // Primary and secondary snapshots contain identical orders.
    let primary = vec![
        Order { order_id: 1, is_bid: true, price: 100, quantity: 10 },
        Order { order_id: 2, is_bid: false, price: 105, quantity: 15 },
    ];
    let secondary = vec![
        Order { order_id: 1, is_bid: true, price: 100, quantity: 10 },
        Order { order_id: 2, is_bid: false, price: 105, quantity: 15 },
    ];
    let messages: Vec<Message> = Vec::new();
    let time_window = Duration::from_secs(10);
    let (bids, asks) = reconcile_order_books(primary.clone(), secondary.clone(), messages, time_window);

    // Bids should contain order_id 1 and Asks order_id 2.
    assert_eq!(bids.len(), 1);
    assert_eq!(asks.len(), 1);
    assert_eq!(bids[0].order_id, 1);
    assert_eq!(asks[0].order_id, 2);
}

#[test]
fn test_add_order_within_time_window() {
    let now = Instant::now();
    // Primary snapshot only has one order.
    let primary = vec![
        Order { order_id: 1, is_bid: true, price: 100, quantity: 10 },
    ];
    let secondary = vec![
        Order { order_id: 1, is_bid: true, price: 100, quantity: 10 },
    ];
    let messages = vec![
        Message::AddOrder {
            order_id: 2,
            is_bid: false,
            price: 105,
            quantity: 20,
            timestamp: create_instant_offset(now, 100),
        },
        Message::AddOrder {
            order_id: 3,
            is_bid: true,
            price: 98,
            quantity: 30,
            timestamp: create_instant_offset(now, 200),
        },
    ];
    // Latest message is at now + 200ms; setting time window to 300ms includes both messages.
    let time_window = Duration::from_millis(300);
    let (bids, asks) = reconcile_order_books(primary.clone(), secondary.clone(), messages, time_window);

    // Expect primary order unchanged plus two added orders.
    // Bids should have order_id 1 and order_id 3 sorted in descending order by price.
    // Asks should contain order_id 2.
    assert_eq!(bids.len(), 2);
    assert_eq!(asks.len(), 1);
    assert_eq!(bids[0].price, 100);
    assert_eq!(bids[1].price, 98);
    assert_eq!(asks[0].price, 105);
}

#[test]
fn test_cancel_order_and_execute_order() {
    let now = Instant::now();
    // Primary and secondary snapshots contain two orders.
    let primary = vec![
        Order { order_id: 10, is_bid: true, price: 200, quantity: 50 },
        Order { order_id: 20, is_bid: false, price: 205, quantity: 30 },
    ];
    let secondary = vec![
        Order { order_id: 10, is_bid: true, price: 200, quantity: 50 },
        Order { order_id: 20, is_bid: false, price: 205, quantity: 30 },
    ];
    let messages = vec![
        // Cancel order_id 10.
        Message::CancelOrder {
            order_id: 10,
            timestamp: create_instant_offset(now, 50),
        },
        // Execute order_id 20 partially.
        Message::ExecuteOrder {
            order_id: 20,
            executed_quantity: 10,
            timestamp: create_instant_offset(now, 100),
        },
        // Execute order_id 20 to completion.
        Message::ExecuteOrder {
            order_id: 20,
            executed_quantity: 20,
            timestamp: create_instant_offset(now, 150),
        },
    ];
    let time_window = Duration::from_millis(200);
    let (bids, asks) = reconcile_order_books(primary.clone(), secondary.clone(), messages, time_window);

    // Expect both orders to be removed after cancellation and full execution.
    assert_eq!(bids.len(), 0);
    assert_eq!(asks.len(), 0);
}

#[test]
fn test_stale_messages_filtered_by_time_window() {
    let now = Instant::now();
    // Primary and secondary snapshots with one order.
    let primary = vec![
        Order { order_id: 100, is_bid: true, price: 150, quantity: 20 },
    ];
    let secondary = vec![
        Order { order_id: 100, is_bid: true, price: 150, quantity: 20 },
    ];
    let messages = vec![
        Message::AddOrder {
            order_id: 101,
            is_bid: false,
            price: 155,
            quantity: 25,
            timestamp: create_instant_offset(now, 100),
        },
        Message::CancelOrder {
            order_id: 100,
            timestamp: create_instant_offset(now, 150),
        },
        Message::ExecuteOrder {
            order_id: 101,
            executed_quantity: 5,
            timestamp: create_instant_offset(now, 500),
        },
    ];
    // Latest message is at now + 500ms; set the time window to 300ms.
    // This means messages before now + 200ms are considered stale.
    let time_window = Duration::from_millis(300);
    let (bids, asks) = reconcile_order_books(primary.clone(), secondary.clone(), messages, time_window);

    // The AddOrder and CancelOrder messages are stale.
    // Only the ExecuteOrder at 500ms is processed, but it refers to order 101 which was never added.
    // Therefore, primary order remains unchanged.
    assert_eq!(bids.len(), 1);
    assert_eq!(asks.len(), 0);
    assert_eq!(bids[0].order_id, 100);
    assert_eq!(bids[0].quantity, 20);
}

#[test]
fn test_conflicting_primary_secondary_snapshot() {
    let now = Instant::now();
    // Primary snapshot has a different quantity than secondary; primary takes precedence.
    let primary = vec![
        Order { order_id: 201, is_bid: false, price: 250, quantity: 40 },
    ];
    let secondary = vec![
        Order { order_id: 201, is_bid: false, price: 250, quantity: 35 },
    ];
    let messages = vec![
        Message::ExecuteOrder {
            order_id: 201,
            executed_quantity: 10,
            timestamp: create_instant_offset(now, 50),
        },
    ];
    let time_window = Duration::from_millis(100);
    let (bids, asks) = reconcile_order_books(primary.clone(), secondary.clone(), messages, time_window);

    // Starting from primary quantity of 40, executing 10 should result in 30 remaining.
    assert_eq!(asks.len(), 1);
    assert_eq!(asks[0].order_id, 201);
    assert_eq!(asks[0].quantity, 30);
}