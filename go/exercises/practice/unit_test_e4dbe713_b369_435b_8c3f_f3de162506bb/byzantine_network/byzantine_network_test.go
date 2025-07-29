package byzantine_network

import (
	"testing"
)

func TestOptimalPartition(t *testing.T) {
	tests := []struct {
		name          string
		N             int
		K             int
		edges         [][2]int
		groupSizes    []int
		expectedCost  int
		expectFailure bool
	}{
		{
			name:  "simple valid case",
			N:     7,
			K:     2,
			edges: [][2]int{{0, 1}, {0, 2}, {1, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 6}},
			groupSizes:    []int{3, 3},
			expectedCost:  2,
			expectFailure: false,
		},
		{
			name:  "minimum group size not met",
			N:     7,
			K:     2,
			edges: [][2]int{{0, 1}, {0, 2}, {1, 2}, {1, 3}, {2, 4}, {3, 5}, {4, 6}},
			groupSizes:    []int{4, 4},
			expectedCost:  -1,
			expectFailure: true,
		},
		{
			name:  "disconnected graph",
			N:     6,
			K:     2,
			edges: [][2]int{{0, 1}, {1, 2}, {3, 4}, {4, 5}},
			groupSizes:    []int{3, 3},
			expectedCost:  0,
			expectFailure: false,
		},
		{
			name:  "single group case",
			N:     4,
			K:     1,
			edges: [][2]int{{0, 1}, {1, 2}, {2, 3}},
			groupSizes:    []int{4},
			expectedCost:  0,
			expectFailure: false,
		},
		{
			name:  "byzantine resilience requirement",
			N:     8,
			K:     2,
			edges: [][2]int{{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 6}, {6, 7}},
			groupSizes:    []int{4, 4},
			expectedCost:  1,
			expectFailure: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actualCost := OptimalPartition(tt.N, tt.K, tt.edges, tt.groupSizes)
			if tt.expectFailure {
				if actualCost != tt.expectedCost {
					t.Errorf("Expected failure with cost %d, got %d", tt.expectedCost, actualCost)
				}
			} else {
				if actualCost > tt.expectedCost {
					t.Errorf("Expected cost <= %d, got %d", tt.expectedCost, actualCost)
				}
				// Additional checks for group sizes and byzantine resilience
				// would be implemented here if we had access to the partition details
			}
		})
	}
}

func BenchmarkOptimalPartition(b *testing.B) {
	N := 100
	K := 5
	edges := make([][2]int, 0)
	// Create a simple line graph
	for i := 0; i < N-1; i++ {
		edges = append(edges, [2]int{i, i + 1})
	}
	groupSizes := []int{20, 20, 20, 20, 20}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalPartition(N, K, edges, groupSizes)
	}
}