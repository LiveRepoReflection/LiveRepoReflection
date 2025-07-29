package network_pathfinder

import (
	"reflect"
	"testing"
)

func TestFindPaths(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		cables   [][]int
		queries  [][]int
		expected []int
	}{
		{
			name:   "basic_example",
			n:      5,
			cables: [][]int{{0, 1, 5}, {0, 2, 3}, {1, 3, 2}, {2, 3, 4}, {3, 4, 1}},
			queries: [][]int{
				{0, 3, 2, 10},
				{0, 4, 3, 12},
			},
			expected: []int{2, 2},
		},
		{
			name:     "source_equals_destination",
			n:        3,
			cables:   [][]int{{0, 1, 5}, {1, 2, 4}},
			queries:  [][]int{{1, 1, 1, 10}},
			expected: []int{1},
		},
		{
			name:     "no_path_available",
			n:        4,
			cables:   [][]int{{0, 1, 5}},
			queries:  [][]int{{0, 3, 2, 10}},
			expected: []int{0},
		},
		{
			name:   "multiple_paths",
			n:      6,
			cables: [][]int{{0, 1, 1}, {0, 2, 2}, {1, 3, 2}, {2, 3, 1}, {3, 4, 3}, {3, 5, 2}, {4, 5, 1}},
			queries: [][]int{
				{0, 5, 3, 6},
			},
			expected: []int{2},
		},
		{
			name:   "diamond_graph",
			n:      4,
			cables: [][]int{{0, 1, 3}, {1, 3, 3}, {0, 2, 2}, {2, 3, 2}, {1, 2, 1}},
			queries: [][]int{
				{0, 3, 3, 7},
			},
			expected: []int{4},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := findPaths(tc.n, tc.cables, tc.queries)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("Test case '%s' failed. Expected %v, got %v", tc.name, tc.expected, result)
			}
		})
	}
}

func BenchmarkFindPaths(b *testing.B) {
	n := 6
	cables := [][]int{{0, 1, 1}, {0, 2, 2}, {1, 3, 2}, {2, 3, 1}, {3, 4, 3}, {3, 5, 2}, {4, 5, 1}}
	queries := [][]int{{0, 5, 3, 6}}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = findPaths(n, cables, queries)
	}
}