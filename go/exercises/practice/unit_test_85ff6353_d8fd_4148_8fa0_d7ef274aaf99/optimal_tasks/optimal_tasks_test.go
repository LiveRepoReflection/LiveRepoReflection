package optimal_tasks

import (
	"testing"
)

func TestOptimalSchedule(t *testing.T) {
	for _, tc := range taskTestCases {
		t.Run(tc.description, func(t *testing.T) {
			result := OptimalSchedule(tc.input)
			if !equalSlices(result, tc.expected) {
				t.Errorf("OptimalSchedule(%v): expected %v, got %v", tc.input, tc.expected, result)
			}
		})
	}
}

func equalSlices(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

var scheduleBench []int

func BenchmarkOptimalSchedule(b *testing.B) {
	for i := 0; i < b.N; i++ {
		for _, tc := range taskTestCases {
			scheduleBench = OptimalSchedule(tc.input)
		}
	}
}