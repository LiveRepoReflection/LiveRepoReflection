package decentralized_auction

import (
	"errors"
	"sync"
)

// Auction represents an NFT auction
type Auction struct {
	ID           string
	NFTID        string
	StartPrice   int
	Duration     int
	Creator      string
	StartBlock   int
	HighestBid   int
	HighestBidder string
	Ended        bool
	mu           sync.RWMutex
}

// NFTOwnership tracks the current owner of each NFT
type NFTOwnership struct {
	Owner string
	mu    sync.RWMutex
}

var (
	auctions = make(map[string]*Auction)
	nftOwners = make(map[string]*NFTOwnership)
	globalMu sync.RWMutex

	// Error definitions
	ErrAuctionExists      = errors.New("auction already exists")
	ErrInvalidPrice      = errors.New("invalid starting price")
	ErrInvalidDuration   = errors.New("invalid duration")
	ErrAuctionNotFound   = errors.New("auction not found")
	ErrAuctionEnded      = errors.New("auction has ended")
	ErrBidTooLow        = errors.New("bid amount too low")
	ErrAuctionNotEnded   = errors.New("auction has not ended yet")
	ErrInvalidAuctionState = errors.New("invalid auction state")
)

// CreateAuction creates a new NFT auction
func CreateAuction(auctionID string, nftID string, startingPrice int, duration int, creator string, currentBlock int) error {
	if startingPrice <= 0 {
		return ErrInvalidPrice
	}
	if duration <= 0 {
		return ErrInvalidDuration
	}

	globalMu.Lock()
	defer globalMu.Unlock()

	// Check if auction already exists
	if _, exists := auctions[auctionID]; exists {
		return ErrAuctionExists
	}

	// Create new auction
	auction := &Auction{
		ID:         auctionID,
		NFTID:      nftID,
		StartPrice: startingPrice,
		Duration:   duration,
		Creator:    creator,
		StartBlock: currentBlock,
	}

	// Initialize NFT ownership if not exists
	if _, exists := nftOwners[nftID]; !exists {
		nftOwners[nftID] = &NFTOwnership{Owner: creator}
	}

	auctions[auctionID] = auction
	return nil
}

// PlaceBid places a bid on an auction
func PlaceBid(auctionID string, bidder string, bidAmount int, currentBlock int) error {
	globalMu.RLock()
	auction, exists := auctions[auctionID]
	globalMu.RUnlock()

	if !exists {
		return ErrAuctionNotFound
	}

	auction.mu.Lock()
	defer auction.mu.Unlock()

	// Check if auction has ended
	if auction.Ended || currentBlock >= auction.StartBlock+auction.Duration {
		return ErrAuctionEnded
	}

	// Check if bid is high enough
	if bidAmount <= auction.StartPrice || (auction.HighestBid > 0 && bidAmount <= auction.HighestBid) {
		return ErrBidTooLow
	}

	// Update highest bid
	auction.HighestBid = bidAmount
	auction.HighestBidder = bidder

	return nil
}

// EndAuction ends an auction and transfers the NFT to the winner
func EndAuction(auctionID string, currentBlock int) (string, int, error) {
	globalMu.Lock()
	defer globalMu.Unlock()

	auction, exists := auctions[auctionID]
	if !exists {
		return "", 0, ErrAuctionNotFound
	}

	auction.mu.Lock()
	defer auction.mu.Unlock()

	// Check if auction can be ended
	if auction.Ended {
		return "", 0, ErrInvalidAuctionState
	}

	if currentBlock < auction.StartBlock+auction.Duration {
		return "", 0, ErrAuctionNotEnded
	}

	// Mark auction as ended
	auction.Ended = true

	// If no bids were placed, return empty result
	if auction.HighestBidder == "" {
		return "", 0, nil
	}

	// Transfer NFT ownership
	nftOwnership, exists := nftOwners[auction.NFTID]
	if !exists {
		nftOwners[auction.NFTID] = &NFTOwnership{Owner: auction.HighestBidder}
	} else {
		nftOwnership.mu.Lock()
		nftOwnership.Owner = auction.HighestBidder
		nftOwnership.mu.Unlock()
	}

	return auction.HighestBidder, auction.HighestBid, nil
}

// GetNFTOwner returns the current owner of an NFT
func GetNFTOwner(nftID string) string {
	globalMu.RLock()
	defer globalMu.RUnlock()

	nftOwnership, exists := nftOwners[nftID]
	if !exists {
		return ""
	}

	nftOwnership.mu.RLock()
	defer nftOwnership.mu.RUnlock()
	
	return nftOwnership.Owner
}