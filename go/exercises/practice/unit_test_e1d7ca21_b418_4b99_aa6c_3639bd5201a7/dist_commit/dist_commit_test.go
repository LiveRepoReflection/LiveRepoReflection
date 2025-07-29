package dist_commit

import (
	"testing"
)

type testCase struct {
	name             string
	n                int
	dependencies     [][2]int
	states           []string
	latency          [][]int
	expectedDecision string
	expectedLatency  int
}

func TestProcessTransaction(t *testing.T) {
	tests := []testCase{
		{
			name:         "Example Case",
			n:            4,
			dependencies: [][2]int{{0, 1}, {0, 2}, {1, 3}},
			states:       []string{"READY", "READY", "READY", "READY"},
			latency: [][]int{
				{-1, 0, 5, 2},
				{0, -1, 1, -1},
				{5, 1, -1, 1},
				{2, -1, 1, -1},
			},
			expectedDecision: "COMMIT",
			expectedLatency:  9,
		},
		{
			name:         "Failed Shard",
			n:            3,
			dependencies: [][2]int{{0, 1}, {1, 2}},
			states:       []string{"READY", "FAILED", "READY"},
			latency: [][]int{
				{-1, 3, 4},
				{3, -1, 2},
				{4, 2, -1},
			},
			expectedDecision: "ABORT",
			expectedLatency:  0,
		},
		{
			name:         "No Dependencies",
			n:            3,
			dependencies: [][2]int{},
			states:       []string{"READY", "READY", "READY"},
			latency: [][]int{
				{-1, 2, 3},
				{2, -1, 4},
				{3, 4, -1},
			},
			// Explanation:
			// Prepare phase: maximum latency from coordinator (shard 0) to others = max(2,3) = 3.
			// Commit phase: shards with no dependencies can be committed concurrently,
			// commit latency = max(2,3) = 3.
			// Total latency = 3 + 3 = 6.
			expectedDecision: "COMMIT",
			expectedLatency:  6,
		},
		{
			name:         "Diamond Dependency",
			n:            4,
			dependencies: [][2]int{{0, 1}, {0, 2}, {1, 3}, {2, 3}},
			states:       []string{"READY", "READY", "READY", "READY"},
			latency: [][]int{
				{-1, 1, 4, 7},
				{1, -1, 2, 3},
				{4, 2, -1, 1},
				{7, 3, 1, -1},
			},
			// Explanation:
			// Prepare phase: maximum latency from coordinator (shard 0) = max(1, 4, 7) = 7.
			// Commit phase:
			// Level 1 (shards 1 and 2, which depend on shard 0): commit latency = max(1, 4) = 4.
			// Level 2 (shard 3, depends on shards 1 and 2): commit latency = 7.
			// Total latency = 7 + 4 + 7 = 18.
			expectedDecision: "COMMIT",
			expectedLatency:  18,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			// Convert dependencies from slice of [2]int to slice of []int.
			var deps [][]int
			for _, edge := range tc.dependencies {
				deps = append(deps, []int{edge[0], edge[1]})
			}
			decision, totalLatency := ProcessTransaction(tc.n, deps, tc.states, tc.latency)
			if decision != tc.expectedDecision || totalLatency != tc.expectedLatency {
				t.Errorf("Test %q failed. Got (%s, %d), expected (%s, %d)", tc.name, decision, totalLatency, tc.expectedDecision, tc.expectedLatency)
			}
		})
	}
}