package network_balance

import (
	"reflect"
	"testing"
)

type testCase struct {
	name     string
	N        int
	capacity []int
	load     []int
	edges    [][]int
	expected int
}

func TestOptimizeNetwork(t *testing.T) {
	tests := []testCase{
		{
			name:     "SingleServer",
			N:        1,
			capacity: []int{10},
			load:     []int{5},
			edges:    [][]int{},
			expected: 5,
		},
		{
			name:     "TwoServers",
			N:        2,
			capacity: []int{10, 10},
			load:     []int{8, 3},
			edges:    [][]int{{0, 1}},
			expected: 6,
		},
		{
			name:     "ThreeNodesChain",
			N:        3,
			capacity: []int{10, 10, 10},
			load:     []int{10, 0, 0},
			edges:    [][]int{{0, 1}, {1, 2}},
			expected: 4,
		},
		{
			name:     "FourNodesSpanningTree",
			N:        4,
			capacity: []int{5, 10, 8, 6},
			load:     []int{5, 7, 0, 0},
			edges:    [][]int{{0, 1}, {1, 2}, {1, 3}},
			expected: 3,
		},
		{
			name:     "ComplexGraph",
			N:        5,
			capacity: []int{10, 9, 8, 7, 6},
			load:     []int{9, 3, 2, 1, 0},
			edges:    [][]int{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}},
			expected: 3,
		},
		{
			name:     "EdgeCaseFullCapacity",
			N:        3,
			capacity: []int{5, 5, 5},
			load:     []int{5, 5, 0},
			edges:    [][]int{{0, 1}, {1, 2}},
			expected: 4,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := OptimizeNetwork(tc.N, tc.capacity, tc.load, tc.edges)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Fatalf("For test %q, expected result %d, but got %d", tc.name, tc.expected, result)
			}
		})
	}
}