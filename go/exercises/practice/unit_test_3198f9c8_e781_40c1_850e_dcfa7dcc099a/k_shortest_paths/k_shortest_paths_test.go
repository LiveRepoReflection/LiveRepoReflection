package k_shortest_paths

import (
	"reflect"
	"sort"
	"testing"
)

func TestKShortestPaths(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		graph    [][][2]int
		start    int
		end      int
		k        int
		expected []int
	}{
		{
			name: "basic case",
			n:    5,
			graph: [][][2]int{
				{{1, 2}, {2, 4}}, // Node 0
				{{2, 1}, {3, 7}}, // Node 1
				{{3, 3}},         // Node 2
				{{4, 1}},         // Node 3
				{},               // Node 4
			},
			start:    0,
			end:      4,
			k:        3,
			expected: []int{7, 8, 10},
		},
		{
			name: "k greater than available",
			n:    4,
			graph: [][][2]int{
				{{1, 1}}, // Node 0
				{{2, 1}}, // Node 1
				{{3, 1}}, // Node 2
				{},       // Node 3
			},
			start:    0,
			end:      3,
			k:        5,
			expected: []int{3},
		},
		{
			name: "no available path",
			n:    3,
			graph: [][][2]int{
				{{1, 1}}, // Node 0
				{},       // Node 1
				{},       // Node 2
			},
			start:    0,
			end:      2,
			k:        2,
			expected: []int{},
		},
		{
			name: "cycle in graph",
			n:    4,
			graph: [][][2]int{
				{{1, 1}, {2, 5}}, // Node 0
				{{0, 1}, {2, 2}, {3, 1}}, // Node 1
				{{3, 1}},                 // Node 2
				{},                       // Node 3
			},
			start:    0,
			end:      3,
			k:        4,
			expected: []int{2, 4, 4, 6},
		},
		{
			name: "self loop",
			n:    3,
			graph: [][][2]int{
				{{0, 1}, {1, 2}}, // Node 0
				{{2, 1}},         // Node 1
				{},               // Node 2
			},
			start:    0,
			end:      2,
			k:        3,
			expected: []int{3, 4, 5},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := KShortestPaths(tc.n, tc.graph, tc.start, tc.end, tc.k)
			// Sorting since order of paths may differ based on the implementation
			sortedResult := append([]int(nil), result...)
			sort.Ints(sortedResult)
			sortedExpected := append([]int(nil), tc.expected...)
			sort.Ints(sortedExpected)
			if !reflect.DeepEqual(sortedResult, sortedExpected) {
				t.Errorf("%s: expected %v, got %v", tc.name, sortedExpected, sortedResult)
			}
		})
	}
}

func BenchmarkKShortestPaths(b *testing.B) {
	// Construct a moderately sized graph for benchmarking purposes.
	n := 500
	graph := make([][][2]int, n)
	for i := 0; i < n-1; i++ {
		graph[i] = append(graph[i], [2]int{i + 1, (i % 10) + 1})
		// Adding a self loop to introduce cycles.
		graph[i] = append(graph[i], [2]int{i, 1})
	}
	// Last node has no outgoing edges.
	start := 0
	end := n - 1
	k := 10

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = KShortestPaths(n, graph, start, end, k)
	}
}