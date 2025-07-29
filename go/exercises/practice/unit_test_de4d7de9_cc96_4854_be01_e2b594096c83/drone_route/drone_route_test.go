package drone_route

import "testing"

type testCase struct {
	description string
	n           int
	edges       [][]int // each edge is represented as [u, v, w]
	S           int
	D           int
	B           int
	R           int
	expected    int
}

func TestMinRouteTime(t *testing.T) {
	testCases := []testCase{
		{
			description: "Sample input provided in description",
			n:           4,
			edges: [][]int{
				{0, 1, 10},
				{0, 2, 15},
				{1, 3, 20},
				{2, 3, 5},
				{0, 3, 40},
			},
			S:        0,
			D:        3,
			B:        30,
			R:        10,
			expected: 20,
		},
		{
			description: "No possible route due to battery capacity",
			n:           3,
			edges: [][]int{
				{0, 1, 50},
				{1, 2, 10},
			},
			S:        0,
			D:        2,
			B:        40,
			R:        10,
			expected: -1,
		},
		{
			description: "Trivial case: start equals destination",
			n:           1,
			edges:       [][]int{},
			S:           0,
			D:           0,
			B:           30,
			R:           10,
			expected:    0,
		},
		{
			description: "Multiple recharges required",
			n:           5,
			edges: [][]int{
				{0, 1, 15},
				{1, 2, 15},
				{2, 3, 15},
				{3, 4, 15},
			},
			S:        0,
			D:        4,
			B:        20,
			R:        5,
			expected: 75,
		},
		{
			description: "Optimal route selection with crossover",
			n:           5,
			edges: [][]int{
				{0, 1, 10},
				{1, 4, 10},
				{0, 2, 15},
				{2, 3, 15},
				{3, 4, 5},
				{1, 2, 5},
			},
			S:        0,
			D:        4,
			B:        20,
			R:        10,
			expected: 20,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := MinRouteTime(tc.n, tc.edges, tc.S, tc.D, tc.B, tc.R)
			if result != tc.expected {
				t.Errorf("Test %q failed; expected %d but got %d", tc.description, tc.expected, result)
			}
		})
	}
}