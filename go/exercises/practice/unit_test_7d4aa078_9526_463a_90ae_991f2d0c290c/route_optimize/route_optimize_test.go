package route_optimize

import (
	"reflect"
	"testing"
)

func TestFindOptimalRoute(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := FindOptimalRoute(tc.graph, tc.start, tc.end, tc.deadline)
			if !reflect.DeepEqual(actual, tc.expected) {
				t.Errorf("FindOptimalRoute() = %v, want %v", actual, tc.expected)
			}
		})
	}
}

func BenchmarkFindOptimalRoute(b *testing.B) {
	if testing.Short() {
		b.Skip("skipping benchmark in short mode.")
	}
	for i := 0; i < b.N; i++ {
		for _, tc := range testCases {
			FindOptimalRoute(tc.graph, tc.start, tc.end, tc.deadline)
		}
	}
}