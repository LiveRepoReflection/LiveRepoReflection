package network_quorum

import (
	"testing"
)

func TestMinimumTotalReplicas(t *testing.T) {
	tests := []struct {
		name string
		n    int
		m    int
		k    int
		want int
	}{
		{
			name: "k=1 minimal case",
			n:    5,
			m:    3,
			k:    1,
			// For k = 1, minimum replicas per data item = 2*1-1 = 1, total = 3 data items * 1 = 3.
			want: 3,
		},
		{
			name: "sample case",
			n:    5,
			m:    3,
			k:    2,
			// For k = 2, minimum replicas per data item = 2*2-1 = 3, total = 3 data items * 3 = 9.
			want: 9,
		},
		{
			name: "k=3 case",
			n:    100,
			m:    2,
			k:    3,
			// For k = 3, minimum replicas per data item = 2*3-1 = 5, total = 2 data items * 5 = 10.
			want: 10,
		},
		{
			name: "larger case",
			n:    200,
			m:    10,
			k:    4,
			// For k = 4, minimum replicas per data item = 2*4-1 = 7, total = 10 data items * 7 = 70.
			want: 70,
		},
		{
			name: "edge case n equals small limit",
			n:    10,
			m:    2,
			k:    5,
			// For k = 5, minimum replicas per data item = 2*5-1 = 9, total = 2 data items * 9 = 18.
			want: 18,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := MinimumTotalReplicas(tc.n, tc.m, tc.k)
			if got != tc.want {
				t.Errorf("MinimumTotalReplicas(%d, %d, %d) = %d; want %d", tc.n, tc.m, tc.k, got, tc.want)
			}
		})
	}
}

func BenchmarkMinimumTotalReplicas(b *testing.B) {
	// Use large values within constraints for benchmarking.
	n, m, k := 100000, 100000, 50
	for i := 0; i < b.N; i++ {
		_ = MinimumTotalReplicas(n, m, k)
	}
}