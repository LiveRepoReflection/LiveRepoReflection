package mst_critical

import (
	"testing"
)

func TestMSTCritical(t *testing.T) {
	testCases := []struct {
		description   string
		n             int
		edges         [][]int
		criticalNodes []int
		expected      int
	}{
		{
			description:   "Single node",
			n:             1,
			edges:         [][]int{},
			criticalNodes: []int{0},
			expected:      0,
		},
		{
			description:   "Two nodes, simple edge",
			n:             2,
			edges:         [][]int{{0, 1, 5}},
			criticalNodes: []int{0, 1},
			expected:      5,
		},
		{
			description:   "Three nodes with connected critical nodes",
			n:             3,
			edges:         [][]int{{0, 1, 3}, {1, 2, 4}, {0, 2, 7}},
			criticalNodes: []int{0, 2},
			expected:      7,
		},
		{
			description:   "Example graph with multiple edges",
			n:             6,
			edges:         [][]int{{0, 1, 4}, {0, 2, 6}, {1, 2, 1}, {1, 3, 5}, {2, 3, 7}, {2, 4, 9}, {3, 4, 3}, {3, 5, 2}, {4, 5, 8}},
			criticalNodes: []int{0, 4, 5},
			expected:      17,
		},
		{
			description:   "Graph with tie conditions",
			n:             4,
			edges:         [][]int{{0, 1, 10}, {0, 2, 6}, {0, 3, 5}, {1, 3, 15}, {2, 3, 4}},
			criticalNodes: []int{1, 2},
			expected:      19,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := MSTCritical(tc.n, tc.edges, tc.criticalNodes)
			if result != tc.expected {
				t.Errorf("Test %s failed: expected %d, got %d", tc.description, tc.expected, result)
			}
		})
	}
}

func BenchmarkMSTCritical(b *testing.B) {
	// Generate a chain graph: 0-1, 1-2, ..., (n-2)-(n-1) with cost 1 each.
	n := 1000
	edges := make([][]int, n-1)
	for i := 0; i < n-1; i++ {
		edges[i] = []int{i, i + 1, 1}
	}
	// Choose critical nodes as the first and the last nodes.
	criticalNodes := []int{0, n - 1}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MSTCritical(n, edges, criticalNodes)
	}
}