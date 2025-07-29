use order_matcher::{OrderMatcher, OrderEvent, TradeEvent, OrderSide, OrderAction};

fn create_new_event(
    timestamp: u64,
    order_id: &str,
    user_id: &str,
    side: OrderSide,
    price: u64,
    quantity: u64,
) -> OrderEvent {
    OrderEvent {
        timestamp,
        order_id: order_id.to_string(),
        user_id: user_id.to_string(),
        side,
        price,
        quantity,
        action: OrderAction::New,
    }
}

fn create_cancel_event(
    timestamp: u64,
    order_id: &str,
    user_id: &str,
    side: OrderSide,
    price: u64,
) -> OrderEvent {
    OrderEvent {
        timestamp,
        order_id: order_id.to_string(),
        user_id: user_id.to_string(),
        side,
        price,
        quantity: 0,
        action: OrderAction::Cancel,
    }
}

#[test]
fn test_full_match() {
    let mut matcher = OrderMatcher::new();

    // Insert a buy order
    let event1 = create_new_event(1, "buy1", "alice", OrderSide::Buy, 100, 10);
    let trades1 = matcher.process_event(event1);
    // No match yet
    assert!(trades1.is_empty());

    // Insert a sell order at matching price and quantity
    let event2 = create_new_event(2, "sell1", "bob", OrderSide::Sell, 100, 10);
    let trades2 = matcher.process_event(event2);
    // Expect a full trade match
    assert_eq!(trades2.len(), 1);
    let trade = &trades2[0];
    assert_eq!(trade.price, 100);
    assert_eq!(trade.quantity, 10);
    // Since buy order was first, it should be matched with sell1
    assert_eq!(trade.buy_order_id, "buy1");
    assert_eq!(trade.sell_order_id, "sell1");
}

#[test]
fn test_partial_fill() {
    let mut matcher = OrderMatcher::new();

    // Insert a buy order with larger quantity
    let event1 = create_new_event(1, "buy2", "alice", OrderSide::Buy, 100, 15);
    let trades1 = matcher.process_event(event1);
    assert!(trades1.is_empty());

    // Insert a sell order that partially fills the buy order.
    let event2 = create_new_event(2, "sell2", "bob", OrderSide::Sell, 100, 10);
    let trades2 = matcher.process_event(event2);
    // Expect one trade of quantity 10.
    assert_eq!(trades2.len(), 1);
    let trade1 = &trades2[0];
    assert_eq!(trade1.price, 100);
    assert_eq!(trade1.quantity, 10);
    assert_eq!(trade1.buy_order_id, "buy2");
    assert_eq!(trade1.sell_order_id, "sell2");

    // The remaining quantity of the buy order should be 5.
    // Insert another sell order that can fill the remaining quantity.
    let event3 = create_new_event(3, "sell3", "charlie", OrderSide::Sell, 100, 10);
    let trades3 = matcher.process_event(event3);
    // Expect a trade of quantity 5 to fully consume the remaining buy order.
    assert_eq!(trades3.len(), 1);
    let trade2 = &trades3[0];
    assert_eq!(trade2.price, 100);
    assert_eq!(trade2.quantity, 5);
    assert_eq!(trade2.buy_order_id, "buy2");
    assert_eq!(trade2.sell_order_id, "sell3");
}

#[test]
fn test_order_cancellation() {
    let mut matcher = OrderMatcher::new();

    // Insert a buy order and then cancel it.
    let event1 = create_new_event(1, "buy3", "alice", OrderSide::Buy, 105, 10);
    let trades1 = matcher.process_event(event1);
    assert!(trades1.is_empty());

    // Cancel the order.
    let cancel_event = create_cancel_event(2, "buy3", "alice", OrderSide::Buy, 105);
    let trades2 = matcher.process_event(cancel_event);
    // Cancellation should not produce any trades.
    assert!(trades2.is_empty());

    // Insert a sell order that would have matched the cancelled buy order.
    let event2 = create_new_event(3, "sell4", "bob", OrderSide::Sell, 105, 10);
    let trades3 = matcher.process_event(event2);
    // Since buy3 was cancelled, no trade should happen.
    assert!(trades3.is_empty());
}

#[test]
fn test_order_priority() {
    let mut matcher = OrderMatcher::new();

    // Insert two sell orders at the same price, different timestamps.
    let event1 = create_new_event(1, "sell5", "bob", OrderSide::Sell, 100, 5);
    let trades1 = matcher.process_event(event1);
    assert!(trades1.is_empty());

    let event2 = create_new_event(2, "sell6", "charlie", OrderSide::Sell, 100, 10);
    let trades2 = matcher.process_event(event2);
    assert!(trades2.is_empty());

    // Insert a buy order that can fill only part of both sell orders.
    let event3 = create_new_event(3, "buy4", "alice", OrderSide::Buy, 100, 10);
    let trades3 = matcher.process_event(event3);
    // Expect a trade with sell5 fully matched first (5 units) and then sell6 partially filled (5 units)
    assert_eq!(trades3.len(), 2);
    
    let trade_first = &trades3[0];
    assert_eq!(trade_first.quantity, 5);
    assert_eq!(trade_first.buy_order_id, "buy4");
    assert_eq!(trade_first.sell_order_id, "sell5");

    let trade_second = &trades3[1];
    assert_eq!(trade_second.quantity, 5);
    assert_eq!(trade_second.buy_order_id, "buy4");
    assert_eq!(trade_second.sell_order_id, "sell6");
}

#[test]
fn test_no_match_due_to_price() {
    let mut matcher = OrderMatcher::new();

    // Insert a buy order with a lower price.
    let event1 = create_new_event(1, "buy5", "alice", OrderSide::Buy, 99, 10);
    let trades1 = matcher.process_event(event1);
    assert!(trades1.is_empty());

    // Insert a sell order with a higher price.
    let event2 = create_new_event(2, "sell7", "bob", OrderSide::Sell, 100, 10);
    let trades2 = matcher.process_event(event2);
    // No trade should occur due to price mismatch.
    assert!(trades2.is_empty());
}

#[test]
fn test_cancel_nonexistent_order() {
    let mut matcher = OrderMatcher::new();
    // Attempt to cancel an order that was never added.
    let cancel_event = create_cancel_event(1, "nonexistent", "ghost", OrderSide::Buy, 100);
    let trades = matcher.process_event(cancel_event);
    // Expected to have no trade and handle the cancellation gracefully.
    assert!(trades.is_empty());
}