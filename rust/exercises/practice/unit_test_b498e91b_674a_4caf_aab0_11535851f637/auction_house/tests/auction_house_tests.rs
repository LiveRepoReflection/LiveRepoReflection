use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Duration;

use auction_house::{AuctionError, AuctionHouse, AuctionResult};

fn setup_auction_house() -> AuctionHouse {
    // Create a new instance of AuctionHouse.
    AuctionHouse::new()
}

#[test]
fn test_list_item_valid() {
    let mut ah = setup_auction_house();
    let res = ah.list_item("item1", 100, 10, 5, "seller1");
    assert!(res.is_ok(), "Listing a valid item should succeed");
}

#[test]
fn test_list_item_invalid() {
    let mut ah = setup_auction_house();
    // Invalid if starting price is zero.
    let res = ah.list_item("item_invalid", 0, 10, 5, "seller1");
    assert!(res.is_err(), "Listing with zero starting price should return an error");

    // Invalid if duration is zero.
    let res = ah.list_item("item_invalid2", 100, 10, 0, "seller1");
    assert!(res.is_err(), "Listing with zero duration should return an error");
}

#[test]
fn test_place_bid_below_min_increment() {
    let mut ah = setup_auction_house();
    // List an auction
    let _ = ah.list_item("item2", 100, 20, 10, "seller2");
    // First valid bid
    let res = ah.place_bid("item2", "bidder1", 100, 1);
    assert!(res.is_ok(), "Initial bid equal to starting price should be allowed");
    // Bid below the required minimum increment
    let res = ah.place_bid("item2", "bidder2", 110, 2);
    assert!(res.is_err(), "Bid below the minimum increment should return an error");
}

#[test]
fn test_place_bid_on_nonexistent_item() {
    let mut ah = setup_auction_house();
    let res = ah.place_bid("nonexistent", "bidder", 150, 1);
    assert!(res.is_err(), "Bidding on a non-existent auction should return an error");
}

#[test]
fn test_settle_before_duration() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item3", 200, 20, 5, "seller3");
    let _ = ah.place_bid("item3", "bidder1", 200, 1);
    // Try to settle before the auction's duration has elapsed.
    let res = ah.settle("item3", 4);
    assert!(res.is_err(), "Settlement before auction duration should return an error");
}

#[test]
fn test_settle_success() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item4", 300, 30, 5, "seller4");
    let _ = ah.place_bid("item4", "bidder1", 300, 1);
    let _ = ah.place_bid("item4", "bidder2", 330, 2);
    // Settle auction after duration is reached.
    let res = ah.settle("item4", 6);
    assert!(res.is_ok(), "Settlement after auction duration should succeed");
    let result = res.unwrap();
    match result {
        AuctionResult::Won { item_id, winner, bid_amount } => {
            assert_eq!(item_id, "item4");
            assert_eq!(winner, "bidder2");
            assert_eq!(bid_amount, 330);
        },
        _ => panic!("AuctionResult should indicate a winner"),
    }
}

#[test]
fn test_bid_after_auction_expires() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item5", 100, 10, 3, "seller5");
    let _ = ah.place_bid("item5", "bidder1", 100, 1);
    // Simulate auction expiry by using a block number past duration.
    let res = ah.place_bid("item5", "bidder2", 120, 4);
    assert!(res.is_err(), "Bidding after auction expiry should return an error");
}

#[test]
fn test_concurrent_bidding() {
    let ah = Arc::new(parking_lot::RwLock::new(setup_auction_house()));
    // List an auction
    {
        let mut ahw = ah.write();
        let res = ahw.list_item("item6", 500, 50, 10, "seller6");
        assert!(res.is_ok(), "Listing item6 should succeed");
    }

    let num_threads = 10;
    let barrier = Arc::new(Barrier::new(num_threads));
    let mut handles = Vec::new();

    for i in 0..num_threads {
        let ah_clone = Arc::clone(&ah);
        let barrier_clone = Arc::clone(&barrier);
        let handle = thread::spawn(move || {
            // Ensure all threads start bidding at the same time.
            barrier_clone.wait();
            let bidder = format!("bidder_{}", i);
            // Each thread tries to bid an increment: initial bid is 500, so bid = 500 + 50 * (i+1)
            let bid_price = 500 + 50 * (i + 1) as u64;
            // Using a fixed current_block within auction duration.
            let res = {
                let mut ahw = ah_clone.write();
                ahw.place_bid("item6", &bidder, bid_price, 5)
            };
            res
        });
        handles.push(handle);
    }

    // Wait for all threads
    for handle in handles {
        let res = handle.join();
        assert!(res.is_ok(), "Thread bidding resulted in error: {:?}", res);
    }

    // Settle the auction after the duration.
    let settle_res = {
        let mut ahw = ah.write();
        ahw.settle("item6", 11)
    };
    assert!(settle_res.is_ok(), "Settlement should succeed after auction ends");
    let result = settle_res.unwrap();
    match result {
        AuctionResult::Won { item_id, winner, bid_amount } => {
            assert_eq!(item_id, "item6", "Settled auction item id should match");
            // The highest bidder should be the one with the highest bid value.
            assert_eq!(bid_amount, 500 + 50 * num_threads as u64, "Highest bid amount is incorrect");
        },
        _ => panic!("AuctionResult should indicate a winner for concurrent bidding"),
    }
}

#[test]
fn test_cancel_auction_before_bid() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item7", 400, 40, 10, "seller7");
    // Attempt to cancel by seller.
    let res = ah.cancel_auction("item7", "seller7");
    assert!(res.is_ok(), "Seller should be able to cancel auction with no bids");

    // Listing cancelled auction should no longer accept bids.
    let bid_res = ah.place_bid("item7", "bidder1", 400, 1);
    assert!(bid_res.is_err(), "Bidding on a cancelled auction should return error");
}

#[test]
fn test_cancel_auction_after_bid() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item8", 600, 60, 10, "seller8");
    let _ = ah.place_bid("item8", "bidder1", 600, 1);
    // Attempt to cancel by seller after a bid has been placed.
    let res = ah.cancel_auction("item8", "seller8");
    assert!(res.is_err(), "Auction with bids should not be cancelable");
}

#[test]
fn test_refund_losing_bid() {
    let mut ah = setup_auction_house();
    let _ = ah.list_item("item9", 700, 70, 10, "seller9");
    let _ = ah.place_bid("item9", "bidder1", 700, 1);
    let _ = ah.place_bid("item9", "bidder2", 770, 2);
    let _ = ah.place_bid("item9", "bidder3", 840, 3);
    // Settle the auction.
    let res = ah.settle("item9", 11);
    assert!(res.is_ok(), "Settlement should succeed");
    // After settlement, refund the losing bids.
    let refund_bidder1 = ah.refund_bid("item9", "bidder1");
    let refund_bidder2 = ah.refund_bid("item9", "bidder2");
    // The highest bidder should not get a refund.
    let refund_bidder3 = ah.refund_bid("item9", "bidder3");

    assert!(refund_bidder1.is_ok(), "Losing bidder1 should be refunded");
    assert!(refund_bidder2.is_ok(), "Losing bidder2 should be refunded");
    assert!(refund_bidder3.is_err(), "Winning bidder3 should not be allowed a refund");
}