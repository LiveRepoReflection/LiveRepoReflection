use std::sync::{Arc, Mutex};
use std::thread;

use dex_aggregator::{DexAggregator, Order, OrderBook, Side, TradePlan};

#[test]
fn test_order_book_aggregation() {
    // Setup aggregator and two DEX order books
    let mut aggregator = DexAggregator::new();

    // DEX 1 order book
    let dex1_order_book = OrderBook {
        bids: vec![Order { side: Side::Bid, price: 100, quantity: 5 }],
        asks: vec![Order { side: Side::Ask, price: 105, quantity: 5 }],
    };

    // DEX 2 order book
    let dex2_order_book = OrderBook {
        bids: vec![Order { side: Side::Bid, price: 99, quantity: 10 }],
        asks: vec![Order { side: Side::Ask, price: 104, quantity: 10 }],
    };

    aggregator.update_order_book("dex1".to_string(), dex1_order_book);
    aggregator.update_order_book("dex2".to_string(), dex2_order_book);

    // Aggregate order books
    let aggregated = aggregator.aggregate_order_books();
    // Expectations:
    // Bids sorted descending: [100, 99]
    // Asks sorted ascending: [104, 105]
    assert!(!aggregated.bids.is_empty());
    assert!(!aggregated.asks.is_empty());
    assert_eq!(aggregated.bids[0].price, 100);
    assert_eq!(aggregated.bids[1].price, 99);
    assert_eq!(aggregated.asks[0].price, 104);
    assert_eq!(aggregated.asks[1].price, 105);
}

#[test]
fn test_optimal_order_routing() {
    let mut aggregator = DexAggregator::new();

    // Setup DEX order books with ask liquidity for a buy order.
    let dex1_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 105, quantity: 5 },
        ],
    };

    let dex2_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 104, quantity: 10 },
        ],
    };

    aggregator.update_order_book("dex1".to_string(), dex1_order_book);
    aggregator.update_order_book("dex2".to_string(), dex2_order_book);

    // Place a buy order for quantity 12 with a generous slippage tolerance.
    let buy_order = Order { side: Side::Ask, price: 0, quantity: 12 };
    let slippage_tolerance = 0.05; // 5% tolerance

    let trade_plan_result = aggregator.route_order(buy_order, slippage_tolerance);
    assert!(trade_plan_result.is_ok());
    let plan: TradePlan = trade_plan_result.unwrap();

    // Expected plan: Use 10 units from dex2 at price 104 and 2 units from dex1 at price 105.
    // Total planned quantity should be 12.
    let mut total_qty = 0;
    for (_, qty, _) in &plan.instructions {
        total_qty += qty;
    }
    assert_eq!(total_qty, 12);

    // Verify that the instructions follow the order of lower price first, then next.
    // First instruction should be from dex2.
    if let Some((dex_id, qty, price)) = plan.instructions.first() {
        assert_eq!(dex_id, "dex2");
        assert_eq!(*price, 104);
    } else {
        panic!("Expected at least one trade instruction");
    }
}

#[test]
fn test_slippage_control() {
    let mut aggregator = DexAggregator::new();

    // Setup DEX order books where liquidity is sparse or priced too high.
    let dex_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 150, quantity: 5 },
            Order { side: Side::Ask, price: 160, quantity: 5 },
        ],
    };

    aggregator.update_order_book("dex1".to_string(), dex_order_book);

    // Place a buy order for quantity 8 with a very tight slippage tolerance.
    let buy_order = Order { side: Side::Ask, price: 0, quantity: 8 };
    let slippage_tolerance = 0.01; // 1% tolerance, too strict for available liquidity

    let trade_plan_result = aggregator.route_order(buy_order, slippage_tolerance);
    // Since slippage tolerance is exceeded, expect an error.
    assert!(trade_plan_result.is_err());
}

#[test]
fn test_dex_failure_handling() {
    let mut aggregator = DexAggregator::new();

    // Setup two DEX order books.
    let dex1_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 104, quantity: 10 },
        ],
    };

    let dex2_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 105, quantity: 5 },
        ],
    };

    aggregator.update_order_book("dex1".to_string(), dex1_order_book);
    aggregator.update_order_book("dex2".to_string(), dex2_order_book);

    // Simulate dex2 failure by removing its order book.
    aggregator.remove_order_book("dex2");

    // Place a buy order for quantity 8.
    let buy_order = Order { side: Side::Ask, price: 0, quantity: 8 };
    let slippage_tolerance = 0.1; // 10% tolerance

    let trade_plan_result = aggregator.route_order(buy_order, slippage_tolerance);
    assert!(trade_plan_result.is_ok());
    let plan = trade_plan_result.unwrap();

    // All instructions must come from dex1.
    for (dex_id, _, _) in plan.instructions.iter() {
        assert_eq!(dex_id, "dex1");
    }
}

#[test]
fn test_dynamic_fee_adjustment() {
    let mut aggregator = DexAggregator::new();

    // Setup DEX order books.
    let dex1_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 104, quantity: 10 },
        ],
    };

    let dex2_order_book = OrderBook {
        bids: vec![],
        asks: vec![
            Order { side: Side::Ask, price: 104, quantity: 10 },
        ],
    };

    aggregator.update_order_book("dex1".to_string(), dex1_order_book);
    aggregator.update_order_book("dex2".to_string(), dex2_order_book);

    // Set a high fee on dex2.
    aggregator.set_fee("dex2".to_string(), 50); // fee value is arbitrary

    // Place a buy order for quantity 10.
    let buy_order = Order { side: Side::Ask, price: 0, quantity: 10 };
    let slippage_tolerance = 0.1;

    let trade_plan_result = aggregator.route_order(buy_order, slippage_tolerance);
    assert!(trade_plan_result.is_ok());
    let plan = trade_plan_result.unwrap();

    // Expect that the execution avoids dex2 due to high fee.
    for (dex_id, _, _) in plan.instructions.iter() {
        assert_eq!(dex_id, "dex1");
    }
}

#[test]
fn test_concurrent_order_requests() {
    // Wrap the aggregator in an Arc<Mutex<>> to allow safe concurrent access.
    let aggregator = Arc::new(Mutex::new(DexAggregator::new()));

    // Setup DEX order books.
    {
        let mut agg = aggregator.lock().unwrap();
        let dex1_order_book = OrderBook {
            bids: vec![],
            asks: vec![
                Order { side: Side::Ask, price: 104, quantity: 20 },
            ],
        };
        let dex2_order_book = OrderBook {
            bids: vec![],
            asks: vec![
                Order { side: Side::Ask, price: 105, quantity: 20 },
            ],
        };

        agg.update_order_book("dex1".to_string(), dex1_order_book);
        agg.update_order_book("dex2".to_string(), dex2_order_book);
    }

    let mut handles = vec![];
    for _ in 0..10 {
        let aggregator_clone = Arc::clone(&aggregator);
        let handle = thread::spawn(move || {
            let buy_order = Order { side: Side::Ask, price: 0, quantity: 15 };
            let slippage_tolerance = 0.1;
            // Lock the aggregator for routing the order.
            let agg = aggregator_clone.lock().unwrap();
            let result = agg.route_order(buy_order, slippage_tolerance);
            result
        });
        handles.push(handle);
    }

    for handle in handles {
        let result = handle.join().unwrap();
        assert!(result.is_ok());
        let plan = result.unwrap();
        let mut total_qty = 0;
        for (_, qty, _) in plan.instructions.iter() {
            total_qty += qty;
        }
        assert_eq!(total_qty, 15);
    }
}