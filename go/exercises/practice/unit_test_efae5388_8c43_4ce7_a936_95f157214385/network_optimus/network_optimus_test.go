package networkoptimus

import (
	"testing"
)

func TestOptimizeNetwork(t *testing.T) {
	tests := []struct {
		name        string
		n           int
		connections [][]int
		maxLatency  int
		expected    int
	}{
		{
			name:        "single node",
			n:           1,
			connections: [][]int{},
			maxLatency:  10,
			expected:    0,
		},
		{
			name:        "two nodes valid",
			n:           2,
			connections: [][]int{{0, 1, 5}},
			maxLatency:  6,
			expected:    5,
		},
		{
			name:        "two nodes multiple connections",
			n:           2,
			connections: [][]int{{0, 1, 10}, {0, 1, 4}},
			maxLatency:  5,
			expected:    4,
		},
		{
			name:        "insufficient connections",
			n:           3,
			connections: [][]int{{0, 1, 3}},
			maxLatency:  10,
			expected:    -1,
		},
		{
			name:        "three nodes valid spanning tree",
			n:           3,
			connections: [][]int{{0, 1, 3}, {1, 2, 3}, {0, 2, 7}},
			maxLatency:  6,
			expected:    6,
		},
		{
			name:        "three nodes invalid latency",
			n:           3,
			connections: [][]int{{0, 1, 3}, {1, 2, 3}, {0, 2, 7}},
			maxLatency:  5,
			expected:    -1,
		},
		{
			name: "four nodes valid configuration",
			n:    4,
			connections: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{2, 3, 1},
				{0, 3, 4},
				{0, 2, 2},
			},
			maxLatency: 3,
			expected:   3,
		},
		{
			name: "four nodes invalid latency",
			n:    4,
			connections: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{2, 3, 1},
				{0, 3, 4},
				{0, 2, 2},
			},
			maxLatency: 2,
			expected:   -1,
		},
		{
			name: "self loop test",
			n:    3,
			connections: [][]int{
				{0, 0, 10},
				{0, 1, 2},
				{1, 2, 2},
				{0, 2, 5},
			},
			maxLatency: 4,
			expected:   4,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := OptimizeNetwork(tt.n, tt.connections, tt.maxLatency)
			if result != tt.expected {
				t.Errorf("OptimizeNetwork(%d, %v, %d) = %d; expected %d", tt.n, tt.connections, tt.maxLatency, result, tt.expected)
			}
		})
	}
}

func BenchmarkOptimizeNetwork(b *testing.B) {
	n := 10
	var connections [][]int
	// Construct a complete graph
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			latency := ((i + j + 1) % 10) + 1
			connections = append(connections, []int{i, j, latency})
		}
	}
	maxLatency := 15
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimizeNetwork(n, connections, maxLatency)
	}
}