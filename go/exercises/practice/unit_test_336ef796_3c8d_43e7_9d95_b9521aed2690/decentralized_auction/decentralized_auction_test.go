package decentralized_auction

import (
	"testing"
)

func TestCreateAuction(t *testing.T) {
	tests := []struct {
		name         string
		auctionID   string
		nftID       string
		startPrice  int
		duration    int
		creator     string
		curBlock    int
		expectError bool
	}{
		{
			name:         "Valid auction creation",
			auctionID:   "auction1",
			nftID:       "nft1",
			startPrice:  100,
			duration:    10,
			creator:     "creator1",
			curBlock:    1,
			expectError: false,
		},
		{
			name:         "Duplicate auction ID",
			auctionID:   "auction1",
			nftID:       "nft2",
			startPrice:  200,
			duration:    10,
			creator:     "creator2",
			curBlock:    1,
			expectError: true,
		},
		{
			name:         "Invalid starting price",
			auctionID:   "auction2",
			nftID:       "nft2",
			startPrice:  -100,
			duration:    10,
			creator:     "creator1",
			curBlock:    1,
			expectError: true,
		},
		{
			name:         "Invalid duration",
			auctionID:   "auction3",
			nftID:       "nft3",
			startPrice:  100,
			duration:    0,
			creator:     "creator1",
			curBlock:    1,
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := CreateAuction(tt.auctionID, tt.nftID, tt.startPrice, tt.duration, tt.creator, tt.curBlock)
			if (err != nil) != tt.expectError {
				t.Errorf("CreateAuction() error = %v, expectError %v", err, tt.expectError)
			}
		})
	}
}

func TestPlaceBid(t *testing.T) {
	// Setup initial auction
	CreateAuction("test_auction", "test_nft", 100, 10, "creator1", 1)

	tests := []struct {
		name         string
		auctionID   string
		bidder      string
		amount      int
		curBlock    int
		expectError bool
	}{
		{
			name:         "Valid bid",
			auctionID:   "test_auction",
			bidder:      "bidder1",
			amount:      150,
			curBlock:    2,
			expectError: false,
		},
		{
			name:         "Bid too low",
			auctionID:   "test_auction",
			bidder:      "bidder2",
			amount:      120,
			curBlock:    3,
			expectError: true,
		},
		{
			name:         "Non-existent auction",
			auctionID:   "fake_auction",
			bidder:      "bidder1",
			amount:      200,
			curBlock:    4,
			expectError: true,
		},
		{
			name:         "Auction ended",
			auctionID:   "test_auction",
			bidder:      "bidder3",
			amount:      300,
			curBlock:    12,
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := PlaceBid(tt.auctionID, tt.bidder, tt.amount, tt.curBlock)
			if (err != nil) != tt.expectError {
				t.Errorf("PlaceBid() error = %v, expectError %v", err, tt.expectError)
			}
		})
	}
}

func TestEndAuction(t *testing.T) {
	// Setup test cases
	CreateAuction("auction_end_test", "nft_end_test", 100, 10, "creator1", 1)
	PlaceBid("auction_end_test", "bidder1", 150, 2)
	PlaceBid("auction_end_test", "bidder2", 200, 3)

	tests := []struct {
		name          string
		auctionID    string
		curBlock     int
		expectWinner string
		expectAmount int
		expectError  bool
	}{
		{
			name:          "Auction not yet ended",
			auctionID:    "auction_end_test",
			curBlock:     5,
			expectWinner: "",
			expectAmount: 0,
			expectError:  true,
		},
		{
			name:          "Successfully end auction",
			auctionID:    "auction_end_test",
			curBlock:     12,
			expectWinner: "bidder2",
			expectAmount: 200,
			expectError:  false,
		},
		{
			name:          "Non-existent auction",
			auctionID:    "fake_auction",
			curBlock:     12,
			expectWinner: "",
			expectAmount: 0,
			expectError:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			winner, amount, err := EndAuction(tt.auctionID, tt.curBlock)
			if (err != nil) != tt.expectError {
				t.Errorf("EndAuction() error = %v, expectError %v", err, tt.expectError)
			}
			if winner != tt.expectWinner {
				t.Errorf("EndAuction() winner = %v, want %v", winner, tt.expectWinner)
			}
			if amount != tt.expectAmount {
				t.Errorf("EndAuction() amount = %v, want %v", amount, tt.expectAmount)
			}
		})
	}
}

func TestGetNFTOwner(t *testing.T) {
	// Setup test cases
	CreateAuction("nft_owner_test", "test_nft_ownership", 100, 10, "creator1", 1)
	PlaceBid("nft_owner_test", "bidder1", 150, 2)
	EndAuction("nft_owner_test", 12)

	tests := []struct {
		name         string
		nftID       string
		expectOwner string
	}{
		{
			name:         "Check transferred NFT ownership",
			nftID:       "test_nft_ownership",
			expectOwner: "bidder1",
		},
		{
			name:         "Non-existent NFT",
			nftID:       "fake_nft",
			expectOwner: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			owner := GetNFTOwner(tt.nftID)
			if owner != tt.expectOwner {
				t.Errorf("GetNFTOwner() = %v, want %v", owner, tt.expectOwner)
			}
		})
	}
}