package order_optimizer

import (
	"fmt"
	"testing"
)

// TestCase represents a single test scenario for CalculateOptimalBuy.
type TestCase struct {
	name          string
	events        []string
	targetQty     int
	slippage      float64
	maxOrderSize  int
	commission    float64
	expectedPrice int
	expectedQty   int
}

func TestCalculateOptimalBuy(t *testing.T) {
	testCases := []TestCase{
		{
			name: "Exact match within slippage",
			events: []string{
				"NEW,BID,99,100",
				"NEW,ASK,100,5",
				"NEW,ASK,101,10",
				"NEW,ASK,102,15",
			},
			targetQty:     10,
			slippage:      0.02,
			maxOrderSize:  1000,
			commission:    0.0,
			expectedPrice: 101,
			expectedQty:   10,
		},
		{
			name: "Partial fulfillment, capped by slippage",
			events: []string{
				"NEW,BID,99,100",
				"NEW,ASK,100,5",
				"NEW,ASK,101,10",
				"NEW,ASK,102,15",
			},
			targetQty:     30,
			slippage:      0.02,
			maxOrderSize:  1000,
			commission:    0.0,
			expectedPrice: 101,
			expectedQty:   15,
		},
		{
			name: "Empty order book (no ask orders)",
			events: []string{
				"NEW,BID,100,50",
			},
			targetQty:     10,
			slippage:      0.02,
			maxOrderSize:  1000,
			commission:    0.0,
			expectedPrice: -1,
			expectedQty:   0,
		},
		{
			name: "Zero target quantity",
			events: []string{
				"NEW,BID,100,50",
				"NEW,ASK,101,10",
			},
			targetQty:     0,
			slippage:      0.02,
			maxOrderSize:  1000,
			commission:    0.0,
			// When Q is 0, expected execution quantity is 0.
			// Optimal price can default to the best ask if available.
			expectedPrice: 101,
			expectedQty:   0,
		},
		{
			name: "High commission affecting slippage",
			events: []string{
				"NEW,BID,100,100",
				"NEW,ASK,100,5",
				"NEW,ASK,101,10",
			},
			targetQty:     10,
			slippage:      0.02,
			maxOrderSize:  1000,
			commission:    0.05,
			// Even minimal fill pushes effective price above slippage threshold.
			expectedPrice: -1,
			expectedQty:   0,
		},
		{
			name: "Order size limit constraint",
			events: []string{
				"NEW,BID,100,100",
				"NEW,ASK,100,50",
				"NEW,ASK,101,50",
				"NEW,ASK,102,50",
			},
			targetQty:     120,
			slippage:      0.05,
			maxOrderSize:  40,
			commission:    0.0,
			// With maxOrderSize limited to 40, the system takes:
			// 40 from price 100, 40 from price 101, and 40 from price 102.
			// Execution average becomes 101, with last level price 102.
			expectedPrice: 102,
			expectedQty:   120,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			price, qty := CalculateOptimalBuy(tc.events, tc.targetQty, tc.slippage, tc.maxOrderSize, tc.commission)
			if price != tc.expectedPrice || qty != tc.expectedQty {
				t.Errorf("Test '%s' failed:\nEvents: %v\nParameters: targetQty=%d, slippage=%f, maxOrderSize=%d, commission=%f\nExpected (price, qty): (%d, %d) but got (%d, %d)",
					tc.name, tc.events, tc.targetQty, tc.slippage, tc.maxOrderSize, tc.commission,
					tc.expectedPrice, tc.expectedQty, price, qty)
			} else {
				t.Logf("Test '%s' succeeded: got (price, qty): (%d, %d)", tc.name, price, qty)
			}
		})
	}
}

// Benchmark test for performance evaluation.
func BenchmarkCalculateOptimalBuy(b *testing.B) {
	events := []string{
		"NEW,BID,100,500",
		"NEW,ASK,101,500",
		"NEW,ASK,102,500",
		"NEW,ASK,103,500",
		"NEW,ASK,104,500",
		"NEW,BID,99,500",
		"NEW,ASK,105,500",
	}
	targetQty := 1000
	slippage := 0.03
	maxOrderSize := 1000
	commission := 0.01

	for i := 0; i < b.N; i++ {
		_, _ = CalculateOptimalBuy(events, targetQty, slippage, maxOrderSize, commission)
	}
}

// Example test to demonstrate usage.
func ExampleCalculateOptimalBuy() {
	events := []string{
		"NEW,BID,99,100",
		"NEW,ASK,100,5",
		"NEW,ASK,101,10",
		"NEW,ASK,102,15",
	}
	targetQty := 10
	slippage := 0.02
	maxOrderSize := 1000
	commission := 0.0

	price, qty := CalculateOptimalBuy(events, targetQty, slippage, maxOrderSize, commission)
	fmt.Printf("%d %d", price, qty)
	// Output: 101 10
}