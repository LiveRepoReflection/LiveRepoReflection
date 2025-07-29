package order_match

import (
	"reflect"
	"testing"
	"time"
)

func TestExactMatch(t *testing.T) {
	engine := NewEngine()

	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "BTC/USD",
		Type:      "BUY",
		Price:     100.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}
	sellOrder := Order{
		OrderID:   "sell1",
		Symbol:    "BTC/USD",
		Type:      "SELL",
		Price:     100.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(buyOrder); err != nil {
		t.Fatalf("Failed to place buy order: %v", err)
	}
	if err := engine.PlaceOrder(sellOrder); err != nil {
		t.Fatalf("Failed to place sell order: %v", err)
	}

	trades := engine.MatchOrders("BTC/USD")
	expectedTrades := []Trade{
		{
			Price:      100.0,
			Quantity:   10,
			BuyOrderID: "buy1",
			SellOrderID: "sell1",
		},
	}
	if !reflect.DeepEqual(trades, expectedTrades) {
		t.Errorf("Expected trades %v, but got %v", expectedTrades, trades)
	}
}

func TestPartialMatch(t *testing.T) {
	engine := NewEngine()

	// A buy order with larger quantity than available in one sell order should partially match.
	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "BTC/USD",
		Type:      "BUY",
		Price:     105.0,
		Quantity:  15,
		Timestamp: time.Now().UnixNano(),
	}
	sellOrder1 := Order{
		OrderID:   "sell1",
		Symbol:    "BTC/USD",
		Type:      "SELL",
		Price:     105.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}
	sellOrder2 := Order{
		OrderID:   "sell2",
		Symbol:    "BTC/USD",
		Type:      "SELL",
		Price:     105.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(sellOrder1); err != nil {
		t.Fatalf("Failed to place sell order1: %v", err)
	}
	if err := engine.PlaceOrder(sellOrder2); err != nil {
		t.Fatalf("Failed to place sell order2: %v", err)
	}
	if err := engine.PlaceOrder(buyOrder); err != nil {
		t.Fatalf("Failed to place buy order: %v", err)
	}

	trades := engine.MatchOrders("BTC/USD")
	expectedTrades := []Trade{
		{
			Price:      105.0,
			Quantity:   10,
			BuyOrderID: "buy1",
			SellOrderID: "sell1",
		},
		{
			Price:      105.0,
			Quantity:   5,
			BuyOrderID: "buy1",
			SellOrderID: "sell2",
		},
	}
	if !reflect.DeepEqual(trades, expectedTrades) {
		t.Errorf("Expected trades %v, but got %v", expectedTrades, trades)
	}
}

func TestFIFO(t *testing.T) {
	engine := NewEngine()

	// Two sell orders at the same price but different timestamps should be processed in FIFO order.
	sellOrder1 := Order{
		OrderID:   "sell1",
		Symbol:    "ETH/USD",
		Type:      "SELL",
		Price:     200.0,
		Quantity:  5,
		Timestamp: time.Now().UnixNano(),
	}
	time.Sleep(1 * time.Microsecond)
	sellOrder2 := Order{
		OrderID:   "sell2",
		Symbol:    "ETH/USD",
		Type:      "SELL",
		Price:     200.0,
		Quantity:  5,
		Timestamp: time.Now().UnixNano(),
	}
	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "ETH/USD",
		Type:      "BUY",
		Price:     200.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(sellOrder1); err != nil {
		t.Fatalf("Failed to place sell order1: %v", err)
	}
	if err := engine.PlaceOrder(sellOrder2); err != nil {
		t.Fatalf("Failed to place sell order2: %v", err)
	}
	if err := engine.PlaceOrder(buyOrder); err != nil {
		t.Fatalf("Failed to place buy order: %v", err)
	}

	trades := engine.MatchOrders("ETH/USD")
	expectedTrades := []Trade{
		{
			Price:      200.0,
			Quantity:   5,
			BuyOrderID: "buy1",
			SellOrderID: "sell1",
		},
		{
			Price:      200.0,
			Quantity:   5,
			BuyOrderID: "buy1",
			SellOrderID: "sell2",
		},
	}
	if !reflect.DeepEqual(trades, expectedTrades) {
		t.Errorf("Expected trades %v, but got %v", expectedTrades, trades)
	}
}

func TestCancellation(t *testing.T) {
	engine := NewEngine()

	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "BTC/USD",
		Type:      "BUY",
		Price:     110.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}
	sellOrder := Order{
		OrderID:   "sell1",
		Symbol:    "BTC/USD",
		Type:      "SELL",
		Price:     110.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(buyOrder); err != nil {
		t.Fatalf("Failed to place buy order: %v", err)
	}
	if err := engine.PlaceOrder(sellOrder); err != nil {
		t.Fatalf("Failed to place sell order: %v", err)
	}

	// Cancel the sell order before matching.
	if err := engine.CancelOrder("sell1"); err != nil {
		t.Fatalf("Cancellation failed: %v", err)
	}

	trades := engine.MatchOrders("BTC/USD")
	if len(trades) != 0 {
		t.Errorf("Expected no trades after cancellation, but got %v", trades)
	}
}

func TestMarketOrder(t *testing.T) {
	engine := NewEngine()

	// Place limit sell orders first.
	sellOrder1 := Order{
		OrderID:   "sell1",
		Symbol:    "LTC/USD",
		Type:      "SELL",
		Price:     50.0,
		Quantity:  5,
		Timestamp: time.Now().UnixNano(),
	}
	sellOrder2 := Order{
		OrderID:   "sell2",
		Symbol:    "LTC/USD",
		Type:      "SELL",
		Price:     55.0,
		Quantity:  10,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(sellOrder1); err != nil {
		t.Fatalf("Failed to place sell order1: %v", err)
	}
	if err := engine.PlaceOrder(sellOrder2); err != nil {
		t.Fatalf("Failed to place sell order2: %v", err)
	}

	// Place a market buy order. Here, a market order is indicated by Price = 0.
	marketBuyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "LTC/USD",
		Type:      "BUY",
		Price:     0.0,
		Quantity:  7,
		Timestamp: time.Now().UnixNano(),
	}

	if err := engine.PlaceOrder(marketBuyOrder); err != nil {
		t.Fatalf("Failed to place market buy order: %v", err)
	}

	trades := engine.MatchOrders("LTC/USD")
	expectedTrades := []Trade{
		{
			Price:      50.0,
			Quantity:   5,
			BuyOrderID: "buy1",
			SellOrderID: "sell1",
		},
		{
			Price:      55.0,
			Quantity:   2,
			BuyOrderID: "buy1",
			SellOrderID: "sell2",
		},
	}
	if !reflect.DeepEqual(trades, expectedTrades) {
		t.Errorf("Expected trades %v, but got %v", expectedTrades, trades)
	}
}