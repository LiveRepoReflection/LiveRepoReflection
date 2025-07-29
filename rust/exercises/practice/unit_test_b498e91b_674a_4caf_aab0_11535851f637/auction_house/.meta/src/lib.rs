use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub enum AuctionError {
    InvalidListing,
    AuctionNotFound,
    AuctionEnded,
    BidTooLow,
    AuctionNotActive,
    AlreadyCancelled,
    CancelNotAllowed,
    RefundError,
}

#[derive(Debug, PartialEq)]
pub enum AuctionResult {
    Won { item_id: String, winner: String, bid_amount: u64 },
    NoBids { item_id: String },
}

#[derive(Clone, Debug)]
struct Bid {
    bidder: String,
    amount: u64,
    bid_block: u64,
}

#[derive(Clone, Debug)]
struct Auction {
    item_id: String,
    seller: String,
    starting_price: u64,
    min_increment: u64,
    duration: u64,
    listed_block: u64,
    bids: Vec<Bid>,
    is_cancelled: bool,
}

impl Auction {
    fn new(item_id: &str, starting_price: u64, min_increment: u64, duration: u64, seller: &str, listed_block: u64) -> Self {
        Auction {
            item_id: item_id.to_string(),
            seller: seller.to_string(),
            starting_price,
            min_increment,
            duration,
            listed_block,
            bids: Vec::new(),
            is_cancelled: false,
        }
    }
    
    fn current_highest_bid(&self) -> Option<&Bid> {
        self.bids.last()
    }
}

pub struct AuctionHouse {
    // Active auctions mapped by item_id.
    auctions: HashMap<String, Auction>,
    // Finished auctions for refund purposes.
    finished: HashMap<String, Auction>,
}

impl AuctionHouse {
    pub fn new() -> Self {
        AuctionHouse {
            auctions: HashMap::new(),
            finished: HashMap::new(),
        }
    }

    pub fn list_item(&mut self, item_id: &str, starting_price: u64, min_increment: u64, duration: u64, seller: &str) -> Result<(), AuctionError> {
        if starting_price == 0 || duration == 0 {
            return Err(AuctionError::InvalidListing);
        }
        // For simplicity, we assume the listing block to be 0.
        if self.auctions.contains_key(item_id) || self.finished.contains_key(item_id) {
            return Err(AuctionError::InvalidListing);
        }
        let auction = Auction::new(item_id, starting_price, min_increment, duration, seller, 0);
        self.auctions.insert(item_id.to_string(), auction);
        Ok(())
    }

    pub fn place_bid(&mut self, item_id: &str, bidder: &str, bid_amount: u64, current_block: u64) -> Result<(), AuctionError> {
        let auction = self.auctions.get_mut(item_id);
        if auction.is_none() {
            return Err(AuctionError::AuctionNotFound);
        }
        let auction = auction.unwrap();
        if auction.is_cancelled {
            return Err(AuctionError::AuctionNotActive);
        }
        // Check if auction has already ended.
        if current_block >= auction.listed_block + auction.duration {
            return Err(AuctionError::AuctionEnded);
        }
        // Validate bid amount.
        if auction.bids.is_empty() {
            if bid_amount < auction.starting_price {
                return Err(AuctionError::BidTooLow);
            }
        } else {
            let highest_bid = auction.current_highest_bid().unwrap();
            if bid_amount < highest_bid.amount + auction.min_increment {
                return Err(AuctionError::BidTooLow);
            }
        }
        let bid = Bid {
            bidder: bidder.to_string(),
            amount: bid_amount,
            bid_block: current_block,
        };
        auction.bids.push(bid);
        Ok(())
    }

    pub fn settle(&mut self, item_id: &str, current_block: u64) -> Result<AuctionResult, AuctionError> {
        let auction = self.auctions.remove(item_id);
        if auction.is_none() {
            return Err(AuctionError::AuctionNotFound);
        }
        let auction = auction.unwrap();
        if current_block < auction.listed_block + auction.duration {
            // Put the auction back since it is not ready to be settled.
            self.auctions.insert(item_id.to_string(), auction);
            return Err(AuctionError::AuctionNotActive);
        }
        // Move auction to finished mapping.
        self.finished.insert(item_id.to_string(), auction.clone());
        if auction.bids.is_empty() {
            return Ok(AuctionResult::NoBids { item_id: item_id.to_string() });
        } else {
            let highest_bid = auction.current_highest_bid().unwrap();
            return Ok(AuctionResult::Won {
                item_id: item_id.to_string(),
                winner: highest_bid.bidder.clone(),
                bid_amount: highest_bid.amount,
            });
        }
    }

    pub fn cancel_auction(&mut self, item_id: &str, seller: &str) -> Result<(), AuctionError> {
        let auction = self.auctions.get_mut(item_id);
        if auction.is_none() {
            return Err(AuctionError::AuctionNotFound);
        }
        let auction = auction.unwrap();
        if auction.seller != seller {
            return Err(AuctionError::CancelNotAllowed);
        }
        if !auction.bids.is_empty() {
            return Err(AuctionError::CancelNotAllowed);
        }
        if auction.is_cancelled {
            return Err(AuctionError::AlreadyCancelled);
        }
        auction.is_cancelled = true;
        Ok(())
    }

    pub fn refund_bid(&mut self, item_id: &str, bidder: &str) -> Result<u64, AuctionError> {
        let auction = self.finished.get(item_id);
        if auction.is_none() {
            return Err(AuctionError::AuctionNotFound);
        }
        let auction = auction.unwrap();
        if auction.bids.is_empty() {
            return Err(AuctionError::RefundError);
        }
        let highest_bid = auction.current_highest_bid().unwrap();
        if highest_bid.bidder == bidder {
            return Err(AuctionError::RefundError);
        }
        // Find the latest bid from the bidder.
        let mut refund_amount: Option<u64> = None;
        for bid in auction.bids.iter().rev() {
            if bid.bidder == bidder {
                refund_amount = Some(bid.amount);
                break;
            }
        }
        if let Some(amount) = refund_amount {
            Ok(amount)
        } else {
            Err(AuctionError::RefundError)
        }
    }
}