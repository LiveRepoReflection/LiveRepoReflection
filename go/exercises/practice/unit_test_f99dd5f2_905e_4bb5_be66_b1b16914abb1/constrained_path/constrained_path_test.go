package constrained_path

import "testing"

func TestFindConstrainedPath(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := FindConstrainedPath(tc.n, tc.edges, tc.start, tc.destination, tc.maxRisk)
			if actual != tc.expected {
				t.Errorf("FindConstrainedPath(%d, %v, %d, %d, %d) = %d, want %d",
					tc.n, tc.edges, tc.start, tc.destination, tc.maxRisk, actual, tc.expected)
			}
		})
	}
}

func BenchmarkFindConstrainedPath(b *testing.B) {
	if testing.Short() {
		b.Skip("skipping benchmark in short mode.")
	}
	for i := 0; i < b.N; i++ {
		for _, tc := range testCases {
			FindConstrainedPath(tc.n, tc.edges, tc.start, tc.destination, tc.maxRisk)
		}
	}
}