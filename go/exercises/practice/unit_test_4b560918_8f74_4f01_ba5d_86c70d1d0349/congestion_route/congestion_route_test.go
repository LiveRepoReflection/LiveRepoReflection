package congestion_route

import (
	"reflect"
	"testing"
)

func TestFindOptimalRoute(t *testing.T) {
	tests := []struct {
		name       string
		n          int
		edges      [][]int
		congestion []int
		M          int
		S          int
		D          int
		K          int
		expected   []int
	}{
		{
			name: "Source equals destination",
			n:    3,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 10},
			},
			congestion: []int{0, 5, 10},
			M:          10,
			S:          1,
			D:          1,
			K:          2,
			expected:   []int{1},
		},
		{
			name: "Simple route found",
			n:    3,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 10},
				{0, 2, 25},
			},
			congestion: []int{0, 5, 5},
			M:          10,
			S:          0,
			D:          2,
			K:          2,
			// Calculation:
			// Route 0 -> 1 -> 2: Edge 0-1: 10*(1+5/10) = 15, Edge 1-2: 10*(1+5/10) = 15, total = 30.
			// Route 0 -> 2: 25*(1+5/10) = 37.5.
			// Expected optimal route: [0, 1, 2]
			expected: []int{0, 1, 2},
		},
		{
			name: "Route with multiple valid approaches, choose optimal",
			n:    4,
			edges: [][]int{
				{0, 1, 5},
				{1, 3, 20},
				{0, 2, 10},
				{2, 3, 10},
				{0, 3, 50},
			},
			// Congestion values: Node0=0, Node1=10, Node2=0, Node3=5.
			congestion: []int{0, 10, 0, 5},
			M:          10,
			S:          0,
			D:          3,
			K:          2,
			// Calculation:
			// Route 0 -> 1 -> 3: Edge 0-1: 5*(1+10/10)=10, Edge 1-3: 20*(1+5/10)=30, total = 40.
			// Route 0 -> 2 -> 3: Edge 0-2: 10*(1+0/10)=10, Edge 2-3: 10*(1+5/10)=15, total = 25.
			// Direct 0 -> 3: 50*(1+5/10)=75.
			// Expected optimal route: [0, 2, 3]
			expected: []int{0, 2, 3},
		},
		{
			name: "No route within maximum hops",
			n:    4,
			edges: [][]int{
				{0, 1, 5},
				{1, 2, 5},
				{2, 3, 5},
			},
			congestion: []int{0, 0, 0, 0},
			M:          10,
			S:          0,
			D:          3,
			K:          2, // Requires 3 hops but maximum allowed is 2.
			expected:   []int{},
		},
		{
			name: "Multiple edges between nodes",
			n:    3,
			edges: [][]int{
				{0, 1, 10},
				{0, 1, 5},
				{1, 2, 10},
			},
			congestion: []int{0, 2, 4},
			M:          10,
			S:          0,
			D:          2,
			K:          2,
			// Calculation:
			// Best edge 0 -> 1: 5*(1+2/10)=6, then 1 -> 2: 10*(1+4/10)=14, total = 20.
			// Expected optimal route: [0, 1, 2]
			expected: []int{0, 1, 2},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := FindOptimalRoute(tt.n, tt.edges, tt.congestion, tt.M, tt.S, tt.D, tt.K)
			if !reflect.DeepEqual(result, tt.expected) {
				t.Errorf("Test %q failed. Expected route %v, got %v", tt.name, tt.expected, result)
			}
		})
	}
}