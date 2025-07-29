use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

use dex_engine::{DexEngine, Order, OrderType, Trade};

fn create_order(order_id: &str, order_type: OrderType, price: u32, quantity: u64) -> Order {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_nanos() as u64;
    Order {
        order_id: order_id.to_string(),
        timestamp: now,
        order_type,
        price,
        quantity,
        user_id: "user1".to_string(),
        signature: "valid_signature".to_string(),
    }
}

#[test]
fn test_single_match() {
    let mut engine = DexEngine::new();
    // Create a buy and sell order that should match exactly.
    let buy_order = create_order("buy1", OrderType::Buy, 1000, 10);
    let sell_order = create_order("sell1", OrderType::Sell, 1000, 10);
    engine.submit_order(buy_order);
    engine.submit_order(sell_order);
    // Process matching orders.
    engine.match_orders();
    let trades = engine.get_trades();
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.price, 1000);
    assert_eq!(trade.quantity, 10);
    assert_eq!(trade.buy_order_id, "buy1");
    assert_eq!(trade.sell_order_id, "sell1");
    // The order book should be empty now.
    assert!(engine.get_orders(OrderType::Buy).is_empty());
    assert!(engine.get_orders(OrderType::Sell).is_empty());
}

#[test]
fn test_partial_fill() {
    let mut engine = DexEngine::new();
    // Buy order has a larger quantity than the sell order.
    let buy_order = create_order("buy2", OrderType::Buy, 1500, 20);
    let sell_order = create_order("sell2", OrderType::Sell, 1500, 5);
    engine.submit_order(buy_order);
    engine.submit_order(sell_order);
    engine.match_orders();
    let trades = engine.get_trades();
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.quantity, 5);
    // The remaining buy order should have 15 left.
    let remaining_buy = engine.get_orders(OrderType::Buy);
    assert_eq!(remaining_buy.len(), 1);
    assert_eq!(remaining_buy[0].quantity, 15);
    // No sell orders should remain.
    assert!(engine.get_orders(OrderType::Sell).is_empty());
}

#[test]
fn test_multiple_matches() {
    let mut engine = DexEngine::new();
    // Create multiple sell orders for one buy order.
    let buy_order = create_order("buy3", OrderType::Buy, 2000, 30);
    let sell_order1 = create_order("sell3a", OrderType::Sell, 2000, 10);
    let sell_order2 = create_order("sell3b", OrderType::Sell, 2000, 15);
    let sell_order3 = create_order("sell3c", OrderType::Sell, 2000, 10);
    // Submit sell orders first to enforce FIFO order.
    engine.submit_order(sell_order1);
    engine.submit_order(sell_order2);
    engine.submit_order(sell_order3);
    engine.submit_order(buy_order);
    engine.match_orders();
    let trades = engine.get_trades();
    // Expected: Three trades (10 + 15 + 5 = 30) with one sell order partially filled.
    assert_eq!(trades.len(), 3);
    let total_traded: u64 = trades.iter().map(|t| t.quantity).sum();
    assert_eq!(total_traded, 30);
    // The remaining sell order should have a quantity of 5.
    let remaining_sells = engine.get_orders(OrderType::Sell);
    assert_eq!(remaining_sells.len(), 1);
    assert_eq!(remaining_sells[0].order_id, "sell3c");
    assert_eq!(remaining_sells[0].quantity, 5);
}

#[test]
fn test_order_cancellation() {
    let mut engine = DexEngine::new();
    let order = create_order("cancel1", OrderType::Buy, 1200, 10);
    engine.submit_order(order);
    let orders_before = engine.get_orders(OrderType::Buy);
    assert_eq!(orders_before.len(), 1);
    // Cancel the order.
    let cancelled = engine.cancel_order("cancel1");
    assert!(cancelled);
    let orders_after = engine.get_orders(OrderType::Buy);
    assert!(orders_after.is_empty());
    // Attempting to cancel a non-existent order should return false.
    let cancelled_again = engine.cancel_order("nonexistent");
    assert!(!cancelled_again);
}

#[test]
fn test_concurrent_order_submission() {
    let engine = Arc::new(Mutex::new(DexEngine::new()));
    let num_threads = 10;
    let orders_per_thread = 100;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::new();

    for i in 0..num_threads {
        let engine_clone = Arc::clone(&engine);
        let barrier_clone = Arc::clone(&barrier);
        let handle = thread::spawn(move || {
            // Wait until all threads are ready.
            barrier_clone.wait();
            for j in 0..orders_per_thread {
                let order_id = format!("thread{}_order{}", i, j);
                let order = create_order(&order_id, OrderType::Buy, 1000 + (j % 10) as u32, 10);
                engine_clone.lock().unwrap().submit_order(order);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let engine_locked = engine.lock().unwrap();
    let all_buys = engine_locked.get_orders(OrderType::Buy);
    assert_eq!(all_buys.len(), num_threads * orders_per_thread);
}

#[test]
fn test_persistence() {
    let mut engine = DexEngine::new();
    // Submit a matching pair of orders.
    let buy_order = create_order("persist_buy", OrderType::Buy, 2500, 15);
    let sell_order = create_order("persist_sell", OrderType::Sell, 2500, 15);
    engine.submit_order(buy_order);
    engine.submit_order(sell_order);
    engine.match_orders();
    // Persist the current state to disk.
    let persist_result = engine.persist("test_persistence_state.json");
    assert!(persist_result.is_ok());
    // Load a new engine instance from the persisted state.
    let loaded_engine = DexEngine::load("test_persistence_state.json");
    assert!(loaded_engine.is_ok());
    let loaded_engine = loaded_engine.unwrap();
    let trades = loaded_engine.get_trades();
    assert_eq!(trades.len(), 1);
    let trade = &trades[0];
    assert_eq!(trade.price, 2500);
    assert_eq!(trade.quantity, 15);
    // Clean up the test persistence file.
    let cleanup = std::fs::remove_file("test_persistence_state.json");
    assert!(cleanup.is_ok());
}