package order_book_aggregator_test

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"order_book_aggregator"
)

type shardResponse struct {
	Orders []orderEntry `json:"orders"`
}

type orderEntry struct {
	Price     float64 `json:"price"`
	Quantity  float64 `json:"quantity"`
	Timestamp string  `json:"timestamp"`
	Side      string  `json:"side"`
}

func createTestServer(orders []orderEntry, statusCode int) *httptest.Server {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(statusCode)
		resp := shardResponse{Orders: orders}
		data, err := json.Marshal(resp)
		if err != nil {
			http.Error(w, "internal error", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(data)
	})
	return httptest.NewServer(handler)
}

func parseTimestamp(t time.Time) string {
	return t.Format(time.RFC3339)
}

func TestBasicAggregation(t *testing.T) {
	now := time.Now().UTC()

	// Shard 1: one bid, one ask.
	orders1 := []orderEntry{
		{
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now),
			Side:      "bid",
		},
		{
			Price:     105.0,
			Quantity:  2.0,
			Timestamp: parseTimestamp(now),
			Side:      "ask",
		},
	}
	server1 := createTestServer(orders1, http.StatusOK)
	defer server1.Close()

	// Shard 2: one bid, one ask.
	orders2 := []orderEntry{
		{
			Price:     100.0,
			Quantity:  2.0,
			Timestamp: parseTimestamp(now),
			Side:      "bid",
		},
		{
			Price:     104.0,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now),
			Side:      "ask",
		},
	}
	server2 := createTestServer(orders2, http.StatusOK)
	defer server2.Close()

	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: server1.URL, Weight: 1.0},
			{Endpoint: server2.URL, Weight: 2.0},
		},
		Depth:      10,
		Staleness:  10 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)
	err := aggregator.RunOnce()
	if err != nil {
		t.Fatalf("RunOnce failed: %v", err)
	}
	aggBook := aggregator.GetAggregatedBook()

	// Expected aggregation:
	// Bid at 100.0: aggregated quantity = (1.0 * 1.0) + (2.0 * 2.0) = 5.0
	// Asks: Two ask levels. Lower ask comes first.
	// Ask at 104.0: aggregated quantity = 1.0 * 2.0 = 2.0
	// Ask at 105.0: aggregated quantity = 2.0 * 1.0 = 2.0

	// Verify bids: sorted descending by price.
	if len(aggBook.Bids) != 1 {
		t.Fatalf("Expected 1 bid level, got %d", len(aggBook.Bids))
	}
	bid := aggBook.Bids[0]
	if bid.Price != 100.0 {
		t.Errorf("Expected bid price 100.0, got %v", bid.Price)
	}
	if bid.Quantity != 5.0 {
		t.Errorf("Expected aggregated bid quantity 5.0, got %v", bid.Quantity)
	}

	// Verify asks: sorted ascending by price.
	if len(aggBook.Asks) != 2 {
		t.Fatalf("Expected 2 ask levels, got %d", len(aggBook.Asks))
	}
	ask1 := aggBook.Asks[0]
	ask2 := aggBook.Asks[1]
	if ask1.Price != 104.0 {
		t.Errorf("Expected first ask price 104.0, got %v", ask1.Price)
	}
	if ask1.Quantity != 2.0 {
		t.Errorf("Expected aggregated ask quantity 2.0 for price 104.0, got %v", ask1.Quantity)
	}
	if ask2.Price != 105.0 {
		t.Errorf("Expected second ask price 105.0, got %v", ask2.Price)
	}
	if ask2.Quantity != 2.0 {
		t.Errorf("Expected aggregated ask quantity 2.0 for price 105.0, got %v", ask2.Quantity)
	}
}

func TestStaleDataFiltering(t *testing.T) {
	now := time.Now().UTC()

	// Order which is fresh and one that is stale.
	orders := []orderEntry{
		{
			Price:     110.0,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now),
			Side:      "bid",
		},
		{
			Price:     115.0,
			Quantity:  1.5,
			// A stale order: 10 seconds old.
			Timestamp: parseTimestamp(now.Add(-10 * time.Second)),
			Side:      "bid",
		},
	}
	server := createTestServer(orders, http.StatusOK)
	defer server.Close()

	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: server.URL, Weight: 1.0},
		},
		Depth:      10,
		Staleness:  5 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)
	err := aggregator.RunOnce()
	if err != nil {
		t.Fatalf("RunOnce failed: %v", err)
	}
	aggBook := aggregator.GetAggregatedBook()

	// Only the fresh order should be present.
	if len(aggBook.Bids) != 1 {
		t.Fatalf("Expected 1 bid level due to staleness filtering, got %d", len(aggBook.Bids))
	}
	if aggBook.Bids[0].Price != 110.0 {
		t.Errorf("Expected bid price 110.0, got %v", aggBook.Bids[0].Price)
	}
}

