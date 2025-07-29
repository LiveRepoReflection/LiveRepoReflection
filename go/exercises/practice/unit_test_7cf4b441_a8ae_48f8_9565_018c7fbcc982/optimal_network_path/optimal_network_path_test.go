package optimal_network_path

import (
	"testing"
)

func TestOptimalNetworkPath(t *testing.T) {
	tests := []struct {
		name        string
		N           int
		edges       [][]int
		source      int
		destination int
		maxCost     int
		maxLatency  int
		want        int
	}{
		{
			name: "simple path with one edge",
			N:    2,
			edges: [][]int{
				{0, 1, 10, 5},
			},
			source:      0,
			destination: 1,
			maxCost:     15,
			maxLatency:  10,
			want:        1,
		},
		{
			name: "no path exists",
			N:    3,
			edges: [][]int{
				{0, 1, 10, 5},
				{1, 2, 20, 15},
			},
			source:      0,
			destination: 2,
			maxCost:     15,
			maxLatency:  10,
			want:        -1,
		},
		{
			name: "multiple paths with constraints",
			N:    4,
			edges: [][]int{
				{0, 1, 5, 2},
				{0, 2, 10, 1},
				{1, 3, 8, 3},
				{2, 3, 5, 4},
			},
			source:      0,
			destination: 3,
			maxCost:     20,
			maxLatency:  6,
			want:        2,
		},
		{
			name: "multiple edges between same nodes",
			N:    3,
			edges: [][]int{
				{0, 1, 5, 10},
				{0, 1, 8, 5},
				{1, 2, 7, 3},
			},
			source:      0,
			destination: 2,
			maxCost:     15,
			maxLatency:  15,
			want:        2,
		},
		{
			name: "source equals destination",
			N:    3,
			edges: [][]int{
				{0, 1, 5, 2},
				{1, 2, 3, 1},
			},
			source:      1,
			destination: 1,
			maxCost:     100,
			maxLatency:  100,
			want:        0,
		},
		{
			name: "complex network with optimal path",
			N:    6,
			edges: [][]int{
				{0, 1, 3, 2},
				{0, 2, 7, 1},
				{1, 3, 5, 4},
				{2, 3, 2, 3},
				{2, 4, 6, 2},
				{3, 5, 4, 1},
				{4, 5, 3, 5},
			},
			source:      0,
			destination: 5,
			maxCost:     15,
			maxLatency:  10,
			want:        3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalNetworkPath(tt.N, tt.edges, tt.source, tt.destination, tt.maxCost, tt.maxLatency)
			if got != tt.want {
				t.Errorf("OptimalNetworkPath() = %v, want %v", got, tt.want)
			}
		})
	}
}