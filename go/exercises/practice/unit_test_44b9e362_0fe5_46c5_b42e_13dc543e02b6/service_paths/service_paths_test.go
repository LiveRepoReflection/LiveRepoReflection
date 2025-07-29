package service_paths

import (
	"testing"
)

func TestFindKCheapestPaths(t *testing.T) {
	tests := []struct {
		name       string
		numServices int
		edges      [][3]int
		requests   [][2]int
		k          int
		expected   [][]int
	}{
		{
			name:       "basic example",
			numServices: 5,
			edges:      [][3]int{{0, 1, 5}, {0, 2, 3}, {1, 3, 6}, {2, 3, 2}, {3, 4, 1}, {2, 4, 4}, {1, 4, 2}},
			requests:   [][2]int{{0, 4}, {1, 4}},
			k:          2,
			expected:   [][]int{{6, 7}, {2, 7}},
		},
		{
			name:       "no path exists",
			numServices: 3,
			edges:      [][3]int{{0, 1, 1}, {1, 2, 1}},
			requests:   [][2]int{{2, 0}},
			k:          1,
			expected:   [][]int{{}},
		},
		{
			name:       "same start and end",
			numServices: 3,
			edges:      [][3]int{{0, 1, 1}, {1, 2, 1}},
			requests:   [][2]int{{1, 1}},
			k:          1,
			expected:   [][]int{{0}},
		},
		{
			name:       "multiple paths with same cost",
			numServices: 4,
			edges:      [][3]int{{0, 1, 2}, {0, 2, 2}, {1, 3, 3}, {2, 3, 3}},
			requests:   [][2]int{{0, 3}},
			k:          3,
			expected:   [][]int{{5, 5}},
		},
		{
			name:       "disconnected graph",
			numServices: 4,
			edges:      [][3]int{{0, 1, 1}, {2, 3, 1}},
			requests:   [][2]int{{0, 3}, {1, 2}},
			k:          1,
			expected:   [][]int{{}, {}},
		},
		{
			name:       "more requests than k paths",
			numServices: 3,
			edges:      [][3]int{{0, 1, 1}, {0, 1, 2}, {0, 1, 3}, {1, 2, 1}},
			requests:   [][2]int{{0, 1}, {0, 2}},
			k:          2,
			expected:   [][]int{{1, 2}, {2, 3}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := FindKCheapestPaths(tt.numServices, tt.edges, tt.requests, tt.k)
			if !compareResults(result, tt.expected) {
				t.Errorf("FindKCheapestPaths() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func compareResults(a, b [][]int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if len(a[i]) != len(b[i]) {
			return false
		}
		for j := range a[i] {
			if a[i][j] != b[i][j] {
				return false
			}
		}
	}
	return true
}