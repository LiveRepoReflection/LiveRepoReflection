use dex_orderbook::{OrderBook, Order};

#[test]
fn test_add_and_query_quantity() {
    let mut ob = OrderBook::new();
    // Add a buy order and a sell order at the same price level.
    let res1 = ob.add_order("order1".to_string(), 100, 10, "buy".to_string(), 1);
    assert!(res1.is_ok());
    let res2 = ob.add_order("order2".to_string(), 100, 5, "sell".to_string(), 2);
    assert!(res2.is_ok());
    
    // Query the quantity at price 100.
    let qty_result = ob.get_quantity_at_price(100);
    assert!(qty_result.is_ok());
    let (buy_qty, sell_qty) = qty_result.unwrap();
    assert_eq!(buy_qty, 10);
    assert_eq!(sell_qty, 5);
}

#[test]
fn test_cancel_order() {
    let mut ob = OrderBook::new();
    // Add two buy orders.
    assert!(ob.add_order("order1".to_string(), 101, 10, "buy".to_string(), 1).is_ok());
    assert!(ob.add_order("order2".to_string(), 101, 15, "buy".to_string(), 2).is_ok());
    
    // Cancel one order.
    let cancel_res = ob.cancel_order("order1".to_string());
    assert!(cancel_res.is_ok());
    
    // Verify the quantity at price 101 reflects the cancellation.
    let qty_result = ob.get_quantity_at_price(101);
    assert!(qty_result.is_ok());
    let (buy_qty, sell_qty) = qty_result.unwrap();
    assert_eq!(buy_qty, 15);
    assert_eq!(sell_qty, 0);
}

#[test]
fn test_get_recent_orders() {
    let mut ob = OrderBook::new();
    // Add multiple orders with increasing timestamps.
    assert!(ob.add_order("order1".to_string(), 102, 10, "buy".to_string(), 1).is_ok());
    assert!(ob.add_order("order2".to_string(), 103, 20, "sell".to_string(), 2).is_ok());
    assert!(ob.add_order("order3".to_string(), 104, 30, "buy".to_string(), 3).is_ok());
    assert!(ob.add_order("order4".to_string(), 105, 40, "sell".to_string(), 4).is_ok());
    assert!(ob.add_order("order5".to_string(), 106, 50, "buy".to_string(), 5).is_ok());
    assert!(ob.add_order("order6".to_string(), 107, 60, "sell".to_string(), 6).is_ok());
    
    // Retrieve the 2 most recent orders for each type.
    let recent_result = ob.get_recent_orders(2);
    assert!(recent_result.is_ok());
    let (recent_buys, recent_sells) = recent_result.unwrap();

    // Expect recent buys to be orders with timestamps 5 and 3.
    assert_eq!(recent_buys.len(), 2);
    assert_eq!(recent_buys[0].order_id, "order5");
    assert_eq!(recent_buys[1].order_id, "order3");
    
    // Expect recent sells to be orders with timestamps 6 and 4.
    assert_eq!(recent_sells.len(), 2);
    assert_eq!(recent_sells[0].order_id, "order6");
    assert_eq!(recent_sells[1].order_id, "order4");
}

#[test]
fn test_get_weighted_average_price() {
    let mut ob = OrderBook::new();
    // Add buy orders within price range 100 to 105.
    assert!(ob.add_order("order1".to_string(), 100, 10, "buy".to_string(), 1).is_ok());
    assert!(ob.add_order("order2".to_string(), 105, 20, "buy".to_string(), 2).is_ok());
    
    // Add sell orders within price range 100 to 105.
    assert!(ob.add_order("order3".to_string(), 100, 5, "sell".to_string(), 3).is_ok());
    assert!(ob.add_order("order4".to_string(), 105, 15, "sell".to_string(), 4).is_ok());
    
    // Calculate the volume weighted average price within the price range.
    let wap_result = ob.get_weighted_average_price(100, 105);
    assert!(wap_result.is_ok());
    let (buy_wap, sell_wap) = wap_result.unwrap();
    
    // Expected weighted average for buy orders: (100*10 + 105*20) / (10+20).
    let expected_buy = (100 * 10 + 105 * 20) as f64 / 30.0;
    // Expected weighted average for sell orders: (100*5 + 105*15) / (5+15).
    let expected_sell = (100 * 5 + 105 * 15) as f64 / 20.0;
    
    assert!((buy_wap - expected_buy).abs() < 1e-5);
    assert!((sell_wap - expected_sell).abs() < 1e-5);
}

#[test]
fn test_no_orders_in_range() {
    let mut ob = OrderBook::new();
    // Without any orders, weighted average should be 0.0.
    let wap_result = ob.get_weighted_average_price(50, 60);
    assert!(wap_result.is_ok());
    let (buy_wap, sell_wap) = wap_result.unwrap();
    assert_eq!(buy_wap, 0.0);
    assert_eq!(sell_wap, 0.0);
}

#[test]
fn test_cancel_nonexistent_order() {
    let mut ob = OrderBook::new();
    // Attempt to cancel an order that has not been added.
    let result = ob.cancel_order("nonexistent".to_string());
    assert!(result.is_err());
}

#[test]
fn test_duplicate_order_id() {
    let mut ob = OrderBook::new();
    // Add an order.
    assert!(ob.add_order("order1".to_string(), 110, 10, "buy".to_string(), 1).is_ok());
    // Attempt to add another order with the same ID.
    let duplicate = ob.add_order("order1".to_string(), 110, 15, "sell".to_string(), 2);
    assert!(duplicate.is_err());
}

#[test]
fn test_get_recent_orders_empty() {
    let mut ob = OrderBook::new();
    // When no orders have been added, recent orders should be empty.
    let recent_result = ob.get_recent_orders(5);
    assert!(recent_result.is_ok());
    let (recent_buys, recent_sells) = recent_result.unwrap();
    assert!(recent_buys.is_empty());
    assert!(recent_sells.is_empty());
}

#[test]
fn test_get_quantity_no_orders() {
    let mut ob = OrderBook::new();
    // Query a price level with no orders.
    let result = ob.get_quantity_at_price(999);
    assert!(result.is_err());
}