package resilience

import "testing"

func TestIsResilient(t *testing.T) {
	for _, tc := range resilienceTests {
		t.Run(tc.description, func(t *testing.T) {
			got := IsResilient(tc.n, tc.adjMatrix, tc.data)
			if got != tc.expected {
				t.Errorf("IsResilient(%d, %v, %v) = %v, want %v",
					tc.n, tc.adjMatrix, tc.data, got, tc.expected)
			}
		})
	}
}

func BenchmarkIsResilient(b *testing.B) {
	if testing.Short() {
		b.Skip("skipping benchmark in short mode.")
	}
	for i := 0; i < b.N; i++ {
		for _, test := range resilienceTests {
			IsResilient(test.n, test.adjMatrix, test.data)
		}
	}
}