package dex_matcher

import (
	"testing"
	"time"
)

func TestOrderMatching(t *testing.T) {
	t.Run("empty order book", func(t *testing.T) {
		engine := NewMatchingEngine()
		trades := engine.MatchOrder(Order{
			ID:        "order1",
			Type:      BUY,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		})
		if len(trades) != 0 {
			t.Errorf("Expected no trades with empty order book, got %d", len(trades))
		}
	})

	t.Run("exact match", func(t *testing.T) {
		engine := NewMatchingEngine()
		sellOrder := Order{
			ID:        "sell1",
			Type:      SELL,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		}
		engine.MatchOrder(sellOrder)

		buyOrder := Order{
			ID:        "buy1",
			Type:      BUY,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		}
		trades := engine.MatchOrder(buyOrder)

		if len(trades) != 1 {
			t.Fatalf("Expected 1 trade, got %d", len(trades))
		}
		if trades[0].Quantity != 1.0 {
			t.Errorf("Expected quantity 1.0, got %f", trades[0].Quantity)
		}
	})

	t.Run("partial match", func(t *testing.T) {
		engine := NewMatchingEngine()
		sellOrder := Order{
			ID:        "sell1",
			Type:      SELL,
			Price:     100.0,
			Quantity:  2.0,
			Timestamp: time.Now().UnixNano(),
		}
		engine.MatchOrder(sellOrder)

		buyOrder := Order{
			ID:        "buy1",
			Type:      BUY,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		}
		trades := engine.MatchOrder(buyOrder)

		if len(trades) != 1 {
			t.Fatalf("Expected 1 trade, got %d", len(trades))
		}
		if trades[0].Quantity != 1.0 {
			t.Errorf("Expected quantity 1.0, got %f", trades[0].Quantity)
		}
	})

	t.Run("price priority", func(t *testing.T) {
		engine := NewMatchingEngine()
		engine.MatchOrder(Order{
			ID:        "sell1",
			Type:      SELL,
			Price:     101.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		})
		engine.MatchOrder(Order{
			ID:        "sell2",
			Type:      SELL,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		})

		buyOrder := Order{
			ID:        "buy1",
			Type:      BUY,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		}
		trades := engine.MatchOrder(buyOrder)

		if len(trades) != 1 {
			t.Fatalf("Expected 1 trade, got %d", len(trades))
		}
		if trades[0].Price != 100.0 {
			t.Errorf("Expected price 100.0, got %f", trades[0].Price)
		}
	})

	t.Run("time priority", func(t *testing.T) {
		now := time.Now().UnixNano()
		engine := NewMatchingEngine()
		engine.MatchOrder(Order{
			ID:        "sell1",
			Type:      SELL,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: now,
		})
		engine.MatchOrder(Order{
			ID:        "sell2",
			Type:      SELL,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: now + 1,
		})

		buyOrder := Order{
			ID:        "buy1",
			Type:      BUY,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: now + 2,
		}
		trades := engine.MatchOrder(buyOrder)

		if len(trades) != 1 {
			t.Fatalf("Expected 1 trade, got %d", len(trades))
		}
		if trades[0].SellerOrderID != "sell1" {
			t.Errorf("Expected seller order ID 'sell1', got '%s'", trades[0].SellerOrderID)
		}
	})

	t.Run("concurrent matching", func(t *testing.T) {
		engine := NewMatchingEngine()
		done := make(chan bool)
		numOrders := 1000

		go func() {
			for i := 0; i < numOrders; i++ {
				engine.MatchOrder(Order{
					ID:        string(rune(i)),
					Type:      SELL,
					Price:     100.0,
					Quantity:  1.0,
					Timestamp: time.Now().UnixNano(),
				})
			}
			done <- true
		}()

		go func() {
			for i := 0; i < numOrders; i++ {
				engine.MatchOrder(Order{
					ID:        string(rune(i + numOrders)),
					Type:      BUY,
					Price:     100.0,
					Quantity:  1.0,
					Timestamp: time.Now().UnixNano(),
				})
			}
			done <- true
		}()

		<-done
		<-done
	})
}

func BenchmarkMatchingEngine(b *testing.B) {
	engine := NewMatchingEngine()
	orders := make([]Order, b.N)
	for i := 0; i < b.N; i++ {
		orderType := BUY
		if i%2 == 0 {
			orderType = SELL
		}
		orders[i] = Order{
			ID:        string(rune(i)),
			Type:      orderType,
			Price:     100.0,
			Quantity:  1.0,
			Timestamp: time.Now().UnixNano(),
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		engine.MatchOrder(orders[i])
	}
}