func TestDepthLimit(t *testing.T) {
	now := time.Now().UTC()

	// Create orders with different prices.
	var orders []orderEntry
	for i := 0; i < 20; i++ {
		price := 100.0 + float64(i)
		orders = append(orders, orderEntry{
			Price:     price,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now),
			Side:      "ask",
		})
	}

	server := createTestServer(orders, http.StatusOK)
	defer server.Close()

	// Set depth limit to 5.
	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: server.URL, Weight: 1.0},
		},
		Depth:      5,
		Staleness:  10 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)
	err := aggregator.RunOnce()
	if err != nil {
		t.Fatalf("RunOnce failed: %v", err)
	}
	aggBook := aggregator.GetAggregatedBook()

	// Since these are asks, they should be sorted ascending and only top 5 retained.
	if len(aggBook.Asks) != 5 {
		t.Fatalf("Expected 5 ask levels due to depth limit, got %d", len(aggBook.Asks))
	}
	for i, ask := range aggBook.Asks {
		expectedPrice := 100.0 + float64(i)
		if ask.Price != expectedPrice {
			t.Errorf("At depth index %d, expected ask price %v, got %v", i, expectedPrice, ask.Price)
		}
	}
}

func TestShardFailure(t *testing.T) {
	now := time.Now().UTC()

	// Shard that returns valid orders.
	ordersValid := []orderEntry{
		{
			Price:     95.0,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now),
			Side:      "bid",
		},
	}
	validServer := createTestServer(ordersValid, http.StatusOK)
	defer validServer.Close()

	// Shard that simulates a failure (HTTP 500).
	failureServer := createTestServer(nil, http.StatusInternalServerError)
	defer failureServer.Close()

	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: validServer.URL, Weight: 1.0},
			{Endpoint: failureServer.URL, Weight: 1.0},
		},
		Depth:      10,
		Staleness:  10 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)
	err := aggregator.RunOnce()
	if err != nil {
		t.Fatalf("RunOnce failed when processing shards with partial failure: %v", err)
	}
	aggBook := aggregator.GetAggregatedBook()

	// Only the valid shard's data should be aggregated.
	if len(aggBook.Bids) == 0 && len(aggBook.Asks) == 0 {
		t.Fatalf("Expected aggregated orders from valid shard even when one shard fails")
	}
	// In this case, expect one bid from valid shard.
	if len(aggBook.Bids) != 1 {
		t.Errorf("Expected 1 bid level from valid shard, got %d", len(aggBook.Bids))
	}
	if aggBook.Bids[0].Price != 95.0 {
		t.Errorf("Expected bid price 95.0, got %v", aggBook.Bids[0].Price)
	}
}

func TestRealTimeUpdate(t *testing.T) {
	// This test simulates multiple consecutive aggregator runs and ensures that metrics
	// and aggregated book updates behave correctly.
	now := time.Now().UTC()

	// Create a server that updates its response.
	currentOrders := []orderEntry{
		{
			Price:     120.0,
			Quantity:  1.5,
			Timestamp: parseTimestamp(now),
			Side:      "ask",
		},
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := shardResponse{Orders: currentOrders}
		data, _ := json.Marshal(resp)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(data)
	}))
	defer server.Close()

	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: server.URL, Weight: 1.0},
		},
		Depth:      10,
		Staleness:  10 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)

	// First run.
	err := aggregator.RunOnce()
	if err != nil {
		t.Fatalf("First RunOnce failed: %v", err)
	}
	aggBook := aggregator.GetAggregatedBook()
	if len(aggBook.Asks) != 1 || aggBook.Asks[0].Price != 120.0 {
		t.Errorf("Expected ask with price 120.0, got %+v", aggBook.Asks)
	}

	// Update orders in the server.
	now2 := time.Now().UTC()
	currentOrders = []orderEntry{
		{
			Price:     118.0,
			Quantity:  2.0,
			Timestamp: parseTimestamp(now2),
			Side:      "ask",
		},
		{
			Price:     125.0,
			Quantity:  1.0,
			Timestamp: parseTimestamp(now2),
			Side:      "bid",
		},
	}

	// Second run.
	time.Sleep(100 * time.Millisecond)
	err = aggregator.RunOnce()
	if err != nil {
		t.Fatalf("Second RunOnce failed: %v", err)
	}
	aggBook = aggregator.GetAggregatedBook()

	// Verify updated aggregated book.
	// Expect bid at 125.0 and ask at 118.0.
	if len(aggBook.Bids) != 1 {
		t.Errorf("Expected 1 bid level after update, got %d", len(aggBook.Bids))
	} else if aggBook.Bids[0].Price != 125.0 {
		t.Errorf("Expected bid price 125.0 after update, got %v", aggBook.Bids[0].Price)
	}
	if len(aggBook.Asks) != 1 {
		t.Errorf("Expected 1 ask level after update, got %d", len(aggBook.Asks))
	} else if aggBook.Asks[0].Price != 118.0 {
		t.Errorf("Expected ask price 118.0 after update, got %v", aggBook.Asks[0].Price)
	}
}

func TestInvalidResponseHandling(t *testing.T) {
	// Test that aggregator handles invalid JSON responses gracefully.
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Return invalid JSON.
		_, _ = io.WriteString(w, "invalid json")
	}))
	defer server.Close()

	config := order_book_aggregator.Config{
		Shards: []order_book_aggregator.ShardConfig{
			{Endpoint: server.URL, Weight: 1.0},
		},
		Depth:     10,
		Staleness: 10 * time.Second,
	}

	aggregator := order_book_aggregator.NewAggregator(config)
	err := aggregator.RunOnce()
	if err == nil {
		t.Fatalf("Expected error on invalid JSON response, got none")
	}
}