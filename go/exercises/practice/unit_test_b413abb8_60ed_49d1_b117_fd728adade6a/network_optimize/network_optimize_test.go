package network_optimize

import (
	"testing"
)

func TestOptimizeNetwork(t *testing.T) {
	tests := []struct {
		name         string
		n            int
		edges        [][3]int
		source       int
		destination  int
		latency      map[[2]int]int
		dataSize     int
		wantPath     []int
		wantThroughput float64
	}{
		{
			name: "simple path with one route",
			n:    2,
			edges: [][3]int{
				{0, 1, 100},
			},
			source:      0,
			destination: 1,
			latency: map[[2]int]int{
				{0, 1}: 10,
			},
			dataSize:     1024,
			wantPath:     []int{0, 1},
			wantThroughput: 10.0, // 100/10
		},
		{
			name: "multiple paths with different throughput",
			n:    4,
			edges: [][3]int{
				{0, 1, 100},
				{0, 2, 50},
				{1, 3, 200},
				{2, 3, 150},
			},
			source:      0,
			destination: 3,
			latency: map[[2]int]int{
				{0, 1}: 10,
				{0, 2}: 5,
				{1, 3}: 20,
				{2, 3}: 12,
			},
			dataSize:     2048,
			wantPath:     []int{0, 1, 3}, // 100/30 = 3.33 vs 50/17 = 2.94
			wantThroughput: 3.3333333333333335,
		},
		{
			name: "no path exists",
			n:    3,
			edges: [][3]int{
				{0, 1, 100},
				{1, 2, 200},
			},
			source:      2,
			destination: 0,
			latency: map[[2]int]int{
				{0, 1}: 10,
				{1, 2}: 20,
			},
			dataSize:     512,
			wantPath:     nil,
			wantThroughput: 0.0,
		},
		{
			name: "multiple edges between nodes",
			n:    3,
			edges: [][3]int{
				{0, 1, 100},
				{0, 1, 200},
				{1, 2, 300},
			},
			source:      0,
			destination: 2,
			latency: map[[2]int]int{
				{0, 1}: 10,
				{0, 1}: 15, // second edge
				{1, 2}: 20,
			},
			dataSize:     1024,
			wantPath:     []int{0, 1, 2}, // 100/30 vs 200/35
			wantThroughput: 5.714285714285714,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotPath, gotThroughput := OptimizeNetwork(
				tt.n,
				tt.edges,
				tt.source,
				tt.destination,
				tt.latency,
				tt.dataSize,
			)

			if !comparePaths(gotPath, tt.wantPath) {
				t.Errorf("OptimizeNetwork() path = %v, want %v", gotPath, tt.wantPath)
			}

			if gotThroughput != tt.wantThroughput {
				t.Errorf("OptimizeNetwork() throughput = %v, want %v", gotThroughput, tt.wantThroughput)
			}
		})
	}
}

func comparePaths(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}