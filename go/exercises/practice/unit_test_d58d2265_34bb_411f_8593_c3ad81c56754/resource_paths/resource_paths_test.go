package resource_paths

import (
	"reflect"
	"testing"
)

type testCase struct {
	description string
	n           int
	edges       [][]int // each element: [u, v, w, c]
	sources     []int
	capacity    []int
	expected    []int
}

func TestResourcePaths(t *testing.T) {
	testCases := []testCase{
		{
			description: "Example 1 - Basic Test",
			n:           5,
			edges: [][]int{
				{0, 1, 5, 2},
				{0, 2, 3, 1},
				{1, 3, 6, 3},
				{2, 3, 2, 1},
				{3, 4, 4, 2},
				{2, 4, 8, 4},
			},
			sources:  []int{0},
			capacity: []int{10, 5, 5, 5, 10},
			expected: []int{0, 5, 3, 5, 9},
		},
		{
			description: "Example 2 - Insufficient Resource",
			n:           3,
			edges: [][]int{
				{0, 1, 1, 5},
				{1, 2, 1, 5},
				{0, 2, 5, 1},
			},
			sources:  []int{0},
			capacity: []int{10, 4, 10},
			expected: []int{0, -1, 5},
		},
		{
			description: "Example 3 - Multiple Paths and Constraints",
			n:           4,
			edges: [][]int{
				{0, 1, 1, 1},
				{1, 2, 1, 1},
				{2, 3, 1, 1},
				{0, 3, 5, 5},
			},
			sources:  []int{0},
			capacity: []int{10, 2, 2, 2},
			expected: []int{0, 1, 2, -1},
		},
		{
			description: "Multi-source Test",
			n:           6,
			edges: [][]int{
				{0, 1, 2, 1},
				{1, 2, 2, 1},
				{2, 3, 2, 2},
				{3, 4, 3, 3},
				{4, 5, 4, 1},
				{1, 5, 10, 4},
			},
			sources:  []int{0, 3},
			capacity: []int{10, 3, 3, 5, 6, 7},
			expected: []int{0, 2, 4, 0, 3, 7},
		},
		{
			description: "Single Node Graph",
			n:           1,
			edges:       [][]int{},
			sources:     []int{0},
			capacity:    []int{0},
			expected:    []int{0},
		},
		{
			description: "Edge with Insufficient Capacity",
			n:           2,
			edges: [][]int{
				{0, 1, 1, 10},
			},
			sources:  []int{0},
			capacity: []int{100, 5},
			expected: []int{0, -1},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := ResourcePaths(tc.n, tc.edges, tc.sources, tc.capacity)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Fatalf("For %q, expected %v but got %v", tc.description, tc.expected, result)
			}
		})
	}
}

func BenchmarkResourcePaths(b *testing.B) {
	// Use one of the larger cases for benchmark.
	n := 10000
	edges := make([][]int, 0, 20000)
	// Form a chain of nodes
	for i := 0; i < n-1; i++ {
		edges = append(edges, []int{i, i + 1, 1, 1})
	}
	sources := []int{0}
	capacity := make([]int, n)
	for i := 0; i < n; i++ {
		capacity[i] = n // large enough to avoid resource constraints on chain
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ResourcePaths(n, edges, sources, capacity)
	}
}