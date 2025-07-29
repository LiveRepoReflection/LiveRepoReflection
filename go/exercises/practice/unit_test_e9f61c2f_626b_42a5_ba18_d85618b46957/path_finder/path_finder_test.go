package path_finder

import (
	"reflect"
	"testing"
)

func TestFindBestRoutes(t *testing.T) {
	testCases := []struct {
		description string
		N           int
		pathways    [][4]int
		requests    [][4]int
		expected    []int
	}{
		{
			description: "Basic graph example",
			N:           4,
			pathways: [][4]int{
				{0, 1, 5, 10},
				{0, 2, 3, 5},
				{1, 2, 2, 3},
				{2, 3, 1, 1},
				{1, 3, 4, 8},
			},
			requests: [][4]int{
				{0, 3, 10, 15}, // Expected best route: 0->2->3 => time = 3+1 = 4, cost = 5+1 = 6.
				{0, 3, 6, 6},   // Expected best route: 0->2->3 => time = 4, cost = 6.
				{1, 0, 7, 12},  // Expected best route: either 1->0 => time = 5, cost = 10 or 1->2->0 with same time.
			},
			expected: []int{4, 4, 5},
		},
		{
			description: "Self route returns 0",
			N:           1,
			pathways:    [][4]int{},
			requests: [][4]int{
				{0, 0, 5, 5},
			},
			expected: []int{0},
		},
		{
			description: "Unreachable destination",
			N:           3,
			pathways: [][4]int{
				{0, 1, 2, 3},
			},
			requests: [][4]int{
				{0, 2, 10, 10},
			},
			expected: []int{-1},
		},
		{
			description: "Multiple pathways between two nodes",
			N:           3,
			pathways: [][4]int{
				{0, 1, 2, 3},
				{0, 1, 1, 5},
				{1, 2, 2, 2},
			},
			requests: [][4]int{
				{0, 2, 10, 8}, // Option one: (0,1,1,5)+(1,2,2,2) => time 3, cost 7.
				{0, 2, 3, 7},  // Same as above.
				{0, 2, 3, 6},  // No valid route as all exceed cost constraint.
			},
			expected: []int{3, 3, -1},
		},
		{
			description: "Graph with cycles and multiple valid paths",
			N:           5,
			pathways: [][4]int{
				{0, 1, 2, 2},
				{1, 2, 2, 2},
				{2, 3, 2, 2},
				{3, 4, 2, 2},
				{0, 4, 10, 1},
				{1, 3, 1, 10},
				{2, 4, 1, 10},
			},
			requests: [][4]int{
				{0, 4, 10, 10}, // Option one: 0->1->2->3->4 => time 8, cost 8; Option two: 0->4 directly => time 10, cost 1.
				{0, 4, 7, 10},  // Neither route fits time constraint. Expected -1.
			},
			expected: []int{8, -1},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := findBestRoutes(tc.N, tc.pathways, tc.requests)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Fatalf("Test %q failed. Expected %v, got %v", tc.description, tc.expected, result)
			}
		})
	}
}