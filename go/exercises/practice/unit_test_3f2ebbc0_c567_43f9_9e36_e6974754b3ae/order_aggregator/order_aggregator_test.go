package order_aggregator

import (
	"reflect"
	"testing"
)

func TestAggregateOrderBook(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Convert test case input to the required format
			var input [][]Order
			for _, nodeOrders := range tc.input {
				var orders []Order
				for _, o := range nodeOrders {
					orders = append(orders, Order{
						Price:    o.Price,
						Quantity: o.Quantity,
						NodeID:   o.NodeID,
					})
				}
				input = append(input, orders)
			}

			// Convert expected output to the required format
			var expectedBuy []Order
			for _, o := range tc.expectedBuy {
				expectedBuy = append(expectedBuy, Order{
					Price:    o.Price,
					Quantity: o.Quantity,
					NodeID:   o.NodeID,
				})
			}

			var expectedSell []Order
			for _, o := range tc.expectedSell {
				expectedSell = append(expectedSell, Order{
					Price:    o.Price,
					Quantity: o.Quantity,
					NodeID:   o.NodeID,
				})
			}

			actualBuy, actualSell := AggregateOrderBook(input, tc.k)

			if !reflect.DeepEqual(actualBuy, expectedBuy) {
				t.Errorf("Buy orders mismatch\nGot: %v\nWant: %v", actualBuy, expectedBuy)
			}

			if !reflect.DeepEqual(actualSell, expectedSell) {
				t.Errorf("Sell orders mismatch\nGot: %v\nWant: %v", actualSell, expectedSell)
			}
		})
	}
}

func BenchmarkAggregateOrderBook(b *testing.B) {
	// Create a large test case for benchmarking
	var largeInput [][]Order
	for i := 0; i < 1000; i++ {
		var nodeOrders []Order
		for j := 0; j < 1000; j++ {
			nodeOrders = append(nodeOrders, Order{
				Price:    100.0 + float64(j)/10.0,
				Quantity: j % 10,
				NodeID:   i % 100,
			})
		}
		largeInput = append(largeInput, nodeOrders)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		AggregateOrderBook(largeInput, 100)
	}
}