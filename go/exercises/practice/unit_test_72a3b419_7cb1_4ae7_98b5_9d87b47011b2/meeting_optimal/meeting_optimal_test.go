package meeting_optimal

import (
	"testing"
)

type testCase struct {
	description string
	n           int
	edges       [][]int // each edge represented as [u, v, w]
	locations   []int
	expected    int
}

func TestMeetingOptimal(t *testing.T) {
	testCases := []testCase{
		{
			description: "single node, one location",
			n:           1,
			edges:       [][]int{},
			locations:   []int{0},
			expected:    0,
		},
		{
			description: "triangle graph, two people's homes",
			n:           3,
			edges:       [][]int{{0, 1, 2}, {1, 2, 3}, {0, 2, 1}},
			locations:   []int{0, 1},
			expected:    0,
		},
		{
			description: "chain graph, endpoints",
			n:           5,
			edges:       [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}, {3, 4, 1}},
			locations:   []int{0, 4},
			expected:    2,
		},
		{
			description: "disconnected graph",
			n:           4,
			edges:       [][]int{{0, 1, 1}},
			locations:   []int{0, 2},
			expected:    -1,
		},
		{
			description: "duplicate locations",
			n:           4,
			edges:       [][]int{{0, 1, 10}, {1, 2, 10}, {2, 3, 10}},
			locations:   []int{1, 1, 3},
			expected:    2,
		},
		{
			description: "empty locations list",
			n:           4,
			edges:       [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}},
			locations:   []int{},
			expected:    -1,
		},
		{
			description: "one location test",
			n:           3,
			edges:       [][]int{{0, 1, 4}, {1, 2, 6}, {0, 2, 10}},
			locations:   []int{2},
			expected:    2,
		},
		{
			description: "tie break optimal meeting point",
			n:           3,
			edges:       [][]int{{0, 1, 5}, {0, 2, 5}, {1, 2, 5}},
			locations:   []int{0, 2},
			expected:    0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := MeetingOptimal(tc.n, tc.edges, tc.locations)
			if result != tc.expected {
				t.Fatalf("MeetingOptimal(%d, %v, %v) = %d; expected %d", tc.n, tc.edges, tc.locations, result, tc.expected)
			}
		})
	}
}