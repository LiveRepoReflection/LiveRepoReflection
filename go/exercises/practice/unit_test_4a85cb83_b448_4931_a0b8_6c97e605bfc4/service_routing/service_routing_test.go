package service_routing

import (
	"reflect"
	"testing"
)

func TestRouteRequest(t *testing.T) {
	tests := []struct {
		name          string
		N             int
		connections   [][]bool
		capacities    []int
		entry         int
		target        int
		latencyMatrix [][]int
		expectEmpty   bool
		expectedPath  []int
	}{
		{
			name: "simple valid path",
			N:    4,
			connections: [][]bool{
				{false, true, false, false},
				{false, false, true, true},
				{false, false, false, true},
				{false, false, false, false},
			},
			capacities: []int{1, 1, 1, 1},
			entry:      0,
			target:     3,
			latencyMatrix: [][]int{
				{0, 1, 0, 0},
				{0, 0, 1, 2},
				{0, 0, 0, 1},
				{0, 0, 0, 0},
			},
			expectEmpty:  false,
			// The optimal path is [0,1,3] with latency 1+2=3, versus [0,1,2,3] with latency 1+1+1=3. Both are same latency.
			// We accept either valid optimal path.
			// We choose [0,1,3] as expected for this test.
			expectedPath: []int{0, 1, 3},
		},
		{
			name: "entry equals target",
			N:    3,
			connections: [][]bool{
				{false, true, false},
				{false, false, true},
				{false, false, false},
			},
			capacities: []int{1, 1, 1},
			entry:      1,
			target:     1,
			latencyMatrix: [][]int{
				{0, 1, 0},
				{0, 0, 1},
				{0, 0, 0},
			},
			expectEmpty:  false,
			expectedPath: []int{1},
		},
		{
			name: "no valid path due to connection",
			N:    3,
			connections: [][]bool{
				{false, false, false},
				{false, false, true},
				{false, false, false},
			},
			capacities: []int{1, 1, 1},
			entry:      0,
			target:     2,
			latencyMatrix: [][]int{
				{0, 0, 0},
				{0, 0, 1},
				{0, 0, 0},
			},
			expectEmpty: true,
		},
		{
			name: "no valid path due to capacity exhaustion",
			N:    4,
			connections: [][]bool{
				{false, true, false, false},
				{false, false, true, false},
				{false, false, false, true},
				{false, false, false, false},
			},
			// Set capacity of node 2 to 0 to force failure.
			capacities: []int{1, 1, 0, 1},
			entry:      0,
			target:     3,
			latencyMatrix: [][]int{
				{0, 2, 0, 0},
				{0, 0, 2, 0},
				{0, 0, 0, 2},
				{0, 0, 0, 0},
			},
			expectEmpty: true,
		},
		{
			name: "multiple paths choose minimal latency",
			N:    5,
			connections: [][]bool{
				// 0 -> 1, 0 -> 2, 1 -> 3, 2 -> 3, 3 -> 4, 0 -> 4
				{false, true, true, false, true},
				{false, false, false, true, false},
				{false, false, false, true, false},
				{false, false, false, false, true},
				{false, false, false, false, false},
			},
			capacities: []int{1, 1, 1, 1, 1},
			entry:      0,
			target:     4,
			latencyMatrix: [][]int{
				{0, 5, 2, 0, 10},
				{0, 0, 0, 1, 0},
				{0, 0, 0, 1, 0},
				{0, 0, 0, 0, 1},
				{0, 0, 0, 0, 0},
			},
			// There are three potential paths:
			// path1: 0->4 with latency 10.
			// path2: 0->1->3->4 with latency 5+1+1 = 7.
			// path3: 0->2->3->4 with latency 2+1+1 = 4.
			// The optimal expected path should then be [0,2,3,4].
			expectEmpty:  false,
			expectedPath: []int{0, 2, 3, 4},
		},
		{
			name: "cycle in graph with valid capacity",
			N:    4,
			connections: [][]bool{
				// Create a cycle: 0->1, 1->2, 2->0, and 2->3
				{false, true, false, false},
				{false, false, true, false},
				{true, false, false, true},
				{false, false, false, false},
			},
			capacities: []int{1, 1, 1, 1},
			entry:      0,
			target:     3,
			latencyMatrix: [][]int{
				{0, 1, 0, 0},
				{0, 0, 1, 0},
				{1, 0, 0, 2},
				{0, 0, 0, 0},
			},
			// The optimal route is [0,1,2,3] with latency 1+1+2 = 4.
			expectEmpty:  false,
			expectedPath: []int{0, 1, 2, 3},
		},
	}

	for _, tc := range tests {
		// Copy capacities to avoid mutation affecting later tests.
		copies := make([]int, len(tc.capacities))
		copy(copies, tc.capacities)
		result := RouteRequest(tc.N, tc.connections, copies, tc.entry, tc.target, tc.latencyMatrix)
		if tc.expectEmpty {
			if len(result) != 0 {
				t.Errorf("Test %q: expected empty path, got %v", tc.name, result)
			}
		} else {
			if len(result) == 0 {
				t.Errorf("Test %q: expected a valid path, got empty slice", tc.name)
			} else {
				// Validate the path: must start with entry and end with target.
				if result[0] != tc.entry || result[len(result)-1] != tc.target {
					t.Errorf("Test %q: path must start with %d and end with %d, got %v", tc.name, tc.entry, tc.target, result)
				}
				// Validate connections exist between consecutive nodes.
				totalLatency := 0
				for i := 0; i < len(result)-1; i++ {
					u, v := result[i], result[i+1]
					if !tc.connections[u][v] {
						t.Errorf("Test %q: invalid connection from %d to %d in path %v", tc.name, u, v, result)
					}
					totalLatency += tc.latencyMatrix[u][v]
				}
				// Verify if the returned path is optimal by comparing to expectedPath if provided.
				if tc.expectedPath != nil && len(tc.expectedPath) > 0 {
					expectedLatency := 0
					for i := 0; i < len(tc.expectedPath)-1; i++ {
						expectedLatency += tc.latencyMatrix[tc.expectedPath[i]][tc.expectedPath[i+1]]
					}
					if totalLatency != expectedLatency {
						t.Errorf("Test %q: total latency mismatch, got %d, expected %d", tc.name, totalLatency, expectedLatency)
					}
					// Alternatively, directly compare the paths if they are identical.
					// Note: Multiple optimal paths might exist.
					if !reflect.DeepEqual(result, tc.expectedPath) && totalLatency == expectedLatency {
						// If paths differ but latency is same, that's acceptable.
					}
				}
			}
		}
	}
}