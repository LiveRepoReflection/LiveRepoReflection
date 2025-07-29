package optimal_schedule

import (
	"testing"
)

type testCase struct {
	description  string
	deadlines    []int
	profits      []int
	dependencies [][]int
	maxLateness  int
	expected     int
}

func TestOptimalSchedule(t *testing.T) {
	testCases := []testCase{
		{
			description:  "Example test with chain dependencies",
			deadlines:    []int{2, 2, 3, 4},
			profits:      []int{6, 7, 8, 9},
			dependencies: [][]int{{}, {0}, {0, 1}, {2}},
			maxLateness:  2,
			expected:     30,
		},
		{
			description:  "Single task scheduled on time",
			deadlines:    []int{1},
			profits:      []int{100},
			dependencies: [][]int{{}},
			maxLateness:  0,
			expected:     100,
		},
		{
			description:  "Multiple tasks with no dependencies meeting deadlines",
			deadlines:    []int{1, 2, 3},
			profits:      []int{10, 20, 30},
			dependencies: [][]int{{}, {}, {}},
			maxLateness:  5,
			expected:     60,
		},
		{
			description:  "Tasks with same deadlines forcing choice",
			deadlines:    []int{1, 1},
			profits:      []int{100, 200},
			dependencies: [][]int{{}, {}},
			maxLateness:  0,
			expected:     200,
		},
		{
			description:  "Chain dependency with slight lateness allowed",
			deadlines:    []int{2, 2, 2},
			profits:      []int{10, 10, 100},
			dependencies: [][]int{{}, {}, {0, 1}},
			maxLateness:  1,
			expected:     120,
		},
		{
			description:  "Optional task inclusion for maximum profit",
			deadlines:    []int{1, 2, 3},
			profits:      []int{100, 1, 1},
			dependencies: [][]int{{}, {}, {0, 1}},
			maxLateness:  0,
			expected:     102,
		},
		{
			description:  "Selective scheduling with dependencies improves profit",
			deadlines:    []int{1, 2, 2},
			profits:      []int{50, 50, 100},
			dependencies: [][]int{{}, {}, {0}},
			maxLateness:  0,
			expected:     150,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := OptimalSchedule(tc.deadlines, tc.profits, tc.dependencies, tc.maxLateness)
			if result != tc.expected {
				t.Errorf("Test %q failed. Expected %d but got %d", tc.description, tc.expected, result)
			}
		})
	}
}

func BenchmarkOptimalSchedule(b *testing.B) {
	// A benchmark test with a moderately sized input.
	deadlines := []int{2, 2, 3, 4, 3, 5, 6, 6, 7, 8, 5, 9, 10, 8, 7, 9, 10, 12, 11, 13}
	profits := []int{6, 7, 8, 9, 10, 20, 15, 8, 12, 18, 7, 20, 25, 14, 10, 30, 22, 16, 19, 21}
	dependencies := [][]int{
		{}, {0}, {0, 1}, {2}, {1, 2}, {3}, {4}, {3, 4}, {5, 6}, {7},
		{5}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16},
	}
	maxLateness := 5

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = OptimalSchedule(deadlines, profits, dependencies, maxLateness)
	}
}