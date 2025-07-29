package airport_placement

import (
	"testing"
)

func TestOptimalAirportPlacement(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		edges    [][]int
		expected int
	}{
		{
			name:     "simple 4-node graph",
			n:        4,
			edges:    [][]int{{0, 1, 1}, {0, 2, 5}, {1, 2, 2}, {1, 3, 10}, {2, 3, 1}},
			expected: 1,
		},
		{
			name:     "single node",
			n:        1,
			edges:    [][]int{},
			expected: 0,
		},
		{
			name:     "linear graph",
			n:        5,
			edges:    [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}, {3, 4, 1}},
			expected: 2,
		},
		{
			name:     "star graph",
			n:        5,
			edges:    [][]int{{0, 1, 1}, {0, 2, 1}, {0, 3, 1}, {0, 4, 1}},
			expected: 0,
		},
		{
			name:     "tie breaker",
			n:        3,
			edges:    [][]int{{0, 1, 1}, {1, 2, 1}},
			expected: 1,
		},
		{
			name:     "complex graph",
			n:        6,
			edges:    [][]int{{0, 1, 3}, {0, 2, 5}, {1, 3, 2}, {2, 3, 1}, {3, 4, 4}, {4, 5, 2}},
			expected: 3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalAirportPlacement(tt.n, tt.edges)
			if got != tt.expected {
				t.Errorf("OptimalAirportPlacement() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkOptimalAirportPlacement(b *testing.B) {
	n := 1000
	edges := make([][]int, 0)
	for i := 0; i < n-1; i++ {
		edges = append(edges, []int{i, i + 1, 1})
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalAirportPlacement(n, edges)
	}
}