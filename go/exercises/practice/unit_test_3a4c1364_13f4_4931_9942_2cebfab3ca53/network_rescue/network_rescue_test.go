package network_rescue

import (
	"testing"
)

type testCase struct {
	description      string
	n                int
	edges            [][]int
	affectedServices []int
	recoveryCosts    []int
	expected         int
}

func TestOptimalPartitioning(t *testing.T) {
	testCases := []testCase{
		{
			description:      "Example test: removal splits graph into 3 clusters",
			n:                5,
			edges:            [][]int{{0, 1}, {1, 2}, {3, 4}},
			affectedServices: []int{1},
			recoveryCosts:    []int{10, 20, 30, 40, 50},
			expected:         130,
		},
		{
			description:      "Fully connected graph with no affected nodes",
			n:                4,
			edges:            [][]int{{0, 1}, {1, 2}, {2, 3}, {3, 0}},
			affectedServices: []int{},
			recoveryCosts:    []int{5, 10, 15, 20},
			expected:         50,
		},
		{
			description:      "All services affected",
			n:                4,
			edges:            [][]int{{0, 1}, {1, 2}, {2, 3}},
			affectedServices: []int{0, 1, 2, 3},
			recoveryCosts:    []int{10, 20, 30, 40},
			expected:         0,
		},
		{
			description:      "Already disconnected graph with no affected nodes",
			n:                3,
			edges:            [][]int{},
			affectedServices: []int{},
			recoveryCosts:    []int{1, 2, 3},
			expected:         6,
		},
		{
			description:      "Chain graph with affected nodes splitting into two clusters",
			n:                6,
			edges:            [][]int{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}},
			affectedServices: []int{2, 3},
			recoveryCosts:    []int{3, 4, 5, 6, 7, 8},
			expected:         22,
		},
		{
			description:      "Graph becomes fully disconnected after removal",
			n:                5,
			edges:            [][]int{{0, 1}, {1, 2}, {2, 3}, {3, 4}},
			affectedServices: []int{1, 3},
			recoveryCosts:    []int{10, 20, 30, 40, 50},
			expected:         90,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := OptimalPartitioning(tc.n, tc.edges, tc.affectedServices, tc.recoveryCosts)
			if result != tc.expected {
				t.Errorf("Test %q failed: expected %d, got %d", tc.description, tc.expected, result)
			}
		})
	}
}