package dax_engine

import (
	"testing"
	"time"
)

func TestOrderMatching(t *testing.T) {
	engine := NewDAXEngine()

	// Test basic buy order matching
	buyOrder := Order{
		OrderID:   "buy1",
		TokenPair: "ETH/USDT",
		OrderType: "BUY",
		Price:     1000000000, // 1.0
		Quantity:  10,
		Timestamp: time.Now().Unix(),
	}

	sellOrder := Order{
		OrderID:   "sell1",
		TokenPair: "ETH/USDT",
		OrderType: "SELL",
		Price:     900000000, // 0.9
		Quantity:  5,
		Timestamp: time.Now().Unix(),
	}

	// Place sell order first
	trades := engine.PlaceOrder(sellOrder)
	if len(trades) != 0 {
		t.Errorf("Expected 0 trades, got %d", len(trades))
	}

	// Place buy order which should match
	trades = engine.PlaceOrder(buyOrder)
	if len(trades) != 1 {
		t.Errorf("Expected 1 trade, got %d", len(trades))
	} else {
		trade := trades[0]
		if trade.Price != 900000000 {
			t.Errorf("Expected trade price 0.9, got %d", trade.Price)
		}
		if trade.Quantity != 5 {
			t.Errorf("Expected trade quantity 5, got %d", trade.Quantity)
		}
	}

	// Verify remaining buy order quantity
	orderBook := engine.GetOrderBook("ETH/USDT")
	if len(orderBook.BuyOrders) != 1 {
		t.Errorf("Expected 1 remaining buy order, got %d", len(orderBook.BuyOrders))
	} else {
		remainingOrder := orderBook.BuyOrders[0]
		if remainingOrder.Quantity != 5 {
			t.Errorf("Expected remaining quantity 5, got %d", remainingOrder.Quantity)
		}
	}
}

func TestPriceTimePriority(t *testing.T) {
	engine := NewDAXEngine()
	now := time.Now().Unix()

	// Create multiple sell orders at different prices and times
	sellOrders := []Order{
		{
			OrderID:   "sell1",
			TokenPair: "ETH/USDT",
			OrderType: "SELL",
			Price:     1000000000, // 1.0
			Quantity:  5,
			Timestamp: now - 10,
		},
		{
			OrderID:   "sell2",
			TokenPair: "ETH/USDT",
			OrderType: "SELL",
			Price:     950000000, // 0.95
			Quantity:  5,
			Timestamp: now - 5,
		},
		{
			OrderID:   "sell3",
			TokenPair: "ETH/USDT",
			OrderType: "SELL",
			Price:     950000000, // 0.95
			Quantity:  5,
			Timestamp: now,
		},
	}

	// Place all sell orders
	for _, order := range sellOrders {
		engine.PlaceOrder(order)
	}

	// Create buy order that should match with best price first
	buyOrder := Order{
		OrderID:   "buy1",
		TokenPair: "ETH/USDT",
		OrderType: "BUY",
		Price:     1000000000, // 1.0
		Quantity:  10,
		Timestamp: now,
	}

	trades := engine.PlaceOrder(buyOrder)
	if len(trades) != 2 {
		t.Errorf("Expected 2 trades, got %d", len(trades))
	} else {
		// First trade should be with sell2 (better price)
		if trades[0].SellOrderID != "sell2" {
			t.Errorf("Expected first trade with sell2, got %s", trades[0].SellOrderID)
		}
		// Second trade should be with sell3 (same price, earlier time)
		if trades[1].SellOrderID != "sell3" {
			t.Errorf("Expected second trade with sell3, got %s", trades[1].SellOrderID)
		}
	}
}

func TestOrderCancellation(t *testing.T) {
	engine := NewDAXEngine()

	order := Order{
		OrderID:   "order1",
		TokenPair: "ETH/USDT",
		OrderType: "BUY",
		Price:     1000000000,
		Quantity:  10,
		Timestamp: time.Now().Unix(),
	}

	// Place order
	engine.PlaceOrder(order)

	// Verify order exists
	orderBook := engine.GetOrderBook("ETH/USDT")
	if len(orderBook.BuyOrders) != 1 {
		t.Errorf("Expected 1 buy order, got %d", len(orderBook.BuyOrders))
	}

	// Cancel order
	success := engine.CancelOrder("order1", "ETH/USDT")
	if !success {
		t.Error("Failed to cancel order")
	}

	// Verify order removed
	orderBook = engine.GetOrderBook("ETH/USDT")
	if len(orderBook.BuyOrders) != 0 {
		t.Errorf("Expected 0 buy orders after cancellation, got %d", len(orderBook.BuyOrders))
	}
}

func TestPartialFills(t *testing.T) {
	engine := NewDAXEngine()

	// Place multiple sell orders
	engine.PlaceOrder(Order{
		OrderID:   "sell1",
		TokenPair: "ETH/USDT",
		OrderType: "SELL",
		Price:     1000000000,
		Quantity:  3,
		Timestamp: time.Now().Unix(),
	})

	engine.PlaceOrder(Order{
		OrderID:   "sell2",
		TokenPair: "ETH/USDT",
		OrderType: "SELL",
		Price:     1000000000,
		Quantity:  3,
		Timestamp: time.Now().Unix(),
	})

	// Place large buy order
	trades := engine.PlaceOrder(Order{
		OrderID:   "buy1",
		TokenPair: "ETH/USDT",
		OrderType: "BUY",
		Price:     1000000000,
		Quantity:  10,
		Timestamp: time.Now().Unix(),
	})

	if len(trades) != 2 {
		t.Errorf("Expected 2 trades, got %d", len(trades))
	}

	// Verify remaining buy order
	orderBook := engine.GetOrderBook("ETH/USDT")
	if len(orderBook.BuyOrders) != 1 {
		t.Errorf("Expected 1 remaining buy order, got %d", len(orderBook.BuyOrders))
	} else {
		remainingOrder := orderBook.BuyOrders[0]
		if remainingOrder.Quantity != 4 {
			t.Errorf("Expected remaining quantity 4, got %d", remainingOrder.Quantity)
		}
	}
}

func TestMultipleTokenPairs(t *testing.T) {
	engine := NewDAXEngine()

	// Place orders for different pairs
	engine.PlaceOrder(Order{
		OrderID:   "eth1",
		TokenPair: "ETH/USDT",
		OrderType: "BUY",
		Price:     1000000000,
		Quantity:  10,
		Timestamp: time.Now().Unix(),
	})

	engine.PlaceOrder(Order{
		OrderID:   "btc1",
		TokenPair: "BTC/USDT",
		OrderType: "BUY",
		Price:     50000000000, // 50.0
		Quantity:  2,
		Timestamp: time.Now().Unix(),
	})

	// Verify separate order books
	ethBook := engine.GetOrderBook("ETH/USDT")
	if len(ethBook.BuyOrders) != 1 {
		t.Errorf("Expected 1 ETH buy order, got %d", len(ethBook.BuyOrders))
	}

	btcBook := engine.GetOrderBook("BTC/USDT")
	if len(btcBook.BuyOrders) != 1 {
		t.Errorf("Expected 1 BTC buy order, got %d", len(btcBook.BuyOrders))
	}
}