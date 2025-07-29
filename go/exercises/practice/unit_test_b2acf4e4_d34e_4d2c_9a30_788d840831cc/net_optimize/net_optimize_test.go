package net_optimize

import (
	"testing"
)

func TestNetworkOptimization(t *testing.T) {
	tests := []struct {
		name                  string
		n                     int
		connections           [][]int
		queries               [][]int
		criticalNodes         []int
		criticalNodePenalty   int
		maxHops               int
		expected              []int
	}{
		{
			name:                "basic connected graph",
			n:                   4,
			connections:         [][]int{{0, 1, 5}, {0, 2, 3}, {1, 3, 6}, {2, 3, 2}},
			queries:             [][]int{{0, 3}, {1, 2}},
			criticalNodes:       []int{3},
			criticalNodePenalty: 10,
			maxHops:             3,
			expected:            []int{15, 8},
		},
		{
			name:                "disconnected graph",
			n:                   5,
			connections:         [][]int{{0, 1, 2}, {2, 3, 4}},
			queries:             [][]int{{0, 4}, {1, 3}},
			criticalNodes:       []int{},
			criticalNodePenalty: 0,
			maxHops:             5,
			expected:            []int{-1, -1},
		},
		{
			name:                "multiple critical nodes",
			n:                   6,
			connections:         [][]int{{0, 1, 1}, {1, 2, 2}, {2, 3, 3}, {3, 4, 4}, {4, 5, 5}},
			queries:             [][]int{{0, 5}, {1, 4}},
			criticalNodes:       []int{2, 4},
			criticalNodePenalty: 5,
			maxHops:             10,
			expected:            []int{25, 19},
		},
		{
			name:                "hop limit constraint",
			n:                   4,
			connections:         [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}, {0, 3, 10}},
			queries:             [][]int{{0, 3}},
			criticalNodes:       []int{},
			criticalNodePenalty: 0,
			maxHops:             2,
			expected:            []int{10},
		},
		{
			name:                "large penalty makes critical nodes undesirable",
			n:                   3,
			connections:         [][]int{{0, 1, 1}, {1, 2, 1}, {0, 2, 5}},
			queries:             [][]int{{0, 2}},
			criticalNodes:       []int{1},
			criticalNodePenalty: 100,
			maxHops:             2,
			expected:            []int{5},
		},
		{
			name:                "no critical nodes",
			n:                   5,
			connections:         [][]int{{0, 1, 2}, {1, 2, 3}, {2, 3, 4}, {3, 4, 5}},
			queries:             [][]int{{0, 4}, {1, 3}},
			criticalNodes:       []int{},
			criticalNodePenalty: 0,
			maxHops:             4,
			expected:            []int{14, 7},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimizeNetwork(tt.n, tt.connections, tt.queries, tt.criticalNodes, tt.criticalNodePenalty, tt.maxHops)
			if len(got) != len(tt.expected) {
				t.Fatalf("expected %d results, got %d", len(tt.expected), len(got))
			}
			for i := range got {
				if got[i] != tt.expected[i] {
					t.Errorf("query %d: expected %d, got %d", i, tt.expected[i], got[i])
				}
			}
		})
	}
}

func BenchmarkOptimizeNetwork(b *testing.B) {
	n := 100
	connections := make([][]int, 0)
	for i := 0; i < n-1; i++ {
		connections = append(connections, []int{i, i + 1, 1})
	}
	queries := [][]int{{0, n - 1}}
	criticalNodes := []int{50}
	criticalNodePenalty := 10
	maxHops := 200

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimizeNetwork(n, connections, queries, criticalNodes, criticalNodePenalty, maxHops)
	}
}