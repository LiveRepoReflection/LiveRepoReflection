package network_reconfigure

import "testing"

func TestReconfigureNetwork(t *testing.T) {
	tests := []struct {
		name            string
		adjMatrix       [][]bool
		targetAdjMatrix [][]bool
		costAdd         [][]int
		costRemove      [][]int
		expected        int
	}{
		{
			name: "Remove single edge",
			adjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			targetAdjMatrix: [][]bool{
				{false, false},
				{false, false},
			},
			costAdd: [][]int{
				{0, 5},
				{5, 0},
			},
			costRemove: [][]int{
				{0, 2},
				{2, 0},
			},
			expected: 2,
		},
		{
			name: "Add single edge",
			adjMatrix: [][]bool{
				{false, false},
				{false, false},
			},
			targetAdjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			costAdd: [][]int{
				{0, 5},
				{5, 0},
			},
			costRemove: [][]int{
				{0, 2},
				{2, 0},
			},
			expected: 5,
		},
		{
			name: "Mixed operations 3 nodes",
			adjMatrix: [][]bool{
				{false, true, true},
				{true, false, false},
				{true, false, false},
			},
			targetAdjMatrix: [][]bool{
				{false, false, true},
				{false, false, true},
				{true, true, false},
			},
			costAdd: [][]int{
				{0, 1, 0},
				{1, 0, 4},
				{0, 4, 0},
			},
			costRemove: [][]int{
				{0, 3, 10},
				{3, 0, 1},
				{10, 1, 0},
			},
			// Remove edge between node 0 and 1 (cost 3) and add edge between node 1 and 2 (cost 4) => total cost = 7.
			expected: 7,
		},
		{
			name: "Multiple operations 4 nodes",
			adjMatrix: [][]bool{
				{false, true, false, true},
				{true, false, false, false},
				{false, false, false, false},
				{true, false, false, false},
			},
			targetAdjMatrix: [][]bool{
				{false, true, true, false},
				{true, false, true, true},
				{true, true, false, true},
				{false, true, true, false},
			},
			costAdd: [][]int{
				{0, 0, 1, 0},
				{0, 0, 2, 3},
				{1, 2, 0, 4},
				{0, 3, 4, 0},
			},
			costRemove: [][]int{
				{0, 0, 0, 2},
				{0, 0, 0, 0},
				{0, 0, 0, 0},
				{2, 0, 0, 0},
			},
			// Add edges: 0-2 (1), 1-2 (2), 1-3 (3), 2-3 (4); Remove edge: 0-3 (2) => total cost = 12.
			expected: 12,
		},
		{
			name: "No change needed",
			adjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			targetAdjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			costAdd: [][]int{
				{0, 10},
				{10, 0},
			},
			costRemove: [][]int{
				{0, 5},
				{5, 0},
			},
			expected: 0,
		},
		{
			name: "Operation impossible due to add restriction",
			adjMatrix: [][]bool{
				{false, false},
				{false, false},
			},
			targetAdjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			costAdd: [][]int{
				{0, -1},
				{-1, 0},
			},
			costRemove: [][]int{
				{0, 2},
				{2, 0},
			},
			// In this case, adding an edge is impossible, so expect -1.
			expected: -1,
		},
		{
			name: "Operation impossible due to remove restriction",
			adjMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			targetAdjMatrix: [][]bool{
				{false, false},
				{false, false},
			},
			costAdd: [][]int{
				{0, 5},
				{5, 0},
			},
			costRemove: [][]int{
				{0, -1},
				{-1, 0},
			},
			// In this case, removing an edge is impossible, so expect -1.
			expected: -1,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := ReconfigureNetwork(tc.adjMatrix, tc.targetAdjMatrix, tc.costAdd, tc.costRemove)
			if result != tc.expected {
				t.Errorf("Test %s failed: expected %d, got %d", tc.name, tc.expected, result)
			}
		})
	}
}

func BenchmarkReconfigureNetwork(b *testing.B) {
	adjMatrix := [][]bool{
		{false, true, false, true},
		{true, false, false, false},
		{false, false, false, false},
		{true, false, false, false},
	}
	targetAdjMatrix := [][]bool{
		{false, true, true, false},
		{true, false, true, true},
		{true, true, false, true},
		{false, true, true, false},
	}
	costAdd := [][]int{
		{0, 0, 1, 0},
		{0, 0, 2, 3},
		{1, 2, 0, 4},
		{0, 3, 4, 0},
	}
	costRemove := [][]int{
		{0, 0, 0, 2},
		{0, 0, 0, 0},
		{0, 0, 0, 0},
		{2, 0, 0, 0},
	}

	for i := 0; i < b.N; i++ {
		_ = ReconfigureNetwork(adjMatrix, targetAdjMatrix, costAdd, costRemove)
	}
}