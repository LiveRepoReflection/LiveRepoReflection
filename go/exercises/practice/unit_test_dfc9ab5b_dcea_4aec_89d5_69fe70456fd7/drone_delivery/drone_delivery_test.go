package drone_delivery

import (
	"reflect"
	"testing"
)

// TestCase holds a single test case for CalculateTotalIdleTime.
type TestCase struct {
	name         string
	N            int
	M            int
	adjMatrix    [][]int
	origins      []int
	destinations []int
	timeWindows  [][]int
	expected     int
}

// TestCalculateTotalIdleTime runs a suite of test cases.
func TestCalculateTotalIdleTime(t *testing.T) {
	testCases := []TestCase{
		{
			name: "single_route_exact_time",
			N:    3,
			M:    1,
			adjMatrix: [][]int{
				{0, 5, -1},
				{-1, 0, 3},
				{-1, -1, 0},
			},
			origins:      []int{0},
			destinations: []int{1},
			timeWindows:  [][]int{{5, 10}},
			// travel time is 5 which meets the earliest; idle time = 0.
			expected: 0,
		},
		{
			name: "single_route_with_waiting",
			N:    3,
			M:    1,
			adjMatrix: [][]int{
				{0, 3, -1},
				{-1, 0, 4},
				{-1, -1, 0},
			},
			origins:      []int{0},
			destinations: []int{1},
			timeWindows:  [][]int{{5, 10}},
			// travel time is 3, waiting time = 5 - 3 = 2.
			expected: 2,
		},
		{
			name: "single_route_too_slow",
			N:    3,
			M:    1,
			adjMatrix: [][]int{
				{0, 12, -1},
				{-1, 0, 4},
				{-1, -1, 0},
			},
			origins:      []int{0},
			destinations: []int{1},
			timeWindows:  [][]int{{5, 10}},
			// travel time is 12 which exceeds allowed window; unsolvable.
			expected: -1,
		},
		{
			name: "single_route_no_direct_edge",
			N:    3,
			M:    1,
			adjMatrix: [][]int{
				{0, -1, -1},
				{-1, 0, 4},
				{-1, -1, 0},
			},
			origins:      []int{0},
			destinations: []int{1},
			timeWindows:  [][]int{{5, 10}},
			// No direct edge from 0 to 1.
			expected: -1,
		},
		{
			name: "multiple_routes_all_valid",
			N:    5,
			M:    3,
			adjMatrix: [][]int{
				{0, 4, -1, -1, -1},
				{-1, 0, 7, -1, -1},
				{-1, -1, 0, 5, -1},
				{-1, -1, -1, 0, 3},
				{-1, -1, -1, -1, 0},
			},
			origins:      []int{0, 1, 2},
			destinations: []int{1, 2, 3},
			timeWindows: [][]int{
				{5, 10},  // Route 0: travel time=4, idle=1
				{7, 12},  // Route 1: travel time=7, idle=0
				{8, 10},  // Route 2: travel time=5, idle=3 (wait 3 minutes to reach 8)
			},
			expected: 4, // total idle = 1+0+3 = 4
		},
		{
			name: "multiple_routes_one_invalid",
			N:    5,
			M:    3,
			adjMatrix: [][]int{
				{0, 4, -1, -1, -1},
				{-1, 0, 7, -1, -1},
				{-1, -1, 0, 5, -1},
				{-1, -1, -1, 0, 3},
				{-1, -1, -1, -1, 0},
			},
			origins:      []int{0, 1, 2},
			destinations: []int{1, 2, 4}, // route 2: from 2 to 4, no direct route
			timeWindows: [][]int{
				{5, 10},
				{7, 12},
				{6, 10},
			},
			expected: -1,
		},
		{
			name: "self_loop_valid",
			N:    2,
			M:    1,
			adjMatrix: [][]int{
				{2, -1},
				{-1, 0},
			},
			origins:      []int{0},
			destinations: []int{0},
			timeWindows:  [][]int{{3, 5}},
			// self-loop: travel time is 2, waiting time = 3-2 = 1.
			expected: 1,
		},
		{
			name: "self_loop_invalid",
			N:    2,
			M:    1,
			adjMatrix: [][]int{
				{6, -1},
				{-1, 0},
			},
			origins:      []int{0},
			destinations: []int{0},
			timeWindows:  [][]int{{3, 5}},
			// self-loop: travel time is 6, which exceeds the allowed time window.
			expected: -1,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := CalculateTotalIdleTime(tc.N, tc.M, tc.adjMatrix, tc.origins, tc.destinations, tc.timeWindows)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Fatalf("Test %s failed:\nN: %d, M: %d\nadjMatrix: %v\norigins: %v\ndestinations: %v\ntimeWindows: %v\nExpected: %d, Got: %d",
					tc.name, tc.N, tc.M, tc.adjMatrix, tc.origins, tc.destinations, tc.timeWindows, tc.expected, result)
			}
		})
	}
}