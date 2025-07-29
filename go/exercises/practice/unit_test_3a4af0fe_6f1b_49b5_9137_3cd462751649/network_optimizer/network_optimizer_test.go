package network_optimizer

import (
	"testing"
)

func TestNetworkOptimizer(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		cost     [][]int
		budget   int
		expected [][]int
	}{
		{
			name: "basic connected case",
			n:    3,
			cost: [][]int{
				{-1, 1, 2},
				{1, -1, 3},
				{2, 3, -1},
			},
			budget:   4,
			expected: [][]int{{0, 1}, {0, 2}},
		},
		{
			name: "insufficient budget",
			n:    4,
			cost: [][]int{
				{-1, 5, 10, -1},
				{5, -1, 3, 8},
				{10, 3, -1, 1},
				{-1, 8, 1, -1},
			},
			budget:   7,
			expected: [][]int{{1, 2}, {2, 3}},
		},
		{
			name: "disconnected servers",
			n:    4,
			cost: [][]int{
				{-1, -1, 5, -1},
				{-1, -1, -1, 2},
				{5, -1, -1, 1},
				{-1, 2, 1, -1},
			},
			budget:   6,
			expected: [][]int{{1, 3}, {2, 3}},
		},
		{
			name: "max budget usage",
			n:    4,
			cost: [][]int{
				{-1, 2, 3, 4},
				{2, -1, 5, 6},
				{3, 5, -1, 7},
				{4, 6, 7, -1},
			},
			budget:   9,
			expected: [][]int{{0, 1}, {0, 2}, {0, 3}},
		},
		{
			name: "no possible connections",
			n:    3,
			cost: [][]int{
				{-1, -1, -1},
				{-1, -1, -1},
				{-1, -1, -1},
			},
			budget:   10,
			expected: [][]int{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := OptimizeNetwork(tt.n, tt.cost, tt.budget)
			if !equalEdges(result, tt.expected) {
				t.Errorf("OptimizeNetwork() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func equalEdges(a, b [][]int) bool {
	if len(a) != len(b) {
		return false
	}

	seen := make(map[[2]int]bool)
	for _, edge := range a {
		key := [2]int{edge[0], edge[1]}
		if edge[0] > edge[1] {
			key = [2]int{edge[1], edge[0]}
		}
		seen[key] = true
	}

	for _, edge := range b {
		key := [2]int{edge[0], edge[1]}
		if edge[0] > edge[1] {
			key = [2]int{edge[1], edge[0]}
		}
		if !seen[key] {
			return false
		}
	}

	return true
}