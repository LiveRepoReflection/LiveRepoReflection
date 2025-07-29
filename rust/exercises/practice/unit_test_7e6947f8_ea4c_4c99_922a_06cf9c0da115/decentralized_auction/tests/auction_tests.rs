use decentralized_auction::{AuctionState, Bid, determine_winners};

#[test]
fn test_no_bids() {
    let auction_state = AuctionState { bids: vec![] };
    let winners = determine_winners(auction_state, 1000, 100);
    assert_eq!(winners, Vec::<String>::new());
}

#[test]
fn test_all_invalid_bids() {
    // All bid timestamps are greater than closing_time + network_latency
    let auction_state = AuctionState {
        bids: vec![
            Bid {
                bidder_id: "A".to_string(),
                amount: 50,
                timestamp: 2000,
            },
            Bid {
                bidder_id: "B".to_string(),
                amount: 100,
                timestamp: 3000,
            },
        ],
    };
    // closing_time + network_latency = 1000 + 500 = 1500, so all bids are invalid.
    let winners = determine_winners(auction_state, 1000, 500);
    assert_eq!(winners, Vec::<String>::new());
}

#[test]
fn test_single_valid_bid() {
    let auction_state = AuctionState {
        bids: vec![Bid {
            bidder_id: "A".to_string(),
            amount: 50,
            timestamp: 1000,
        }],
    };
    let winners = determine_winners(auction_state, 1000, 100);
    assert_eq!(winners, vec!["A".to_string()]);
}

#[test]
fn test_multiple_winners_with_tie() {
    let auction_state = AuctionState {
        bids: vec![
            Bid {
                bidder_id: "A".to_string(),
                amount: 150,
                timestamp: 950,
            },
            Bid {
                bidder_id: "B".to_string(),
                amount: 200,
                timestamp: 1000,
            },
            Bid {
                bidder_id: "C".to_string(),
                amount: 200,
                timestamp: 1050,
            },
            Bid {
                bidder_id: "D".to_string(),
                amount: 190,
                timestamp: 1020,
            },
        ],
    };
    let winners = determine_winners(auction_state, 1000, 100);
    // The highest bid is 200 from bidders B and C.
    let mut sorted_winners = winners;
    sorted_winners.sort();
    assert_eq!(sorted_winners, vec!["B".to_string(), "C".to_string()]);
}

#[test]
fn test_network_latency_inclusion() {
    let auction_state = AuctionState {
        bids: vec![
            Bid {
                bidder_id: "A".to_string(),
                amount: 100,
                timestamp: 1100,
            },
            Bid {
                bidder_id: "B".to_string(),
                amount: 120,
                timestamp: 1200,
            },
            Bid {
                bidder_id: "C".to_string(),
                amount: 110,
                timestamp: 1050,
            },
        ],
    };
    // With closing_time 1000 and network_latency 250, valid bids are those with timestamp <= 1250.
    let winners = determine_winners(auction_state, 1000, 250);
    // The highest bid among valid bids is 120 from bidder B.
    assert_eq!(winners, vec!["B".to_string()]);
}

#[test]
fn test_overflow_handling() {
    // Using closing_time near u64::MAX and network_latency to trigger an overflow.
    let auction_state = AuctionState {
        bids: vec![
            Bid {
                bidder_id: "A".to_string(),
                amount: 300,
                timestamp: 100,
            },
            Bid {
                bidder_id: "B".to_string(),
                amount: 400,
                timestamp: 200,
            },
            Bid {
                bidder_id: "C".to_string(),
                amount: 400,
                timestamp: 300,
            },
        ],
    };
    // The sum of closing_time and network_latency will overflow, so all bids are treated as valid.
    let winners = determine_winners(auction_state, std::u64::MAX - 5, 10);
    let mut sorted_winners = winners;
    sorted_winners.sort();
    // The highest bid is 400 from bidders B and C.
    assert_eq!(sorted_winners, vec!["B".to_string(), "C".to_string()]);
}