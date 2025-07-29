use dex_matcher::{Order, OrderType, Cancellation, Trade, process_orderbook};

#[test]
fn test_no_orders() {
    let orders = vec![];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    assert!(trades.is_empty());
}

#[test]
fn test_single_exact_match() {
    let orders = vec![
        Order { order_id: 1, timestamp: 100, order_type: OrderType::Buy, price: 1000, quantity: 500 },
        Order { order_id: 2, timestamp: 200, order_type: OrderType::Sell, price: 1000, quantity: 500 },
    ];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.buy_order_id, 1);
    assert_eq!(trade.sell_order_id, 2);
    assert_eq!(trade.price, 1000);
    assert_eq!(trade.quantity, 500);
}

#[test]
fn test_partial_fill() {
    let orders = vec![
        // Buy order larger than sell orders, requiring multiple trades.
        Order { order_id: 3, timestamp: 300, order_type: OrderType::Buy, price: 1000, quantity: 700 },
        Order { order_id: 4, timestamp: 310, order_type: OrderType::Sell, price: 1000, quantity: 300 },
        Order { order_id: 5, timestamp: 320, order_type: OrderType::Sell, price: 1000, quantity: 400 },
    ];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    // Expect two trades: one filling 300 and one filling 400.
    assert_eq!(trades.len(), 2);
    let trade1 = &trades[0];
    let trade2 = &trades[1];
    assert_eq!(trade1.buy_order_id, 3);
    assert_eq!(trade1.sell_order_id, 4);
    assert_eq!(trade1.price, 1000);
    assert_eq!(trade1.quantity, 300);
    assert_eq!(trade2.buy_order_id, 3);
    assert_eq!(trade2.sell_order_id, 5);
    assert_eq!(trade2.price, 1000);
    assert_eq!(trade2.quantity, 400);
}

#[test]
fn test_order_priority_time() {
    // Multiple sell orders at the same price, different timestamps.
    // The sell order with the earliest timestamp should be matched first.
    let orders = vec![
        Order { order_id: 6, timestamp: 500, order_type: OrderType::Sell, price: 1000, quantity: 250 },
        Order { order_id: 7, timestamp: 510, order_type: OrderType::Sell, price: 1000, quantity: 250 },
        Order { order_id: 8, timestamp: 520, order_type: OrderType::Buy, price: 1000, quantity: 500 },
    ];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    assert_eq!(trades.len(), 2);
    let trade1 = &trades[0];
    let trade2 = &trades[1];
    assert_eq!(trade1.buy_order_id, 8);
    assert_eq!(trade1.sell_order_id, 6);
    assert_eq!(trade1.quantity, 250);
    assert_eq!(trade2.buy_order_id, 8);
    assert_eq!(trade2.sell_order_id, 7);
    assert_eq!(trade2.quantity, 250);
}

#[test]
fn test_price_priority() {
    // The buy order should match with the sell order offering the lowest price.
    let orders = vec![
        Order { order_id: 9, timestamp: 600, order_type: OrderType::Sell, price: 995, quantity: 300 },
        Order { order_id: 10, timestamp: 610, order_type: OrderType::Sell, price: 1000, quantity: 300 },
        Order { order_id: 11, timestamp: 620, order_type: OrderType::Buy, price: 1000, quantity: 300 },
    ];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.buy_order_id, 11);
    assert_eq!(trade.sell_order_id, 9);
    assert_eq!(trade.price, 995);
    assert_eq!(trade.quantity, 300);
}

#[test]
fn test_order_cancellations() {
    // Test that cancellations prevent orders from being matched.
    let orders = vec![
        Order { order_id: 12, timestamp: 700, order_type: OrderType::Buy, price: 1000, quantity: 500 },
        Order { order_id: 13, timestamp: 710, order_type: OrderType::Sell, price: 1000, quantity: 500 },
        Order { order_id: 14, timestamp: 720, order_type: OrderType::Sell, price: 1000, quantity: 500 },
    ];
    // Cancellation for order 13 should remove it from matching consideration.
    let cancellations = vec![
        Cancellation { order_id: 13 },
    ];
    let trades = process_orderbook(orders, cancellations);
    // Only one trade is expected between order 12 and order 14.
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.buy_order_id, 12);
    assert_eq!(trade.sell_order_id, 14);
    assert_eq!(trade.price, 1000);
    assert_eq!(trade.quantity, 500);
}

#[test]
fn test_no_matches_due_to_price() {
    // Test scenario where orders do not cross in price.
    let orders = vec![
        Order { order_id: 15, timestamp: 800, order_type: OrderType::Buy, price: 980, quantity: 400 },
        Order { order_id: 16, timestamp: 810, order_type: OrderType::Sell, price: 1000, quantity: 400 },
    ];
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    assert!(trades.is_empty());
}

#[test]
fn test_multiple_matches_with_partial_fill_and_cancellation() {
    // Complex scenario with partial fills and a cancellation.
    let orders = vec![
        Order { order_id: 17, timestamp: 900, order_type: OrderType::Sell, price: 1000, quantity: 200 },
        Order { order_id: 18, timestamp: 905, order_type: OrderType::Sell, price: 1000, quantity: 300 },
        Order { order_id: 19, timestamp: 910, order_type: OrderType::Buy, price: 1000, quantity: 400 },
        Order { order_id: 20, timestamp: 915, order_type: OrderType::Buy, price: 990, quantity: 200 },
        Order { order_id: 21, timestamp: 920, order_type: OrderType::Sell, price: 1000, quantity: 100 },
    ];
    // Cancel order 18 so it does not participate in matching.
    let cancellations = vec![
        Cancellation { order_id: 18 },
    ];
    let trades = process_orderbook(orders, cancellations);
    // Expected: Order 19 matches with order 17 for 200 and order 21 for 100.
    assert_eq!(trades.len(), 2);
    let trade1 = &trades[0];
    let trade2 = &trades[1];
    assert_eq!(trade1.buy_order_id, 19);
    assert_eq!(trade1.sell_order_id, 17);
    assert_eq!(trade1.quantity, 200);
    assert_eq!(trade2.buy_order_id, 19);
    assert_eq!(trade2.sell_order_id, 21);
    assert_eq!(trade2.quantity, 100);
}

#[test]
fn test_large_volume_performance() {
    // Simulate a large volume order book scenario.
    let mut orders = Vec::new();
    // Generate 500 buy orders.
    for i in 0..500 {
        orders.push(Order { order_id: 1000 + i as u64, timestamp: 1000 + i as u64, order_type: OrderType::Buy, price: 1000, quantity: 100 });
    }
    // Generate 500 sell orders.
    for i in 0..500 {
        orders.push(Order { order_id: 2000 + i as u64, timestamp: 2000 + i as u64, order_type: OrderType::Sell, price: 1000, quantity: 100 });
    }
    let cancellations = vec![];
    let trades = process_orderbook(orders, cancellations);
    // Expect 500 complete trades.
    assert_eq!(trades.len(), 500);
    for trade in trades {
        assert_eq!(trade.price, 1000);
        assert_eq!(trade.quantity, 100);
    }
}