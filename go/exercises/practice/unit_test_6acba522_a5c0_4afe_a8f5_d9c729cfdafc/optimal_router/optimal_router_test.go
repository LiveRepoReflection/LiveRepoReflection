package optimal_router

import (
	"testing"
)

func TestOptimalRouter(t *testing.T) {
	tests := []struct {
		name     string
		N        int
		M        int
		links    [][]int
		queries  [][]int
		expected []int
	}{
		{
			name: "basic case with two possible paths",
			N:    4,
			M:    5,
			links: [][]int{
				{0, 1, 10},
				{0, 2, 15},
				{1, 2, 5},
				{1, 3, 20},
				{2, 3, 10},
			},
			queries: [][]int{
				{0, 3, 40},
				{0, 3, 35},
			},
			expected: []int{1000000, 1000000},
		},
		{
			name: "direct path meets deadline",
			N:    3,
			M:    3,
			links: [][]int{
				{0, 1, 5},
				{1, 2, 5},
				{0, 2, 15},
			},
			queries: [][]int{
				{0, 2, 14},
			},
			expected: []int{1000000},
		},
		{
			name: "no path meets deadline",
			N:    3,
			M:    3,
			links: [][]int{
				{0, 1, 5},
				{1, 2, 5},
				{0, 2, 15},
			},
			queries: [][]int{
				{0, 2, 9},
			},
			expected: []int{0},
		},
		{
			name: "large network with multiple queries",
			N:    5,
			M:    7,
			links: [][]int{
				{0, 1, 2},
				{0, 2, 4},
				{1, 2, 1},
				{1, 3, 7},
				{2, 3, 3},
				{2, 4, 5},
				{3, 4, 2},
			},
			queries: [][]int{
				{0, 4, 10},
				{0, 3, 6},
				{1, 4, 8},
			},
			expected: []int{1000000, 1000000, 1000000},
		},
		{
			name: "disconnected graph",
			N:    4,
			M:    2,
			links: [][]int{
				{0, 1, 3},
				{2, 3, 4},
			},
			queries: [][]int{
				{0, 3, 10},
			},
			expected: []int{0},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalRouter(tt.N, tt.M, tt.links, tt.queries)
			if len(got) != len(tt.expected) {
				t.Errorf("OptimalRouter() result length = %v, want %v", len(got), len(tt.expected))
				return
			}
			for i := range got {
				if got[i] != tt.expected[i] {
					t.Errorf("OptimalRouter() result[%d] = %v, want %v", i, got[i], tt.expected[i])
				}
			}
		})
	}
}

func BenchmarkOptimalRouter(b *testing.B) {
	N := 100
	M := 500
	links := make([][]int, M)
	for i := 0; i < M; i++ {
		u := i % N
		v := (i + 1) % N
		latency := i%10 + 1
		links[i] = []int{u, v, latency}
	}
	queries := [][]int{{0, N-1, 100}, {0, N/2, 50}}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalRouter(N, M, links, queries)
	}
}