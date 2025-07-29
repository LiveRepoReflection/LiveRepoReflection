package network_design

import (
	"testing"
)

func TestMinNetworkCost(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		costFunc func(int, int) int
		want     int
	}{
		{
			name: "single city",
			n:    1,
			costFunc: func(i, j int) int {
				return 0
			},
			want: 0,
		},
		{
			name: "two cities with cost 5",
			n:    2,
			costFunc: func(i, j int) int {
				if i == 0 && j == 1 {
					return 5
				}
				return 0
			},
			want: 5,
		},
		{
			name: "three cities with triangle costs",
			n:    3,
			costFunc: func(i, j int) int {
				if (i == 0 && j == 1) || (i == 1 && j == 0) {
					return 10
				}
				if (i == 0 && j == 2) || (i == 2 && j == 0) {
					return 15
				}
				if (i == 1 && j == 2) || (i == 2 && j == 1) {
					return 5
				}
				return 0
			},
			want: 15,
		},
		{
			name: "four cities with varying costs",
			n:    4,
			costFunc: func(i, j int) int {
				costs := [][]int{
					{0, 10, 6, 5},
					{10, 0, 15, 20},
					{6, 15, 0, 12},
					{5, 20, 12, 0},
				}
				return costs[i][j]
			},
			want: 21,
		},
		{
			name: "disconnected cities (should still connect)",
			n:    4,
			costFunc: func(i, j int) int {
				if (i == 0 && j == 1) || (i == 1 && j == 0) {
					return 1
				}
				if (i == 2 && j == 3) || (i == 3 && j == 2) {
					return 1
				}
				if (i == 0 && j == 2) || (i == 2 && j == 0) {
					return 100
				}
				return 1000
			},
			want: 102,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinNetworkCost(tt.n, tt.costFunc)
			if got != tt.want {
				t.Errorf("MinNetworkCost() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMinNetworkCost(b *testing.B) {
	n := 100
	costFunc := func(i, j int) int {
		return (i + j) % 100
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinNetworkCost(n, costFunc)
	}
}