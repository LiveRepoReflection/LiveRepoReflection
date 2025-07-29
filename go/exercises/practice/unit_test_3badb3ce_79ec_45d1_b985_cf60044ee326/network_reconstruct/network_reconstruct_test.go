package network_reconstruct

import (
	"reflect"
	"testing"
)

func TestReconstructNetwork(t *testing.T) {
	testCases := []struct {
		description string
		localViews  [][]int
		expected    [][]bool
	}{
		{
			description: "empty input",
			localViews:  [][]int{},
			expected:    [][]bool{},
		},
		{
			description: "all empty views",
			localViews: [][]int{
				{},
				{},
				{},
			},
			expected: [][]bool{
				{false, false, false},
				{false, false, false},
				{false, false, false},
			},
		},
		{
			description: "mutual confirmation with duplicates",
			localViews: [][]int{
				{1, 2},       // Node 0's view
				{0, 2, 3},    // Node 1's view
				{0, 1, 4, 4}, // Node 2's view with duplicate '4'
				{1},          // Node 3's view
				{2},          // Node 4's view
			},
			expected: [][]bool{
				{false, true, true, false, false},
				{true, false, true, true, false},
				{true, true, false, false, true},
				{false, true, false, false, false},
				{false, false, true, false, false},
			},
		},
		{
			description: "self loops ignored",
			localViews: [][]int{
				{0, 1},
				{1, 0},
			},
			expected: [][]bool{
				{false, true},
				{true, false},
			},
		},
		{
			description: "isolated and one-sided view",
			localViews: [][]int{
				{},      // Node 0 isolated
				{2},     // Node 1 sees Node 2, but not reciprocated
				{},      // Node 2 does not see Node 1
				{3, 3},  // Node 3 with duplicate self loops only
			},
			expected: [][]bool{
				{false, false, false, false},
				{false, false, false, false},
				{false, false, false, false},
				{false, false, false, false},
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := ReconstructNetwork(tc.localViews)
			if !reflect.DeepEqual(actual, tc.expected) {
				t.Fatalf("For localViews %v\nexpected: %v\ngot: %v", tc.localViews, tc.expected, actual)
			}
		})
	}
}

func BenchmarkReconstructNetwork(b *testing.B) {
	// A benchmark input with 1000 nodes, where each node randomly claims up to 10 neighbors.
	// For test purposes, we use a deterministic pattern.
	n := 1000
	localViews := make([][]int, n)
	for i := 0; i < n; i++ {
		// Each node lists its next 10 nodes (wrap around) as its neighbors.
		for j := 1; j <= 10; j++ {
			localViews[i] = append(localViews[i], (i+j)%n)
		}
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ReconstructNetwork(localViews)
	}
}