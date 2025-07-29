package router_latency

import (
	"testing"
)

func TestMinMaxLatency(t *testing.T) {
	tests := []struct {
		name     string
		N        int
		K        int
		edges    [][3]int
		expected int
	}{
		{
			name:     "simple 4-node cycle",
			N:        4,
			K:        2,
			edges:    [][3]int{{1, 2, 10}, {2, 3, 10}, {3, 4, 10}, {4, 1, 10}},
			expected: 10,
		},
		{
			name:     "star topology",
			N:        5,
			K:        1,
			edges:    [][3]int{{1, 2, 5}, {1, 3, 5}, {1, 4, 5}, {1, 5, 5}},
			expected: 5,
		},
		{
			name:     "complex network",
			N:        6,
			K:        3,
			edges:    [][3]int{{1, 2, 3}, {2, 3, 4}, {3, 4, 2}, {4, 5, 6}, {5, 6, 1}, {6, 1, 7}, {2, 5, 5}},
			expected: 3,
		},
		{
			name:     "single router must be central",
			N:        3,
			K:        1,
			edges:    [][3]int{{1, 2, 10}, {2, 3, 10}},
			expected: 10,
		},
		{
			name:     "all nodes are routers",
			N:        4,
			K:        4,
			edges:    [][3]int{{1, 2, 5}, {2, 3, 5}, {3, 4, 5}, {4, 1, 5}},
			expected: 0,
		},
		{
			name:     "impossible case (K > N)",
			N:        3,
			K:        5,
			edges:    [][3]int{{1, 2, 1}, {2, 3, 1}},
			expected: -1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinMaxLatency(tt.N, tt.K, tt.edges)
			if got != tt.expected {
				t.Errorf("MinMaxLatency() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkMinMaxLatency(b *testing.B) {
	N := 100
	K := 10
	edges := make([][3]int, 0)
	for i := 1; i < N; i++ {
		edges = append(edges, [3]int{i, i + 1, 1})
	}
	edges = append(edges, [3]int{1, N, 1})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinMaxLatency(N, K, edges)
	}
}