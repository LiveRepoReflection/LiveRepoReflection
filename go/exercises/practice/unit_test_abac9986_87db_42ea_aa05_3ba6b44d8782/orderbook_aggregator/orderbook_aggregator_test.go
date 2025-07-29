package orderbook_aggregator

import (
	"reflect"
	"testing"
	"time"
)

func TestOrderBookAggregator(t *testing.T) {
	t.Run("basic aggregation", func(t *testing.T) {
		node1 := make(chan []Order)
		node2 := make(chan []Order)
		agg := NewOrderBookAggregator([]<-chan []Order{node1, node2})

		go func() {
			node1 <- []Order{{Price: 100, Quantity: 5, IsBid: true}}
			node2 <- []Order{{Price: 100, Quantity: 3, IsBid: true}}
			close(node1)
			close(node2)
		}()

		// Give aggregator time to process
		time.Sleep(100 * time.Millisecond)

		bids, asks := agg.GetTopOrders(1)
		if len(bids) != 1 || bids[0].Quantity != 8 {
			t.Errorf("Expected aggregated bid quantity 8, got %v", bids)
		}
		if len(asks) != 0 {
			t.Errorf("Expected no asks, got %v", asks)
		}
	})

	t.Run("multiple nodes with mixed orders", func(t *testing.T) {
		node1 := make(chan []Order)
		node2 := make(chan []Order)
		agg := NewOrderBookAggregator([]<-chan []Order{node1, node2})

		go func() {
			node1 <- []Order{
				{Price: 100, Quantity: 5, IsBid: true},
				{Price: 200, Quantity: 2, IsBid: false},
			}
			node2 <- []Order{
				{Price: 100, Quantity: 3, IsBid: true},
				{Price: 200, Quantity: 4, IsBid: false},
				{Price: 150, Quantity: 1, IsBid: false},
			}
			close(node1)
			close(node2)
		}()

		time.Sleep(100 * time.Millisecond)

		bids, asks := agg.GetTopOrders(2)
		expectedBids := []Order{{Price: 100, Quantity: 8, IsBid: true}}
		expectedAsks := []Order{
			{Price: 150, Quantity: 1, IsBid: false},
			{Price: 200, Quantity: 6, IsBid: false},
		}

		if !reflect.DeepEqual(bids, expectedBids) {
			t.Errorf("Expected bids %v, got %v", expectedBids, bids)
		}
		if !reflect.DeepEqual(asks, expectedAsks) {
			t.Errorf("Expected asks %v, got %v", expectedAsks, asks)
		}
	})

	t.Run("order removal with zero quantity", func(t *testing.T) {
		node := make(chan []Order)
		agg := NewOrderBookAggregator([]<-chan []Order{node})

		go func() {
			node <- []Order{
				{Price: 100, Quantity: 5, IsBid: true},
				{Price: 100, Quantity: -5, IsBid: true},
			}
			close(node)
		}()

		time.Sleep(100 * time.Millisecond)

		bids, _ := agg.GetTopOrders(1)
		if len(bids) != 0 {
			t.Errorf("Expected no bids after removal, got %v", bids)
		}
	})

	t.Run("node failure handling", func(t *testing.T) {
		node1 := make(chan []Order)
		node2 := make(chan []Order)
		agg := NewOrderBookAggregator([]<-chan []Order{node1, node2})

		go func() {
			node1 <- []Order{{Price: 100, Quantity: 5, IsBid: true}}
			close(node1) // node1 fails
			node2 <- []Order{{Price: 100, Quantity: 3, IsBid: true}}
			close(node2)
		}()

		time.Sleep(100 * time.Millisecond)

		bids, _ := agg.GetTopOrders(1)
		if len(bids) != 1 || bids[0].Quantity != 8 {
			t.Errorf("Expected aggregated bid quantity 8 after node failure, got %v", bids)
		}
	})

	t.Run("get top N orders", func(t *testing.T) {
		node := make(chan []Order)
		agg := NewOrderBookAggregator([]<-chan []Order{node})

		go func() {
			node <- []Order{
				{Price: 90, Quantity: 1, IsBid: true},
				{Price: 100, Quantity: 2, IsBid: true},
				{Price: 110, Quantity: 3, IsBid: true},
				{Price: 200, Quantity: 1, IsBid: false},
				{Price: 210, Quantity: 2, IsBid: false},
				{Price: 220, Quantity: 3, IsBid: false},
			}
			close(node)
		}()

		time.Sleep(100 * time.Millisecond)

		t.Run("N smaller than available", func(t *testing.T) {
			bids, asks := agg.GetTopOrders(2)
			if len(bids) != 2 || bids[0].Price != 110 || bids[1].Price != 100 {
				t.Errorf("Expected top 2 bids, got %v", bids)
			}
			if len(asks) != 2 || asks[0].Price != 200 || asks[1].Price != 210 {
				t.Errorf("Expected top 2 asks, got %v", asks)
			}
		})

		t.Run("N larger than available", func(t *testing.T) {
			bids, asks := agg.GetTopOrders(10)
			if len(bids) != 3 {
				t.Errorf("Expected all 3 bids, got %v", bids)
			}
			if len(asks) != 3 {
				t.Errorf("Expected all 3 asks, got %v", asks)
			}
		})
	})
}