use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use dex_matching::{OrderBook, Order, OrderType, Trade};

#[test]
fn test_basic_match() {
    // Create a new order book instance.
    let mut book = OrderBook::new();

    // Place a buy order with price 100.0 and quantity 50.
    let buy_order = Order {
        id: 1,
        order_type: OrderType::Buy,
        price: 100.0,
        quantity: 50,
    };
    // Place a sell order with price 99.0 and quantity 50.
    let sell_order = Order {
        id: 2,
        order_type: OrderType::Sell,
        price: 99.0,
        quantity: 50,
    };

    // Add the buy order.
    let trades_buy = book.add_order(buy_order).expect("Order accepted");
    // should have no trades yet
    assert!(trades_buy.is_empty());

    // Add the sell order.
    let trades_sell = book.add_order(sell_order).expect("Order accepted");

    // A trade should have been executed.
    assert_eq!(trades_sell.len(), 1);

    let trade = &trades_sell[0];
    // Check that trade details are correct.
    assert_eq!(trade.buy_order_id, 1);
    assert_eq!(trade.sell_order_id, 2);
    assert!(trade.price >= 99.0 && trade.price <= 100.0);
    assert_eq!(trade.quantity, 50);
}

#[test]
fn test_partial_fill() {
    let mut book = OrderBook::new();

    // Buy order with quantity 100.
    let buy_order = Order {
        id: 3,
        order_type: OrderType::Buy,
        price: 105.0,
        quantity: 100,
    };

    // Sell order with quantity 60.
    let sell_order = Order {
        id: 4,
        order_type: OrderType::Sell,
        price: 104.0,
        quantity: 60,
    };

    let trades_buy = book.add_order(buy_order).expect("Order accepted");
    assert!(trades_buy.is_empty());

    let trades_sell = book.add_order(sell_order).expect("Order accepted");
    assert_eq!(trades_sell.len(), 1);
    let trade = &trades_sell[0];
    assert_eq!(trade.quantity, 60);

    // The remaining quantity of the buy order should be 40.
    let state = book.get_state();
    let remaining_buy = state.buy_orders.into_iter().find(|o| o.id == 3);
    assert!(remaining_buy.is_some());
    assert_eq!(remaining_buy.unwrap().quantity, 40);
}

#[test]
fn test_fifo_priority() {
    let mut book = OrderBook::new();

    // Two sell orders with the same price.
    let sell_order1 = Order {
        id: 5,
        order_type: OrderType::Sell,
        price: 102.0,
        quantity: 30,
    };
    let sell_order2 = Order {
        id: 6,
        order_type: OrderType::Sell,
        price: 102.0,
        quantity: 30,
    };

    // Place sell orders.
    let trades1 = book.add_order(sell_order1).expect("Order accepted");
    assert!(trades1.is_empty());
    let trades2 = book.add_order(sell_order2).expect("Order accepted");
    assert!(trades2.is_empty());

    // Now, a buy order that can match with both.
    let buy_order = Order {
        id: 7,
        order_type: OrderType::Buy,
        price: 103.0,
        quantity: 50,
    };

    let trades_buy = book.add_order(buy_order).expect("Order accepted");
    // Expect one trade with the earliest (sell_order1) fully executed and a partial execution on sell_order2.
    assert_eq!(trades_buy.len(), 2);
    // First trade should be from order id 5.
    assert_eq!(trades_buy[0].sell_order_id, 5);
    assert_eq!(trades_buy[0].quantity, 30);
    // Second trade from order id 6, quantity 20 since total buy was 50.
    assert_eq!(trades_buy[1].sell_order_id, 6);
    assert_eq!(trades_buy[1].quantity, 20);

    // Remaining quantity for sell_order2 should be 10.
    let state = book.get_state();
    let remaining_sell = state.sell_orders.into_iter().find(|o| o.id == 6);
    assert!(remaining_sell.is_some());
    assert_eq!(remaining_sell.unwrap().quantity, 10);
}

#[test]
fn test_order_cancellation() {
    let mut book = OrderBook::new();

    // Place orders.
    let order_to_cancel = Order {
        id: 8,
        order_type: OrderType::Buy,
        price: 101.0,
        quantity: 40,
    };
    let _ = book.add_order(order_to_cancel).expect("Order accepted");

    // Cancellation should succeed.
    let cancel_result = book.cancel_order(8);
    assert!(cancel_result);

    // Trying to cancel again should fail.
    let cancel_again = book.cancel_order(8);
    assert!(!cancel_again);

    // Verify the order is no longer in state.
    let state = book.get_state();
    let order_exists = state.buy_orders.iter().any(|o| o.id == 8);
    assert!(!order_exists);
}

