package network_path

import (
	"testing"
)

// TestCase defines a test case for ProcessRequest.
type TestCase struct {
	description      string
	graph            [][]int
	request          []int
	congestionFactor float64
	expected         int
}

func TestProcessRequest(t *testing.T) {
	testCases := []TestCase{
		{
			description:      "Source equals destination should return 0",
			graph:            [][]int{{}, {}},
			request:          []int{0, 0, 10},
			congestionFactor: 1.0,
			expected:         0,
		},
		{
			description: "Simple two-node connected path within deadline",
			graph: [][]int{
				{1, 10},
				{0, 10},
			},
			request:          []int{0, 1, 15},
			congestionFactor: 1.0,
			expected:         10,
		},
		{
			description: "Simple two-node connected path exceeding deadline",
			graph: [][]int{
				{1, 10},
				{0, 10},
			},
			request:          []int{0, 1, 5},
			congestionFactor: 1.0,
			expected:         -1,
		},
		{
			description: "Multiple paths with congestion factor 1.0, direct path optimal",
			graph: [][]int{
				{1, 10, 2, 30},
				{0, 10, 2, 20},
				{0, 30, 1, 20},
			},
			request:          []int{0, 2, 50},
			congestionFactor: 1.0,
			expected:         30,
		},
		{
			description: "Path becomes infeasible when deadline is too tight under low congestion factor",
			graph: [][]int{
				{1, 10, 2, 30},
				{0, 10, 2, 20},
				{0, 30, 1, 20},
			},
			// With congestionFactor 0.5, both paths cost 15.
			request:          []int{0, 2, 14},
			congestionFactor: 0.5,
			expected:         -1,
		},
		{
			description: "Path remains feasible under high congestion factor",
			graph: [][]int{
				{1, 10, 2, 30},
				{0, 10, 2, 20},
				{0, 30, 1, 20},
			},
			// With congestionFactor 1.5, direct path cost is 45.
			request:          []int{0, 2, 60},
			congestionFactor: 1.5,
			expected:         45,
		},
		{
			description: "Disconnected graph should return -1",
			graph: [][]int{
				{1, 5},
				{0, 5},
				// Node 2 is disconnected.
				{},
			},
			request:          []int{0, 2, 100},
			congestionFactor: 1.0,
			expected:         -1,
		},
	}

	for _, tc := range testCases {
		// Set the global congestionFactor as provided in the test case.
		congestionFactor = tc.congestionFactor

		result := ProcessRequest(tc.graph, tc.request)
		if result != tc.expected {
			t.Errorf("FAILED: %s\nGraph: %v\nRequest: %v with congestionFactor: %v\nExpected %d but got %d",
				tc.description, tc.graph, tc.request, tc.congestionFactor, tc.expected, result)
		}
	}
}

func BenchmarkProcessRequest(b *testing.B) {
	// A moderate size graph for benchmarking.
	graph := [][]int{
		{1, 10, 2, 20, 3, 30},
		{0, 10, 2, 25, 3, 35},
		{0, 20, 1, 25, 3, 15},
		{0, 30, 1, 35, 2, 15},
	}

	// Benchmark request: from node 0 to node 3 with a generous deadline.
	request := []int{0, 3, 100}
	congestionFactor = 1.0

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ProcessRequest(graph, request)
	}
}