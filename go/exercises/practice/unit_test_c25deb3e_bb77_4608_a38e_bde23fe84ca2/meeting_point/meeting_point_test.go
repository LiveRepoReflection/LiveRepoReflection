package meeting_point

import (
	"testing"
)

func TestMeetingPoint(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		edges    [][]int
		friends  []int
		expected int
	}{
		{
			name:     "Single friend",
			n:        3,
			edges:    [][]int{{0, 1, 5}, {1, 2, 10}},
			friends:  []int{1},
			expected: 1,
		},
		{
			name: "Linear graph endpoints",
			n:    4,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{2, 3, 1},
			},
			friends:  []int{0, 3},
			// Possible optimal meeting points are nodes 1 and 2 (with max distance 2);
			// expected output is the smallest index, which is 1.
			expected: 1,
		},
		{
			name: "Triangle graph",
			n:    3,
			edges: [][]int{
				{0, 1, 5},
				{0, 2, 2},
				{1, 2, 2},
			},
			friends:  []int{0, 1},
			// For meeting at node 0: distances are [0, 5]; at 1: [5, 0]; at 2: [2, 2] => optimal is node 2.
			expected: 2,
		},
		{
			name: "Star graph",
			n:    4,
			edges: [][]int{
				{0, 1, 3},
				{0, 2, 3},
				{0, 3, 3},
			},
			friends:  []int{1, 2, 3},
			// Meeting at center (node 0) yields max distance 3.
			expected: 0,
		},
		{
			name: "Complex graph",
			n:    5,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2},
				{2, 3, 3},
				{3, 4, 4},
				{0, 4, 10},
				{1, 3, 2},
				{2, 4, 2},
			},
			friends:  []int{0, 4},
			// Evaluating distances:
			// Meeting at node 0: max distance = 5 (friend at 4: via 4->2->1->0: 2+2+1=5)
			// Meeting at node 1: max distance = 4, node 2: max distance = 3, node 3: max distance = 4, node 4: max distance = 5.
			// The optimal meeting point is node 2.
			expected: 2,
		},
		{
			name: "Tie meeting point",
			n:    5,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
				{1, 3, 1},
				{2, 4, 1},
				{3, 4, 1},
			},
			friends:  []int{0, 4},
			// Possible meeting points:
			// Node 0: [0, distance 0-1-2-4 = 1+1+1=3] = 3,
			// Node 1: [1, 4-2-1 = 1+1 = 2] = 2,
			// Node 2: [0-1-2 = 1+1 = 2, 4-2 = 1] = 2,
			// Node 3: [0-1-3 = 1+1 = 2, 4-3 = 1] = 2,
			// Node 4: [0-1-2-4 = 1+1+1 = 3, 0] = 3.
			// The minimal maximum distance is 2 and among nodes 1, 2, 3 choose the smallest index -> 1.
			expected: 1,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := MeetingPoint(tc.n, tc.edges, tc.friends)
			if result != tc.expected {
				t.Errorf("Test %q failed: expected %d, got %d", tc.name, tc.expected, result)
			}
		})
	}
}