#[test]
fn test_persistence_and_recovery() {
    let mut book = OrderBook::new();

    // Place multiple orders.
    let orders = vec![
        Order { id: 9, order_type: OrderType::Buy, price: 110.0, quantity: 70 },
        Order { id: 10, order_type: OrderType::Sell, price: 109.0, quantity: 70 },
        Order { id: 11, order_type: OrderType::Buy, price: 108.0, quantity: 50 },
    ];

    for order in orders {
        let _ = book.add_order(order).expect("Order accepted");
    }

    // Persist the state.
    book.persist().expect("Persistence succeeded");

    // Simulate recovery.
    let recovered_book = OrderBook::recover().expect("Recovery succeeded");

    // Check that the recovered book state matches the original state.
    let original_state = book.get_state();
    let recovered_state = recovered_book.get_state();

    // Compare buy orders
    assert_eq!(original_state.buy_orders.len(), recovered_state.buy_orders.len());
    // Compare sell orders
    assert_eq!(original_state.sell_orders.len(), recovered_state.sell_orders.len());
    // More detailed comparisons could be made, such as order IDs and quantities.
    for (orig, recov) in original_state.buy_orders.iter().zip(recovered_state.buy_orders.iter()) {
        assert_eq!(orig.id, recov.id);
        assert_eq!(orig.price, recov.price);
        assert_eq!(orig.quantity, recov.quantity);
    }
    for (orig, recov) in original_state.sell_orders.iter().zip(recovered_state.sell_orders.iter()) {
        assert_eq!(orig.id, recov.id);
        assert_eq!(orig.price, recov.price);
        assert_eq!(orig.quantity, recov.quantity);
    }
}

#[test]
fn test_concurrent_order_submission() {
    let book = Arc::new(Mutex::new(OrderBook::new()));
    let mut handles = vec![];

    // Create 10 threads submitting orders concurrently.
    for i in 0..10 {
        let book_ref = Arc::clone(&book);
        let handle = thread::spawn(move || {
            // Each thread will add 10 orders.
            for j in 0..10 {
                // Alternate between buy and sell orders.
                let order = if j % 2 == 0 {
                    Order {
                        id: i * 100 + j,
                        order_type: OrderType::Buy,
                        price: 100.0 + (j as f64),
                        quantity: 10 + j,
                    }
                } else {
                    Order {
                        id: i * 100 + j,
                        order_type: OrderType::Sell,
                        price: 100.0 + (j as f64) - 1.0,
                        quantity: 10 + j,
                    }
                };
                {
                    let mut book = book_ref.lock().unwrap();
                    let _ = book.add_order(order);
                }
                // Simulate network latency.
                thread::sleep(Duration::from_millis(5));
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("Thread panicked");
    }

    // Ensure that total orders in the book match the expected count after possible matches.
    let book_final = book.lock().unwrap();
    let state = book_final.get_state();
    let total_orders = state.buy_orders.len() + state.sell_orders.len();
    // Since orders might have been matched, the remaining orders should not exceed 100.
    assert!(total_orders <= 100);
}

#[test]
fn test_trade_execution_details() {
    let mut book = OrderBook::new();

    // Create multiple orders to produce multiple trades.
    let buy_order1 = Order {
        id: 201,
        order_type: OrderType::Buy,
        price: 120.0,
        quantity: 40,
    };
    let buy_order2 = Order {
        id: 202,
        order_type: OrderType::Buy,
        price: 118.0,
        quantity: 30,
    };
    let sell_order1 = Order {
        id: 203,
        order_type: OrderType::Sell,
        price: 119.0,
        quantity: 20,
    };
    let sell_order2 = Order {
        id: 204,
        order_type: OrderType::Sell,
        price: 117.0,
        quantity: 50,
    };

    // Add orders in an order that requires multiple matching operations.
    let _ = book.add_order(buy_order1).expect("Order accepted");
    let trades_sell1 = book.add_order(sell_order1).expect("Order accepted");
    // Check first match from buy_order1.
    assert_eq!(trades_sell1.len(), 1);
    assert_eq!(trades_sell1[0].buy_order_id, 201);
    assert_eq!(trades_sell1[0].sell_order_id, 203);
    assert_eq!(trades_sell1[0].quantity, 20);

    let trades_buy2 = book.add_order(buy_order2).expect("Order accepted");
    // No immediate match expected.
    assert!(trades_buy2.is_empty());

    let trades_sell2 = book.add_order(sell_order2).expect("Order accepted");
    // This should yield multiple trade executions.
    // First, complete remaining quantity for buy_order1 (20) then use buy_order2 partially.
    let total_trade_qty: u64 = trades_sell2.iter().map(|t| t.quantity).sum();
    assert_eq!(total_trade_qty, 50);
    // Verify trade details conform with expected order ids.
    let mut has_trade_201 = false;
    let mut has_trade_202 = false;
    for trade in trades_sell2 {
        if trade.buy_order_id == 201 {
            has_trade_201 = true;
        } else if trade.buy_order_id == 202 {
            has_trade_202 = true;
        }
    }
    assert!(has_trade_201 && has_trade_202);
}