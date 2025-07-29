package grid_optimize

import (
	"testing"
)

func TestOptimizeGrid(t *testing.T) {
	tests := []struct {
		name            string
		n               int
		edges           [][]int
		powerDemands    []int
		communityDemand int
		maxCapacity     int
		expected        int
	}{
		{
			name: "Basic two nodes",
			n:    2,
			edges: [][]int{
				{0, 1, 10},
			},
			powerDemands:    []int{5, 5},
			communityDemand: 10,
			maxCapacity:     20,
			expected:        15,
		},
		{
			name: "Infeasible load",
			n:    3,
			edges: [][]int{
				{0, 1, 5},
				{1, 2, 5},
			},
			powerDemands:    []int{30, 30, 30},
			communityDemand: 10,
			maxCapacity:     50,
			expected:        -1,
		},
		{
			name: "Example case",
			n:    4,
			edges: [][]int{
				{0, 1, 1},
				{0, 2, 5},
				{1, 2, 2},
				{1, 3, 1},
			},
			powerDemands:    []int{10, 12, 15, 8},
			communityDemand: 10,
			maxCapacity:     40,
			expected:        29,
		},
		{
			name: "Larger grid case",
			n:    6,
			edges: [][]int{
				{0, 1, 3},
				{0, 2, 4},
				{1, 3, 2},
				{2, 3, 3},
				{3, 4, 5},
				{4, 5, 1},
				{2, 5, 6},
			},
			powerDemands:    []int{8, 15, 7, 10, 20, 5},
			communityDemand: 12,
			maxCapacity:     50,
			expected:        35,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := OptimizeGrid(tt.n, tt.edges, tt.powerDemands, tt.communityDemand, tt.maxCapacity)
			if result != tt.expected {
				t.Fatalf("OptimizeGrid() = %d, expected %d", result, tt.expected)
			}
		})
	}
}