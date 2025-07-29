package k_color_graph_test

import (
	"testing"

	"k_color_graph"
)

func TestIsKColorable(t *testing.T) {
	testCases := []struct {
		name   string
		n      int
		edges  [][]int
		k      int
		expect bool
	}{
		{
			name:   "empty graph",
			n:      0,
			edges:  [][]int{},
			k:      1,
			expect: true,
		},
		{
			name:   "graph with no edges",
			n:      3,
			edges:  [][]int{},
			k:      1,
			expect: true,
		},
		{
			name:   "single edge with k=1 fails",
			n:      2,
			edges:  [][]int{{0, 1}},
			k:      1,
			expect: false,
		},
		{
			name:   "single edge with k=2 succeeds",
			n:      2,
			edges:  [][]int{{0, 1}},
			k:      2,
			expect: true,
		},
		{
			name:   "self loop always fails",
			n:      3,
			edges:  [][]int{{1, 1}},
			k:      2,
			expect: false,
		},
		{
			name:   "triangle graph with k=2 fails",
			n:      3,
			edges:  [][]int{{0, 1}, {1, 2}, {2, 0}},
			k:      2,
			expect: false,
		},
		{
			name:   "triangle graph with k=3 succeeds",
			n:      3,
			edges:  [][]int{{0, 1}, {1, 2}, {2, 0}},
			k:      3,
			expect: true,
		},
		{
			name:   "complex graph not k-colorable with 2 colors",
			n:      4,
			edges:  [][]int{{0, 1}, {0, 2}, {1, 2}, {2, 3}},
			k:      2,
			expect: false,
		},
		{
			name:   "complex graph k-colorable with 3 colors",
			n:      4,
			edges:  [][]int{{0, 1}, {0, 2}, {1, 2}, {2, 3}},
			k:      3,
			expect: true,
		},
		{
			name:   "star graph with k=1 fails",
			n:      5,
			edges:  [][]int{{0, 1}, {0, 2}, {0, 3}, {0, 4}},
			k:      1,
			expect: false,
		},
		{
			name:   "star graph with k=2 succeeds",
			n:      5,
			edges:  [][]int{{0, 1}, {0, 2}, {0, 3}, {0, 4}},
			k:      2,
			expect: true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := k_color_graph.IsKColorable(tc.n, tc.edges, tc.k)
			if result != tc.expect {
				t.Errorf("IsKColorable(%d, %v, %d) = %v; want %v", tc.n, tc.edges, tc.k, result, tc.expect)
			}
		})
	}
}