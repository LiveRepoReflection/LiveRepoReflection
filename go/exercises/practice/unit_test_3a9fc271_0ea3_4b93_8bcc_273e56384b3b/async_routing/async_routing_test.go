package async_routing

import (
	"reflect"
	"testing"
	"time"
)

// isValidPath checks if the given path is valid in the provided adjacency list.
func isValidPath(adjacency [][]int, path []int) bool {
	for i := 0; i < len(path)-1; i++ {
		valid := false
		for _, neighbor := range adjacency[path[i]] {
			if neighbor == path[i+1] {
				valid = true
				break
			}
		}
		if !valid {
			return false
		}
	}
	return true
}

// TestFindPath validates the correctness and performance of the FindPath function.
// It tests for correct answers in various scenarios and ensures the function responds
// within the required time limit.
func TestFindPath(t *testing.T) {
	testCases := []struct {
		name         string
		n            int
		adjacency    [][]int
		source       int
		destination  int
		expectedPath []int // if empty, means no path exists; if non-empty, length must match shortest route length.
	}{
		{
			name:         "Single node",
			n:            1,
			adjacency:    [][]int{{}},
			source:       0,
			destination:  0,
			expectedPath: []int{0},
		},
		{
			name:         "Direct connection",
			n:            2,
			adjacency:    [][]int{{1}, {}},
			source:       0,
			destination:  1,
			expectedPath: []int{0, 1},
		},
		{
			name:         "No path available",
			n:            2,
			adjacency:    [][]int{{}, {}},
			source:       0,
			destination:  1,
			expectedPath: []int{},
		},
		{
			name:        "Cycle in graph",
			n:           3,
			adjacency:   [][]int{{1}, {2}, {0}},
			source:      0,
			destination: 2,
			// Only valid shortest path has length 3: 0 -> 1 -> 2.
			expectedPath: []int{0, 1, 2},
		},
		{
			name: "Multiple paths choose shortest",
			n:    4,
			adjacency: [][]int{
				{1, 2},
				{3},
				{3},
				{},
			},
			source:       0,
			destination:  3,
			// Both [0,1,3] and [0,2,3] are acceptable as valid shortest paths of length 3.
			expectedPath: []int{0, 1, 3},
		},
		{
			name: "Disconnected subgraph",
			n:    5,
			adjacency: [][]int{
				{1},
				{2},
				{},
				{4},
				{},
			},
			source:       0,
			destination:  4,
			expectedPath: []int{},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Enforce a maximum runtime per test case.
			startTime := time.Now()
			result := FindPath(tc.n, tc.adjacency, tc.source, tc.destination)
			duration := time.Since(startTime)
			if duration > 10*time.Second {
				t.Errorf("Test %q exceeded time limit: %v", tc.name, duration)
			}

			// When no path is expected.
			if len(tc.expectedPath) == 0 {
				if len(result) != 0 {
					t.Errorf("Test %q: expected no path, but got %v", tc.name, result)
				}
				return
			}

			// For non-empty paths, check initial and final nodes.
			if len(result) == 0 {
				t.Errorf("Test %q: expected path %v, but got empty slice", tc.name, tc.expectedPath)
				return
			}
			if result[0] != tc.source {
				t.Errorf("Test %q: path should start with source %d, but got %d", tc.name, tc.source, result[0])
			}
			if result[len(result)-1] != tc.destination {
				t.Errorf("Test %q: path should end with destination %d, but got %d", tc.name, tc.destination, result[len(result)-1])
			}

			// Validate that the path is valid based on the provided adjacency list.
			if !isValidPath(tc.adjacency, result) {
				t.Errorf("Test %q: invalid path %v for the given graph", tc.name, result)
			}

			// Check that the path length is minimal.
			if len(result) != len(tc.expectedPath) {
				t.Errorf("Test %q: expected shortest path length %d, but got path %v of length %d",
					tc.name, len(tc.expectedPath), result, len(result))
			}

			// Optionally, if the expected path is explicitly defined, check for exact match.
			// This may be helpful for cases with only one valid solution.
			if !reflect.DeepEqual(result, tc.expectedPath) && tc.name != "Multiple paths choose shortest" {
				t.Errorf("Test %q: expected path %v, but got %v", tc.name, tc.expectedPath, result)
			}
		})
	}
}