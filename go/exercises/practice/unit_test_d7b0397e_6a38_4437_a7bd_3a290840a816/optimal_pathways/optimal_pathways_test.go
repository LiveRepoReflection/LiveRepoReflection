package optimal_pathways

import (
	"reflect"
	"testing"
)

func TestFindOptimalPathways(t *testing.T) {
	tests := []struct {
		name         string
		n           int
		edges       [][]int
		start       int
		destinations []int
		want        []int
	}{
		{
			name: "basic test case",
			n:    5,
			edges: [][]int{
				{0, 1, 5},
				{0, 2, 3},
				{1, 3, 6},
				{2, 3, 2},
				{3, 4, 4},
			},
			start:       0,
			destinations: []int{3, 4},
			want:        []int{3, 4},
		},
		{
			name: "multiple paths available",
			n:    3,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 5},
				{0, 2, 15},
			},
			start:       0,
			destinations: []int{2},
			want:        []int{10},
		},
		{
			name: "unreachable destinations",
			n:    4,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2},
			},
			start:       0,
			destinations: []int{3},
			want:        []int{-1},
		},
		{
			name:         "empty edges",
			n:           3,
			edges:       [][]int{},
			start:       0,
			destinations: []int{1, 2},
			want:        []int{-1, -1},
		},
		{
			name: "single node self-loop",
			n:    1,
			edges: [][]int{
				{0, 0, 1},
			},
			start:       0,
			destinations: []int{0},
			want:        []int{0},
		},
		{
			name: "multiple edges between same nodes",
			n:    3,
			edges: [][]int{
				{0, 1, 5},
				{0, 1, 3},
				{1, 2, 4},
			},
			start:       0,
			destinations: []int{2},
			want:        []int{4},
		},
		{
			name: "cycle in graph",
			n:    4,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2},
				{2, 1, 3},
				{1, 3, 4},
			},
			start:       0,
			destinations: []int{3},
			want:        []int{4},
		},
		{
			name: "large congestion values",
			n:    3,
			edges: [][]int{
				{0, 1, 1000000000},
				{1, 2, 1000000000},
			},
			start:       0,
			destinations: []int{2},
			want:        []int{1000000000},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindOptimalPathways(tt.n, tt.edges, tt.start, tt.destinations)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("FindOptimalPathways() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkFindOptimalPathways(b *testing.B) {
	// Create a larger test case for benchmarking
	n := 1000
	edges := make([][]int, 5000)
	for i := 0; i < 5000; i++ {
		edges[i] = []int{i % (n - 1), (i + 1) % n, i % 100 + 1}
	}
	destinations := []int{n - 1, n/2, n/4}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindOptimalPathways(n, edges, 0, destinations)
	}
}