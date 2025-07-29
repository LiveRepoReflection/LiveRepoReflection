package dex_matching

import (
	"testing"
)

func TestOrderMatching(t *testing.T) {
	tests := []struct {
		name     string
		orders   []Order
		expected []Trade
	}{
		{
			name: "simple match",
			orders: []Order{
				{"order1", "user1", "buy", 100, 10, 1},
				{"order2", "user2", "sell", 95, 5, 2},
			},
			expected: []Trade{
				{"order1", "order2", 100, 5},
			},
		},
		{
			name: "partial fill",
			orders: []Order{
				{"order1", "user1", "buy", 100, 10, 1},
				{"order2", "user2", "sell", 95, 15, 2},
			},
			expected: []Trade{
				{"order1", "order2", 100, 10},
			},
		},
		{
			name: "multiple matches",
			orders: []Order{
				{"order1", "user1", "buy", 100, 10, 1},
				{"order2", "user2", "sell", 95, 5, 2},
				{"order3", "user3", "sell", 100, 7, 3},
			},
			expected: []Trade{
				{"order1", "order2", 100, 5},
				{"order1", "order3", 100, 5},
			},
		},
		{
			name: "no match",
			orders: []Order{
				{"order1", "user1", "buy", 100, 10, 1},
				{"order2", "user2", "sell", 105, 5, 2},
			},
			expected: []Trade{},
		},
		{
			name: "timestamp priority",
			orders: []Order{
				{"order1", "user1", "buy", 100, 10, 2},
				{"order2", "user2", "buy", 100, 5, 1},
				{"order3", "user3", "sell", 100, 7, 3},
			},
			expected: []Trade{
				{"order2", "order3", 100, 5},
				{"order1", "order3", 100, 2},
			},
		},
		{
			name: "large quantity",
			orders: []Order{
				{"order1", "user1", "buy", 100, 1000000, 1},
				{"order2", "user2", "sell", 100, 1000000, 2},
			},
			expected: []Trade{
				{"order1", "order2", 100, 1000000},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			engine := NewMatchingEngine()
			var actualTrades []Trade

			for _, order := range tt.orders {
				trades := engine.ProcessOrder(order)
				actualTrades = append(actualTrades, trades...)
			}

			if len(actualTrades) != len(tt.expected) {
				t.Fatalf("expected %d trades, got %d", len(tt.expected), len(actualTrades))
			}

			for i := range tt.expected {
				if actualTrades[i] != tt.expected[i] {
					t.Errorf("trade %d mismatch:\nexpected: %+v\ngot:      %+v",
						i, tt.expected[i], actualTrades[i])
				}
			}
		})
	}
}

func BenchmarkOrderMatching(b *testing.B) {
	engine := NewMatchingEngine()
	orders := []Order{
		{"order1", "user1", "buy", 100, 10, 1},
		{"order2", "user2", "sell", 95, 5, 2},
		{"order3", "user3", "sell", 100, 7, 3},
		{"order4", "user4", "buy", 105, 15, 4},
		{"order5", "user5", "sell", 100, 20, 5},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for _, order := range orders {
			engine.ProcessOrder(order)
		}
	}
}