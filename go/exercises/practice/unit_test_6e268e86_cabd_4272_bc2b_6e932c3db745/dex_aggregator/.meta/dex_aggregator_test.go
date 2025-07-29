package dex_aggregator

import (
	"sync"
	"testing"
	"time"
)

func TestEmptyAggregator(t *testing.T) {
	agg := NewAggregator("ETH/USDT", 5)
	ob := agg.GetAggregatedBook()
	if len(ob.Bids) != 0 {
		t.Errorf("Expected empty bids, got %v", ob.Bids)
	}
	if len(ob.Asks) != 0 {
		t.Errorf("Expected empty asks, got %v", ob.Asks)
	}
}

func TestAddOrders(t *testing.T) {
	agg := NewAggregator("ETH/USDT", 2)
	// Add bid orders from different DEXs.
	update1 := OrderUpdate{
		DEXID:     "DEX_A",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "bid", Price: 100.0, Quantity: 1.0, OrderID: "A_bid_1"},
		},
	}
	// Higher bid from another DEX.
	update2 := OrderUpdate{
		DEXID:     "DEX_B",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "bid", Price: 101.0, Quantity: 2.0, OrderID: "B_bid_1"},
		},
	}
	// Add ask orders.
	update3 := OrderUpdate{
		DEXID:     "DEX_C",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "ask", Price: 105.0, Quantity: 1.5, OrderID: "C_ask_1"},
		},
	}
	update4 := OrderUpdate{
		DEXID:     "DEX_D",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "ask", Price: 104.0, Quantity: 3.0, OrderID: "D_ask_1"},
		},
	}
	if err := agg.ProcessUpdate(update1); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	if err := agg.ProcessUpdate(update2); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	if err := agg.ProcessUpdate(update3); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	if err := agg.ProcessUpdate(update4); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}

	ob := agg.GetAggregatedBook()
	// Validate bids: best bids should be sorted in descending order.
	if len(ob.Bids) != 2 {
		t.Errorf("Expected 2 bid orders, got %d", len(ob.Bids))
	} else {
		if ob.Bids[0].Price < ob.Bids[1].Price {
			t.Errorf("Bids are not sorted in descending order: %v", ob.Bids)
		}
		// Best bid should be from DEX_B at 101.0.
		if ob.Bids[0].Price != 101.0 {
			t.Errorf("Expected best bid price 101.0, got %v", ob.Bids[0].Price)
		}
	}

	// Validate asks: best asks should be sorted in ascending order.
	if len(ob.Asks) != 2 {
		t.Errorf("Expected 2 ask orders, got %d", len(ob.Asks))
	} else {
		if ob.Asks[0].Price > ob.Asks[1].Price {
			t.Errorf("Asks are not sorted in ascending order: %v", ob.Asks)
		}
		// Best ask should be from DEX_D at 104.0.
		if ob.Asks[0].Price != 104.0 {
			t.Errorf("Expected best ask price 104.0, got %v", ob.Asks[0].Price)
		}
	}
}

func TestModifyOrder(t *testing.T) {
	agg := NewAggregator("ETH/USDT", 3)
	// Add a bid order.
	addUpdate := OrderUpdate{
		DEXID:     "DEX_X",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "bid", Price: 99.0, Quantity: 1.0, OrderID: "X_bid_1"},
		},
	}
	if err := agg.ProcessUpdate(addUpdate); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	// Modify the same bid order.
	modUpdate := OrderUpdate{
		DEXID:     "DEX_X",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Modify", Side: "bid", Price: 99.0, Quantity: 2.5, OrderID: "X_bid_1"},
		},
	}
	if err := agg.ProcessUpdate(modUpdate); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	ob := agg.GetAggregatedBook()
	if len(ob.Bids) != 1 {
		t.Errorf("Expected 1 bid, got %d", len(ob.Bids))
	} else {
		if ob.Bids[0].Quantity != 2.5 {
			t.Errorf("Expected modified quantity 2.5, got %v", ob.Bids[0].Quantity)
		}
	}
}

func TestRemoveOrder(t *testing.T) {
	agg := NewAggregator("ETH/USDT", 3)
	// Add ask orders.
	addUpdate := OrderUpdate{
		DEXID:     "DEX_Y",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Add", Side: "ask", Price: 106.0, Quantity: 1.0, OrderID: "Y_ask_1"},
			{Type: "Add", Side: "ask", Price: 107.0, Quantity: 2.0, OrderID: "Y_ask_2"},
		},
	}
	if err := agg.ProcessUpdate(addUpdate); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	// Remove one ask order.
	remUpdate := OrderUpdate{
		DEXID:     "DEX_Y",
		TokenPair: "ETH/USDT",
		Changes: []OrderChange{
			{Type: "Remove", Side: "ask", Price: 107.0, Quantity: 0, OrderID: "Y_ask_2"},
		},
	}
	if err := agg.ProcessUpdate(remUpdate); err != nil {
		t.Fatalf("ProcessUpdate failed: %v", err)
	}
	ob := agg.GetAggregatedBook()
	// Only one ask order should remain.
	if len(ob.Asks) != 1 {
		t.Errorf("Expected 1 ask order after removal, got %d", len(ob.Asks))
	} else {
		if ob.Asks[0].Price != 106.0 {
			t.Errorf("Expected remaining ask price 106.0, got %v", ob.Asks[0].Price)
		}
	}
}

func TestConcurrentUpdates(t *testing.T) {
	agg := NewAggregator("ETH/USDT", 5)
	var wg sync.WaitGroup
	updateFunc := func(dexID string, changes []OrderChange) {
		defer wg.Done()
		update := OrderUpdate{
			DEXID:     dexID,
			TokenPair: "ETH/USDT",
			Changes:   changes,
		}
		if err := agg.ProcessUpdate(update); err != nil {
			t.Errorf("ProcessUpdate failed for %s: %v", dexID, err)
		}
	}

	// Prepare a list of updates from different DEXs.
	updates := []struct {
		dexID   string
		changes []OrderChange
	}{
		{"DEX_1", []OrderChange{
			{Type: "Add", Side: "bid", Price: 102.0, Quantity: 1.0, OrderID: "1_bid_1"},
		}},
		{"DEX_2", []OrderChange{
			{Type: "Add", Side: "ask", Price: 103.0, Quantity: 0.5, OrderID: "2_ask_1"},
		}},
		{"DEX_3", []OrderChange{
			{Type: "Add", Side: "bid", Price: 101.0, Quantity: 1.5, OrderID: "3_bid_1"},
		}},
		{"DEX_4", []OrderChange{
			{Type: "Add", Side: "ask", Price: 104.0, Quantity: 2.0, OrderID: "4_ask_1"},
		}},
		{"DEX_5", []OrderChange{
			{Type: "Add", Side: "bid", Price: 100.0, Quantity: 0.8, OrderID: "5_bid_1"},
		}},
	}

	wg.Add(len(updates))
	for _, upd := range updates {
		go updateFunc(upd.dexID, upd.changes)
	}

	wg.Wait()
	// Give some time for aggregator to process concurrent updates.
	time.Sleep(100 * time.Millisecond)

	ob := agg.GetAggregatedBook()
	var bidCount, askCount int
	for _, order := range ob.Bids {
		if order.Price >= 100.0 {
			bidCount++
		}
	}
	for _, order := range ob.Asks {
		if order.Price >= 103.0 {
			askCount++
		}
	}
	if bidCount == 0 {
		t.Errorf("Expected at least one bid order from concurrent updates")
	}
	if askCount == 0 {
		t.Errorf("Expected at least one ask order from concurrent updates")
	}
}