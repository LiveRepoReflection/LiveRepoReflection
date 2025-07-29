package max_network_flow

import (
	"testing"
)

func TestMaxFlow(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		edges    [][]int
		source   int
		sink     int
		expected int
	}{
		{
			name: "simple network",
			n:    4,
			edges: [][]int{
				{0, 1, 3},
				{0, 2, 2},
				{1, 2, 5},
				{1, 3, 2},
				{2, 3, 3},
			},
			source:   0,
			sink:     3,
			expected: 5,
		},
		{
			name: "disconnected graph",
			n:    4,
			edges: [][]int{
				{0, 1, 1},
				{2, 3, 1},
			},
			source:   0,
			sink:     3,
			expected: 0,
		},
		{
			name: "complex network",
			n:    6,
			edges: [][]int{
				{0, 1, 16},
				{0, 2, 13},
				{1, 2, 10},
				{1, 3, 12},
				{2, 1, 4},
				{2, 4, 14},
				{3, 2, 9},
				{3, 5, 20},
				{4, 3, 7},
				{4, 5, 4},
			},
			source:   0,
			sink:     5,
			expected: 23,
		},
		{
			name: "invalid source",
			n:    3,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
			},
			source:   -1,
			sink:     2,
			expected: -1,
		},
		{
			name: "invalid sink",
			n:    3,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
			},
			source:   0,
			sink:     3,
			expected: -1,
		},
		{
			name: "source equals sink",
			n:    3,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
			},
			source:   1,
			sink:     1,
			expected: 0,
		},
		{
			name: "zero capacity edges",
			n:    3,
			edges: [][]int{
				{0, 1, 0},
				{1, 2, 5},
			},
			source:   0,
			sink:     2,
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actual := MaxFlow(tt.n, tt.edges, tt.source, tt.sink)
			if actual != tt.expected {
				t.Errorf("MaxFlow(%d, %v, %d, %d) = %d, want %d",
					tt.n, tt.edges, tt.source, tt.sink, actual, tt.expected)
			}
		})
	}
}

func BenchmarkMaxFlow(b *testing.B) {
	n := 100
	edges := make([][]int, 0)
	for i := 0; i < n-1; i++ {
		edges = append(edges, []int{i, i + 1, 1000000000})
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MaxFlow(n, edges, 0, n-1)
	}
}