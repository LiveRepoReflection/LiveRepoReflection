package multi_hop_route

import (
	"testing"
)

func TestFindOptimalRoute(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			got := FindOptimalRoute(tc.N, tc.edges, tc.source, tc.destination, tc.intermediates)
			if got != tc.expected {
				t.Errorf("FindOptimalRoute(%d, %v, %d, %d, %v) = %d; want %d",
					tc.N, tc.edges, tc.source, tc.destination, tc.intermediates, got, tc.expected)
			}
		})
	}
}

func BenchmarkFindOptimalRoute(b *testing.B) {
	if testing.Short() {
		b.Skip("skipping benchmark in short mode")
	}
	for i := 0; i < b.N; i++ {
		for _, tc := range testCases {
			FindOptimalRoute(tc.N, tc.edges, tc.source, tc.destination, tc.intermediates)
		}
	}
}