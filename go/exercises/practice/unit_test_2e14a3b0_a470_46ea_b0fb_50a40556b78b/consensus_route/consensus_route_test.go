package consensus_route

import (
	"reflect"
	"testing"
)

func TestFindOptimalRoute(t *testing.T) {
	tests := []struct {
		name            string
		N               int
		graph           map[int]map[int]int
		primaryNode     int
		originNode      int
		maxLatency      int
		consistentNodes []int
		expected        []int
	}{
		{
			name:        "Origin is consistent",
			N:           5,
			graph:       map[int]map[int]int{0: {1: 10}, 1: {2: 10}},
			primaryNode: 0,
			originNode:  2,
			maxLatency:  50,
			consistentNodes: []int{2},
			expected:    []int{2},
		},
		{
			name:        "Simple optimal route via intermediate node",
			N:           5,
			graph:       map[int]map[int]int{0: {1: 10, 2: 40}, 1: {2: 20}},
			primaryNode: 0,
			originNode:  0,
			maxLatency:  50,
			consistentNodes: []int{2},
			expected:    []int{0, 1, 2},
		},
		{
			name:        "No route available (disconnected)",
			N:           4,
			graph:       map[int]map[int]int{0: {1: 10}, 1: {0: 10}},
			primaryNode: 0,
			originNode:  0,
			maxLatency:  50,
			consistentNodes: []int{3},
			expected:    nil,
		},
		{
			name:        "Route exists but exceeds maxLatency",
			N:           4,
			graph:       map[int]map[int]int{0: {1: 100}, 1: {2: 100}, 2: {3: 100}},
			primaryNode: 0,
			originNode:  0,
			maxLatency:  250, // Best route latency equals 300, which is over the limit.
			consistentNodes: []int{3},
			expected:    nil,
		},
		{
			name: "Multiple consistent nodes; choose optimal",
			N:    5,
			graph: map[int]map[int]int{
				0: {1: 10, 2: 20},
				1: {3: 10},
				2: {3: 5, 4: 1},
				4: {3: 2},
			},
			primaryNode: 0,
			originNode:  0,
			maxLatency:  50,
			consistentNodes: []int{3, 4},
			// Possible routes:
			// 0->1->3 with latency 10+10 = 20,
			// 0->2->3 with latency 20+5 = 25,
			// 0->2->4 with latency 20+1 = 21.
			// Optimal route is [0, 1, 3] with total latency 20.
			expected: []int{0, 1, 3},
		},
		{
			name: "Direct route available within maxLatency",
			N:    3,
			graph: map[int]map[int]int{
				0: {1: 10, 2: 15},
				1: {2: 5},
			},
			primaryNode: 0,
			originNode:  0,
			maxLatency:  20,
			consistentNodes: []int{2},
			// Direct route: 0->2 with latency 15 is within maxLatency.
			expected: []int{0, 2},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := FindOptimalRoute(tc.N, tc.graph, tc.primaryNode, tc.originNode, tc.maxLatency, tc.consistentNodes)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("Test %q failed: expected route %v, got %v", tc.name, tc.expected, result)
			}
		})
	}
}

func BenchmarkFindOptimalRoute(b *testing.B) {
	graph := map[int]map[int]int{
		0: {1: 10, 2: 20},
		1: {2: 15, 3: 10},
		2: {3: 5, 4: 25},
		3: {4: 10},
		4: {},
	}
	N := 5
	primaryNode := 0
	originNode := 0
	maxLatency := 100
	consistentNodes := []int{3, 4}

	for i := 0; i < b.N; i++ {
		FindOptimalRoute(N, graph, primaryNode, originNode, maxLatency, consistentNodes)
	}
}