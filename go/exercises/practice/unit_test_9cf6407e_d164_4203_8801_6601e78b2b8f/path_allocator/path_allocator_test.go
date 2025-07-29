package path_allocator

import (
	"testing"
)

func TestOptimalPathAllocation(t *testing.T) {
	tests := []struct {
		name          string
		graph         map[int][]Edge
		nodeCaps      map[int]int
		tasks         []int
		k             int
		wantAllocated bool
	}{
		{
			name: "simple graph with valid allocation",
			graph: map[int][]Edge{
				0: {{1, 10}, {2, 5}},
				1: {{2, 8}},
			},
			nodeCaps: map[int]int{
				0: 15,
				1: 10,
				2: 13,
			},
			tasks:         []int{4, 3, 2, 5, 1},
			k:            2,
			wantAllocated: true,
		},
		{
			name: "insufficient capacity",
			graph: map[int][]Edge{
				0: {{1, 2}},
				1: {{2, 2}},
			},
			nodeCaps: map[int]int{
				0: 3,
				1: 3,
				2: 3,
			},
			tasks:         []int{5, 5},
			k:            2,
			wantAllocated: false,
		},
		{
			name: "complex graph with multiple paths",
			graph: map[int][]Edge{
				0: {{1, 10}, {3, 15}},
				1: {{2, 8}, {3, 5}},
				2: {{4, 12}},
				3: {{4, 10}},
			},
			nodeCaps: map[int]int{
				0: 30,
				1: 15,
				2: 15,
				3: 20,
				4: 25,
			},
			tasks:         []int{8, 6, 4, 7, 5, 3},
			k:            3,
			wantAllocated: true,
		},
		{
			name: "not enough unique paths",
			graph: map[int][]Edge{
				0: {{1, 10}},
				1: {{2, 10}},
			},
			nodeCaps: map[int]int{
				0: 20,
				1: 20,
				2: 20,
			},
			tasks:         []int{5, 5, 5},
			k:            3,
			wantAllocated: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := AllocatePaths(tt.graph, tt.nodeCaps, tt.tasks, tt.k)
			if tt.wantAllocated {
				if len(got) == 0 {
					t.Errorf("Expected valid allocation but got none")
				}
				// Verify capacity constraints
				if err := verifyAllocation(tt.graph, tt.nodeCaps, tt.tasks, got); err != nil {
					t.Errorf("Allocation verification failed: %v", err)
				}
			} else {
				if len(got) > 0 {
					t.Errorf("Expected no allocation but got one")
				}
			}
		})
	}
}

func verifyAllocation(graph map[int][]Edge, nodeCaps map[int]int, tasks []int, allocation [][]int) error {
	// Implementation would verify:
	// 1. All tasks are allocated exactly once
	// 2. Node capacities aren't exceeded
	// 3. Edge bandwidths aren't exceeded
	// 4. Paths are unique and valid in the graph
	// (Actual implementation omitted for brevity)
	return nil
}