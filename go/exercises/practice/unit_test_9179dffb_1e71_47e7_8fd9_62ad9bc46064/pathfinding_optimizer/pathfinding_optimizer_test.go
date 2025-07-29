package pathfinding

import (
	"reflect"
	"testing"
)

func TestPathfindingOptimizer(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		edges    [][3]int
		updates  [][3]int
		requests [][4]int
		want     []int
	}{
		{
			name:  "Simple path with no updates",
			n:     3,
			edges: [][3]int{{0, 1, 5}, {1, 2, 5}},
			updates: [][3]int{},
			requests: [][4]int{
				{0, 2, 15, 100}, // Should find path with cost 10
			},
			want: []int{10},
		},
		{
			name:  "Path with deadline miss",
			n:     3,
			edges: [][3]int{{0, 1, 10}, {1, 2, 10}},
			updates: [][3]int{},
			requests: [][4]int{
				{0, 2, 15, 5}, // Cost would be 20, exceeding deadline, return penalty
			},
			want: []int{5},
		},
		{
			name:  "Multiple paths with updates",
			n:     4,
			edges: [][3]int{{0, 1, 10}, {1, 2, 10}, {0, 3, 5}, {3, 2, 5}},
			updates: [][3]int{
				{1, 2, 20}, // Make the upper path more expensive
			},
			requests: [][4]int{
				{0, 2, 30, 100}, // Should take the lower path (0->3->2) with cost 10
			},
			want: []int{10},
		},
		{
			name:  "Complex scenario with multiple requests",
			n:     5,
			edges: [][3]int{{0, 1, 5}, {1, 2, 5}, {2, 3, 5}, {3, 4, 5}, {0, 4, 25}},
			updates: [][3]int{
				{0, 4, 15}, // Make direct path cheaper
			},
			requests: [][4]int{
				{0, 4, 20, 100},  // Should take direct path with cost 15
				{0, 3, 10, 50},   // Should miss deadline and return penalty
				{1, 4, 30, 100},  // Should take path through nodes with cost 15
			},
			want: []int{15, 50, 15},
		},
		{
			name:  "Disconnected graph",
			n:     4,
			edges: [][3]int{{0, 1, 5}, {2, 3, 5}},
			updates: [][3]int{},
			requests: [][4]int{
				{0, 3, 100, 20}, // No path exists, should return penalty
			},
			want: []int{20},
		},
		{
			name:  "Dynamic edge additions",
			n:     3,
			edges: [][3]int{{0, 1, 10}},
			updates: [][3]int{
				{1, 2, 5}, // Add new edge
			},
			requests: [][4]int{
				{0, 2, 20, 100}, // Should use newly added edge
			},
			want: []int{15},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			optimizer := Initialize(tt.n, tt.edges)
			
			// Apply updates
			for _, update := range tt.updates {
				optimizer.UpdateEdgeCost(update[0], update[1], update[2])
			}

			// Process requests
			got := optimizer.ProcessDeliveryRequests(tt.requests)

			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ProcessDeliveryRequests() = %v, want %v", got, tt.want)
			}
		})
	}
}

// Benchmarks
func BenchmarkInitialize(b *testing.B) {
	edges := [][3]int{{0, 1, 5}, {1, 2, 5}, {2, 3, 5}, {3, 4, 5}}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Initialize(5, edges)
	}
}

func BenchmarkUpdateEdgeCost(b *testing.B) {
	optimizer := Initialize(5, [][3]int{{0, 1, 5}, {1, 2, 5}, {2, 3, 5}, {3, 4, 5}})
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		optimizer.UpdateEdgeCost(0, 1, 10)
	}
}

func BenchmarkProcessDeliveryRequests(b *testing.B) {
	optimizer := Initialize(5, [][3]int{{0, 1, 5}, {1, 2, 5}, {2, 3, 5}, {3, 4, 5}})
	requests := [][4]int{{0, 4, 20, 100}, {1, 3, 15, 50}}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		optimizer.ProcessDeliveryRequests(requests)
	}
}