package packet_routing

import (
	"reflect"
	"testing"
)

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		name     string
		N        int
		edges    [][2]int
		L        []int
		Q        int
		queries  [][2]int
		expected [][]int
	}{
		{
			name:  "basic test",
			N:     5,
			edges: [][2]int{{0, 1}, {0, 2}, {1, 2}, {1, 3}, {2, 4}, {3, 4}},
			L:     []int{1, 2, 3, 4, 5},
			Q:     2,
			queries: [][2]int{
				{0, 4},
				{3, 2},
			},
			expected: [][]int{
				{0, 2, 4},
				{3, 1, 2},
			},
		},
		{
			name:  "disconnected graph",
			N:     4,
			edges: [][2]int{{0, 1}, {2, 3}},
			L:     []int{1, 2, 3, 4},
			Q:     2,
			queries: [][2]int{
				{0, 3},
				{1, 2},
			},
			expected: [][]int{
				{},
				{},
			},
		},
		{
			name:  "single node",
			N:     1,
			edges: [][2]int{},
			L:     []int{0},
			Q:     1,
			queries: [][2]int{
				{0, 0},
			},
			expected: [][]int{
				{0},
			},
		},
		{
			name:  "multiple equal paths",
			N:     4,
			edges: [][2]int{{0, 1}, {0, 2}, {1, 3}, {2, 3}},
			L:     []int{1, 1, 1, 1},
			Q:     1,
			queries: [][2]int{
				{0, 3},
			},
			expected: [][]int{
				{0, 1, 3},
			},
		},
		{
			name:  "high latency difference",
			N:     3,
			edges: [][2]int{{0, 1}, {1, 2}},
			L:     []int{1, 100, 1},
			Q:     1,
			queries: [][2]int{
				{0, 2},
			},
			expected: [][]int{
				{0, 1, 2},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindOptimalPaths(tt.N, tt.edges, tt.L, tt.Q, tt.queries)
			if !reflect.DeepEqual(got, tt.expected) {
				t.Errorf("FindOptimalPaths() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkFindOptimalPaths(b *testing.B) {
	N := 1000
	edges := make([][2]int, 0)
	for i := 0; i < N-1; i++ {
		edges = append(edges, [2]int{i, i + 1})
	}
	L := make([]int, N)
	for i := range L {
		L[i] = i % 10
	}
	Q := 10
	queries := make([][2]int, Q)
	for i := 0; i < Q; i++ {
		queries[i] = [2]int{0, N - 1}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindOptimalPaths(N, edges, L, Q, queries)
	}
}