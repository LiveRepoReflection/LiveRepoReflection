package network_hops

import (
	"testing"
)

func TestNetworkHops(t *testing.T) {
	tests := []struct {
		name     string
		N        int
		edges    [][]int
		S        int
		D        int
		L        int
		expected int
	}{
		{
			name:     "single node with zero latency",
			N:        1,
			edges:    [][]int{},
			S:        0,
			D:        0,
			L:        0,
			expected: 0,
		},
		{
			name:     "single node with insufficient latency",
			N:        1,
			edges:    [][]int{},
			S:        0,
			D:        0,
			L:        -1,
			expected: -1,
		},
		{
			name: "simple two node path",
			N:    2,
			edges: [][]int{
				{0, 1, 5},
			},
			S:        0,
			D:        1,
			L:        10,
			expected: 1,
		},
		{
			name: "path exceeds latency constraint",
			N:    2,
			edges: [][]int{
				{0, 1, 15},
			},
			S:        0,
			D:        1,
			L:        10,
			expected: -1,
		},
		{
			name: "multiple paths with different hops",
			N:    4,
			edges: [][]int{
				{0, 1, 2},
				{1, 3, 3},
				{0, 2, 1},
				{2, 3, 2},
			},
			S:        0,
			D:        3,
			L:        4,
			expected: 2,
		},
		{
			name: "disconnected graph",
			N:    3,
			edges: [][]int{
				{0, 1, 1},
			},
			S:        0,
			D:        2,
			L:        10,
			expected: -1,
		},
		{
			name: "graph with cycles",
			N:    3,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{2, 0, 1},
			},
			S:        0,
			D:        2,
			L:        10,
			expected: 2,
		},
		{
			name: "multiple edges between nodes",
			N:    2,
			edges: [][]int{
				{0, 1, 10},
				{0, 1, 5},
			},
			S:        0,
			D:        1,
			L:        7,
			expected: 1,
		},
		{
			name: "large latency constraint",
			N:    4,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{2, 3, 1},
				{0, 3, 10},
			},
			S:        0,
			D:        3,
			L:        100,
			expected: 1,
		},
		{
			name: "minimum hops with tight latency",
			N:    5,
			edges: [][]int{
				{0, 1, 1},
				{1, 4, 1},
				{0, 2, 1},
				{2, 3, 1},
				{3, 4, 1},
			},
			S:        0,
			D:        4,
			L:        2,
			expected: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindMinHops(tt.N, tt.edges, tt.S, tt.D, tt.L)
			if got != tt.expected {
				t.Errorf("FindMinHops() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkFindMinHops(b *testing.B) {
	N := 1000
	edges := make([][]int, 0, N*2)
	for i := 0; i < N-1; i++ {
		edges = append(edges, []int{i, i + 1, 1})
		edges = append(edges, []int{i, (i + 2) % N, 2})
	}
	S := 0
	D := N - 1
	L := N * 2

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindMinHops(N, edges, S, D, L)
	}
}