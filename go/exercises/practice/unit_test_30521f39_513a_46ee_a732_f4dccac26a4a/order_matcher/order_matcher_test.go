package ordermatcher

import (
	"reflect"
	"sort"
	"testing"
)

func TestMatchOrders(t *testing.T) {
	tests := []struct {
		name       string
		buyOrders  []Order
		sellOrders []Order
		want       []Trade
	}{
		{
			name: "basic matching test",
			buyOrders: []Order{
				{"buy1", "BUY", 10, 5, 1678886400000000000, "user1"},
				{"buy2", "BUY", 10, 3, 1678886401000000000, "user2"},
				{"buy3", "BUY", 9, 2, 1678886402000000000, "user3"},
			},
			sellOrders: []Order{
				{"sell1", "SELL", 9, 4, 1678886399000000000, "user4"},
				{"sell2", "SELL", 10, 2, 1678886403000000000, "user5"},
			},
			want: []Trade{
				{BuyOrderID: "buy1", SellOrderID: "sell1", Price: 9, Quantity: 4},
				{BuyOrderID: "buy1", SellOrderID: "sell2", Price: 10, Quantity: 1},
				{BuyOrderID: "buy2", SellOrderID: "sell2", Price: 10, Quantity: 1},
			},
		},
		{
			name:       "empty orders test",
			buyOrders:  []Order{},
			sellOrders: []Order{},
			want:       []Trade{},
		},
		{
			name: "self-trade prevention test",
			buyOrders: []Order{
				{"buy1", "BUY", 10, 5, 1678886400000000000, "user1"},
			},
			sellOrders: []Order{
				{"sell1", "SELL", 10, 5, 1678886400000000000, "user1"},
			},
			want: []Trade{},
		},
		{
			name: "invalid orders test",
			buyOrders: []Order{
				{"buy1", "BUY", -10, 5, 1678886400000000000, "user1"},
				{"buy2", "BUY", 10, -5, 1678886400000000000, "user2"},
			},
			sellOrders: []Order{
				{"sell1", "SELL", 10, 0, 1678886400000000000, "user3"},
			},
			want: []Trade{},
		},
		{
			name: "partial fills test",
			buyOrders: []Order{
				{"buy1", "BUY", 10, 10, 1678886400000000000, "user1"},
			},
			sellOrders: []Order{
				{"sell1", "SELL", 10, 4, 1678886400000000000, "user2"},
				{"sell2", "SELL", 10, 4, 1678886400000000000, "user3"},
			},
			want: []Trade{
				{BuyOrderID: "buy1", SellOrderID: "sell1", Price: 10, Quantity: 4},
				{BuyOrderID: "buy1", SellOrderID: "sell2", Price: 10, Quantity: 4},
			},
		},
		{
			name: "price priority test",
			buyOrders: []Order{
				{"buy1", "BUY", 10, 5, 1678886400000000000, "user1"},
			},
			sellOrders: []Order{
				{"sell1", "SELL", 11, 5, 1678886400000000000, "user2"},
				{"sell2", "SELL", 9, 5, 1678886401000000000, "user3"},
			},
			want: []Trade{
				{BuyOrderID: "buy1", SellOrderID: "sell2", Price: 9, Quantity: 5},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MatchOrders(tt.buyOrders, tt.sellOrders)
			
			// Sort the trades by BuyOrderID and SellOrderID for consistent comparison
			sort.Slice(got, func(i, j int) bool {
				if got[i].BuyOrderID == got[j].BuyOrderID {
					return got[i].SellOrderID < got[j].SellOrderID
				}
				return got[i].BuyOrderID < got[j].BuyOrderID
			})
			sort.Slice(tt.want, func(i, j int) bool {
				if tt.want[i].BuyOrderID == tt.want[j].BuyOrderID {
					return tt.want[i].SellOrderID < tt.want[j].SellOrderID
				}
				return tt.want[i].BuyOrderID < tt.want[j].BuyOrderID
			})

			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("MatchOrders() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMatchOrders(b *testing.B) {
	buyOrders := []Order{
		{"buy1", "BUY", 10, 5, 1678886400000000000, "user1"},
		{"buy2", "BUY", 10, 3, 1678886401000000000, "user2"},
		{"buy3", "BUY", 9, 2, 1678886402000000000, "user3"},
	}
	sellOrders := []Order{
		{"sell1", "SELL", 9, 4, 1678886399000000000, "user4"},
		{"sell2", "SELL", 10, 2, 1678886403000000000, "user5"},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MatchOrders(buyOrders, sellOrders)
	}
}