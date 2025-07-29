package decentralized_dome

import (
	"testing"
	"time"
)

func TestOrderBook_AddOrder(t *testing.T) {
	ob := NewOrderBook()
	order := Order{
		OrderID:   "order1",
		Symbol:    "BTCUSD",
		OrderType: Buy,
		Price:     50000.0,
		Quantity:  1,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}

	err := ob.AddOrder(order)
	if err != nil {
		t.Errorf("AddOrder failed: %v", err)
	}

	if len(ob.buyOrders) != 1 {
		t.Errorf("Expected 1 buy order, got %d", len(ob.buyOrders))
	}
}

func TestOrderBook_RemoveOrder(t *testing.T) {
	ob := NewOrderBook()
	order := Order{
		OrderID:   "order1",
		Symbol:    "BTCUSD",
		OrderType: Buy,
		Price:     50000.0,
		Quantity:  1,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}

	_ = ob.AddOrder(order)
	err := ob.RemoveOrder("order1")
	if err != nil {
		t.Errorf("RemoveOrder failed: %v", err)
	}

	if len(ob.buyOrders) != 0 {
		t.Errorf("Expected 0 buy orders after removal, got %d", len(ob.buyOrders))
	}
}

func TestOrderBook_GetBestBidAsk(t *testing.T) {
	ob := NewOrderBook()
	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "BTCUSD",
		OrderType: Buy,
		Price:     50000.0,
		Quantity:  1,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}
	sellOrder := Order{
		OrderID:   "sell1",
		Symbol:    "BTCUSD",
		OrderType: Sell,
		Price:     51000.0,
		Quantity:  1,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}

	_ = ob.AddOrder(buyOrder)
	_ = ob.AddOrder(sellOrder)

	bestBid := ob.GetBestBid()
	if bestBid != 50000.0 {
		t.Errorf("Expected best bid 50000.0, got %f", bestBid)
	}

	bestAsk := ob.GetBestAsk()
	if bestAsk != 51000.0 {
		t.Errorf("Expected best ask 51000.0, got %f", bestAsk)
	}
}

func TestOrderBook_Matching(t *testing.T) {
	ob := NewOrderBook()
	go ob.StartMatching()

	buyOrder := Order{
		OrderID:   "buy1",
		Symbol:    "BTCUSD",
		OrderType: Buy,
		Price:     50000.0,
		Quantity:  2,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}
	sellOrder := Order{
		OrderID:   "sell1",
		Symbol:    "BTCUSD",
		OrderType: Sell,
		Price:     49000.0,
		Quantity:  1,
		Timestamp: time.Now().UnixNano(),
		NodeID:    "node1",
	}

	_ = ob.AddOrder(buyOrder)
	_ = ob.AddOrder(sellOrder)

	// Give matching goroutine time to process
	time.Sleep(100 * time.Millisecond)

	if len(ob.buyOrders) != 1 || ob.buyOrders[0].Quantity != 1 {
		t.Errorf("Expected remaining buy quantity of 1, got %d", ob.buyOrders[0].Quantity)
	}

	if len(ob.sellOrders) != 0 {
		t.Errorf("Expected sell order to be fully matched, got %d remaining", len(ob.sellOrders))
	}
}

func TestOrderBook_ConcurrentAccess(t *testing.T) {
	ob := NewOrderBook()
	numOrders := 1000
	done := make(chan bool)

	for i := 0; i < numOrders; i++ {
		go func(i int) {
			order := Order{
				OrderID:   string(rune(i)),
				Symbol:    "BTCUSD",
				OrderType: Buy,
				Price:     50000.0 + float64(i),
				Quantity:  1,
				Timestamp: time.Now().UnixNano(),
				NodeID:    "node1",
			}
			_ = ob.AddOrder(order)
			done <- true
		}(i)
	}

	for i := 0; i < numOrders; i++ {
		<-done
	}

	if len(ob.buyOrders) != numOrders {
		t.Errorf("Expected %d orders, got %d", numOrders, len(ob.buyOrders))
	}
}

func TestOrderValidation(t *testing.T) {
	ob := NewOrderBook()
	tests := []struct {
		name    string
		order   Order
		wantErr bool
	}{
		{
			name: "valid order",
			order: Order{
				OrderID:   "valid1",
				Symbol:    "BTCUSD",
				OrderType: Buy,
				Price:     50000.0,
				Quantity:  1,
				Timestamp: time.Now().UnixNano(),
				NodeID:    "node1",
			},
			wantErr: false,
		},
		{
			name: "invalid symbol",
			order: Order{
				OrderID:   "invalid1",
				Symbol:    "INVALID",
				OrderType: Buy,
				Price:     50000.0,
				Quantity:  1,
				Timestamp: time.Now().UnixNano(),
				NodeID:    "node1",
			},
			wantErr: true,
		},
		{
			name: "negative price",
			order: Order{
				OrderID:   "invalid2",
				Symbol:    "BTCUSD",
				OrderType: Buy,
				Price:     -50000.0,
				Quantity:  1,
				Timestamp: time.Now().UnixNano(),
				NodeID:    "node1",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ob.AddOrder(tt.order)
			if (err != nil) != tt.wantErr {
				t.Errorf("AddOrder() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}