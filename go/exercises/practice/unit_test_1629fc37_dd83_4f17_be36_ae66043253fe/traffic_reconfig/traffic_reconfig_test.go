package traffic_reconfig

import (
	"testing"
)

func TestMaxTrafficFlow(t *testing.T) {
	tests := []struct {
		name            string
		n               int
		edges           [][3]int
		reducedEdges    [][3]int
		source          int
		destination     int
		expectedFlow    int
		expectError     bool
	}{
		{
			name: "simple network with no reductions",
			n: 4,
			edges: [][3]int{
				{0, 1, 10},
				{1, 2, 5},
				{2, 3, 10},
			},
			reducedEdges: [][3]int{},
			source: 0,
			destination: 3,
			expectedFlow: 5,
		},
		{
			name: "network with capacity reductions",
			n: 4,
			edges: [][3]int{
				{0, 1, 10},
				{1, 2, 5},
				{2, 3, 10},
				{0, 2, 3},
			},
			reducedEdges: [][3]int{
				{1, 2, 2},
			},
			source: 0,
			destination: 3,
			expectedFlow: 5,
		},
		{
			name: "disconnected network",
			n: 4,
			edges: [][3]int{
				{0, 1, 10},
				{2, 3, 5},
			},
			reducedEdges: [][3]int{},
			source: 0,
			destination: 3,
			expectedFlow: 0,
		},
		{
			name: "multiple paths with reductions",
			n: 5,
			edges: [][3]int{
				{0, 1, 10},
				{0, 2, 5},
				{1, 3, 8},
				{2, 3, 3},
				{3, 4, 10},
			},
			reducedEdges: [][3]int{
				{0, 1, 5},
				{1, 3, 4},
			},
			source: 0,
			destination: 4,
			expectedFlow: 7,
		},
		{
			name: "invalid source node",
			n: 3,
			edges: [][3]int{
				{0, 1, 10},
				{1, 2, 5},
			},
			reducedEdges: [][3]int{},
			source: 5,
			destination: 2,
			expectError: true,
		},
		{
			name: "complete bottleneck",
			n: 3,
			edges: [][3]int{
				{0, 1, 10},
				{1, 2, 10},
			},
			reducedEdges: [][3]int{
				{1, 2, 0},
			},
			source: 0,
			destination: 2,
			expectedFlow: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			flow, err := MaxTrafficFlow(tt.n, tt.edges, tt.reducedEdges, tt.source, tt.destination)
			if tt.expectError {
				if err == nil {
					t.Errorf("Expected error but got none")
				}
				return
			}
			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}
			if flow != tt.expectedFlow {
				t.Errorf("Expected flow %d, got %d", tt.expectedFlow, flow)
			}
		})
	}
}

func BenchmarkMaxTrafficFlow(b *testing.B) {
	n := 100
	edges := make([][3]int, 0)
	for i := 0; i < n-1; i++ {
		edges = append(edges, [3]int{i, i + 1, 100})
	}
	reducedEdges := [][3]int{
		{0, 1, 50},
		{n/2, n/2+1, 30},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MaxTrafficFlow(n, edges, reducedEdges, 0, n-1)
	}
}