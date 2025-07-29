package order_book

import (
	"testing"
	"time"
)

func TestOrderBook(t *testing.T) {
	ob := NewOrderBook()

	t.Run("SubmitOrder", func(t *testing.T) {
		buyOrder := Order{
			OrderID:    "buy1",
			OrderType:  Buy,
			Price:      100,
			Quantity:   10,
			Timestamp:  time.Now().UnixNano(),
			SubmitterID: "user1",
		}

		sellOrder := Order{
			OrderID:    "sell1",
			OrderType:  Sell,
			Price:      110,
			Quantity:   5,
			Timestamp:  time.Now().UnixNano(),
			SubmitterID: "user2",
		}

		ob.SubmitOrder(buyOrder)
		ob.SubmitOrder(sellOrder)

		if len(ob.GetBuyOrders()) != 1 || len(ob.GetSellOrders()) != 1 {
			t.Errorf("Expected 1 buy and 1 sell order, got %d buy and %d sell", len(ob.GetBuyOrders()), len(ob.GetSellOrders()))
		}
	})

	t.Run("MatchOrders", func(t *testing.T) {
		// Clear previous orders
		ob = NewOrderBook()

		// Submit matching orders
		ob.SubmitOrder(Order{
			OrderID:    "buy2",
			OrderType:  Buy,
			Price:      105,
			Quantity:   10,
			Timestamp:  time.Now().UnixNano(),
			SubmitterID: "user1",
		})

		ob.SubmitOrder(Order{
			OrderID:    "sell2",
			OrderType:  Sell,
			Price:      100,
			Quantity:   5,
			Timestamp:  time.Now().UnixNano(),
			SubmitterID: "user2",
		})

		trades := ob.MatchOrders()

		if len(trades) != 1 {
			t.Errorf("Expected 1 trade, got %d", len(trades))
		}

		if trades[0].Quantity != 5 {
			t.Errorf("Expected trade quantity 5, got %d", trades[0].Quantity)
		}

		if len(ob.GetBuyOrders()) != 1 || ob.GetBuyOrders()[0].Quantity != 5 {
			t.Errorf("Expected remaining buy quantity 5, got %d", ob.GetBuyOrders()[0].Quantity)
		}

		if len(ob.GetSellOrders()) != 0 {
			t.Errorf("Expected no remaining sell orders, got %d", len(ob.GetSellOrders()))
		}
	})

	t.Run("CancelOrder", func(t *testing.T) {
		ob = NewOrderBook()

		order := Order{
			OrderID:    "cancel1",
			OrderType:  Buy,
			Price:      100,
			Quantity:   10,
			Timestamp:  time.Now().UnixNano(),
			SubmitterID: "user1",
		}

		ob.SubmitOrder(order)
		if !ob.CancelOrder("cancel1") {
			t.Error("Failed to cancel existing order")
		}

		if len(ob.GetBuyOrders()) != 0 {
			t.Errorf("Expected 0 orders after cancellation, got %d", len(ob.GetBuyOrders()))
		}

		if ob.CancelOrder("nonexistent") {
			t.Error("Cancelled non-existent order")
		}
	})

	t.Run("OrderPriority", func(t *testing.T) {
		ob = NewOrderBook()

		// Same price, different timestamps
		ob.SubmitOrder(Order{
			OrderID:    "early",
			OrderType:  Buy,
			Price:      100,
			Quantity:   10,
			Timestamp:  1000,
			SubmitterID: "user1",
		})

		ob.SubmitOrder(Order{
			OrderID:    "late",
			OrderType:  Buy,
			Price:      100,
			Quantity:   5,
			Timestamp:  2000,
			SubmitterID: "user2",
		})

		// Higher price
		ob.SubmitOrder(Order{
			OrderID:    "high",
			OrderType:  Buy,
			Price:      110,
			Quantity:   3,
			Timestamp:  3000,
			SubmitterID: "user3",
		})

		orders := ob.GetBuyOrders()
		if len(orders) != 3 {
			t.Fatalf("Expected 3 orders, got %d", len(orders))
		}

		if orders[0].OrderID != "high" {
			t.Error("Highest price order not first")
		}

		if orders[1].OrderID != "early" {
			t.Error("Earlier same-price order not before later one")
		}

		if orders[2].OrderID != "late" {
			t.Error("Order priority incorrect")
		}
	})

	t.Run("ConcurrentOperations", func(t *testing.T) {
		ob = NewOrderBook()
		done := make(chan bool)

		go func() {
			for i := 0; i < 100; i++ {
				ob.SubmitOrder(Order{
					OrderID:    string(rune(i)),
					OrderType:  Buy,
					Price:      100 + i,
					Quantity:   1,
					Timestamp:  time.Now().UnixNano(),
					SubmitterID: "user",
				})
			}
			done <- true
		}()

		go func() {
			for i := 0; i < 100; i++ {
				ob.SubmitOrder(Order{
					OrderID:    string(rune(i + 100)),
					OrderType:  Sell,
					Price:      100 + i,
					Quantity:   1,
					Timestamp:  time.Now().UnixNano(),
					SubmitterID: "user",
				})
			}
			done <- true
		}()

		<-done
		<-done

		if len(ob.GetBuyOrders()) != 100 || len(ob.GetSellOrders()) != 100 {
			t.Errorf("Concurrent submission failed, got %d buy and %d sell orders", len(ob.GetBuyOrders()), len(ob.GetSellOrders()))
		}
	})
}