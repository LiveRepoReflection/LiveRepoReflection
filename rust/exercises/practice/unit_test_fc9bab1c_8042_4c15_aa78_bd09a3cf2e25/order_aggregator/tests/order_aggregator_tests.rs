use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use order_aggregator::{Order, OrderAggregator, OrderSide};

#[test]
fn test_aggregate_top_of_book() {
    // Create a new aggregator instance.
    let mut aggregator = OrderAggregator::new();

    // Provider 1 orders: Bid: price=100, Ask: price=110.
    let orders_p1 = vec![
        Order::new("p1".to_string(), 100, 10, OrderSide::Bid),
        Order::new("p1".to_string(), 110, 5, OrderSide::Ask),
    ];
    aggregator.update_provider("p1".to_string(), orders_p1);

    // Provider 2 orders: Bid: price=102, Ask: price=108.
    let orders_p2 = vec![
        Order::new("p2".to_string(), 102, 8, OrderSide::Bid),
        Order::new("p2".to_string(), 108, 3, OrderSide::Ask),
    ];
    aggregator.update_provider("p2".to_string(), orders_p2);

    // The best bid should be the maximum bid and the best ask the minimum ask.
    let top = aggregator.get_top_of_book().unwrap();
    assert_eq!(top.0, Some(102));
    assert_eq!(top.1, Some(108));
}

#[test]
fn test_order_filtering() {
    let mut aggregator = OrderAggregator::new();

    // Add a set of orders from different providers.
    let orders_p1 = vec![
        Order::new("p1".to_string(), 95, 15, OrderSide::Bid),
        Order::new("p1".to_string(), 100, 10, OrderSide::Bid),
        Order::new("p1".to_string(), 112, 5, OrderSide::Ask),
    ];
    let orders_p2 = vec![
        Order::new("p2".to_string(), 105, 20, OrderSide::Ask),
        Order::new("p2".to_string(), 110, 7, OrderSide::Ask),
        Order::new("p2".to_string(), 90, 12, OrderSide::Bid),
    ];
    aggregator.update_provider("p1".to_string(), orders_p1);
    aggregator.update_provider("p2".to_string(), orders_p2);

    // Filter orders: price between 100 and 110, and minimum quantity 10.
    let filtered = aggregator.get_orders(100, 110, 10).unwrap();

    // Expected orders: p1 bid at 100 (10 units) and p2 ask at 105 (20 units).
    let mut found_100_bid = false;
    let mut found_105_ask = false;
    for order in filtered {
        if order.price == 100 && order.quantity == 10 && order.side == OrderSide::Bid {
            found_100_bid = true;
        }
        if order.price == 105 && order.quantity == 20 && order.side == OrderSide::Ask {
            found_105_ask = true;
        }
    }
    assert!(found_100_bid, "Filtered results should include the p1 bid at price 100.");
    assert!(found_105_ask, "Filtered results should include the p2 ask at price 105.");
}

#[test]
fn test_provider_failure() {
    let mut aggregator = OrderAggregator::new();

    // Provider 1 orders.
    let orders_p1 = vec![
        Order::new("p1".to_string(), 100, 10, OrderSide::Bid),
        Order::new("p1".to_string(), 110, 5, OrderSide::Ask),
    ];
    aggregator.update_provider("p1".to_string(), orders_p1);

    // Provider 2 orders.
    let orders_p2 = vec![
        Order::new("p2".to_string(), 102, 8, OrderSide::Bid),
        Order::new("p2".to_string(), 108, 3, OrderSide::Ask),
    ];
    aggregator.update_provider("p2".to_string(), orders_p2);

    // Verify initial top of the book includes orders from both providers.
    let top_initial = aggregator.get_top_of_book().unwrap();
    assert_eq!(top_initial.0, Some(102));
    assert_eq!(top_initial.1, Some(108));

    // Simulate provider failure by removing provider "p2".
    aggregator.remove_provider("p2");
    let top_after_failure = aggregator.get_top_of_book().unwrap();
    
    // Now, only provider "p1" orders remain.
    assert_eq!(top_after_failure.0, Some(100));
    assert_eq!(top_after_failure.1, Some(110));
}

#[test]
fn test_asynchronous_updates() {
    // Wrap the aggregator in an Arc<Mutex<_>> to safely share it between threads.
    let aggregator = Arc::new(Mutex::new(OrderAggregator::new()));

    // Thread simulating asynchronous updates from Provider 1.
    let aggregator_clone1 = Arc::clone(&aggregator);
    let handle1 = thread::spawn(move || {
        for _ in 0..3 {
            let orders = vec![
                Order::new("p1".to_string(), 100, 10, OrderSide::Bid),
                Order::new("p1".to_string(), 110, 5, OrderSide::Ask),
            ];
            aggregator_clone1.lock().unwrap().update_provider("p1".to_string(), orders);
            thread::sleep(Duration::from_millis(50));
        }
    });

    // Thread simulating asynchronous updates from Provider 2.
    let aggregator_clone2 = Arc::clone(&aggregator);
    let handle2 = thread::spawn(move || {
        for _ in 0..3 {
            let orders = vec![
                Order::new("p2".to_string(), 102, 8, OrderSide::Bid),
                Order::new("p2".to_string(), 108, 3, OrderSide::Ask),
            ];
            aggregator_clone2.lock().unwrap().update_provider("p2".to_string(), orders);
            thread::sleep(Duration::from_millis(60));
        }
    });

    // Wait for both threads to finish.
    handle1.join().unwrap();
    handle2.join().unwrap();

    // Retrieve the top of the book after asynchronous updates.
    let top = aggregator.lock().unwrap().get_top_of_book().unwrap();
    // Best bid should be the maximum of (100, 102) and best ask the minimum of (110, 108).
    assert_eq!(top.0, Some(102));
    assert_eq!(top.1, Some(108));
}