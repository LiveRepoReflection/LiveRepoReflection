package dynamic_route

import (
	"testing"
)

func TestFindOptimalRoute(t *testing.T) {
	tests := []struct {
		name        string
		N           int
		T           int
		snapshots   [][][]int
		queries     [][4]int
		expected    []int
		expectError bool
	}{
		{
			name: "basic test case",
			N:    4,
			T:    3,
			snapshots: [][][]int{
				{{0, 1, 2}, {1, 2, 3}},
				{{0, 2, 1}, {2, 3, 4}},
				{{0, 3, 5}},
			},
			queries: [][4]int{
				{0, 3, 0, 2},
			},
			expected:    []int{5},
			expectError: false,
		},
		{
			name: "no path exists",
			N:    3,
			T:    2,
			snapshots: [][][]int{
				{{0, 1, 1}},
				{{1, 2, 2}},
			},
			queries: [][4]int{
				{0, 2, 0, 0},
			},
			expected:    []int{-1},
			expectError: false,
		},
		{
			name: "multiple optimal paths",
			N:    4,
			T:    3,
			snapshots: [][][]int{
				{{0, 1, 1}, {0, 2, 4}},
				{{1, 3, 3}, {2, 3, 2}},
				{{0, 3, 5}},
			},
			queries: [][4]int{
				{0, 3, 0, 2},
			},
			expected:    []int{4},
			expectError: false,
		},
		{
			name: "invalid time window",
			N:    3,
			T:    2,
			snapshots: [][][]int{
				{{0, 1, 1}},
				{{1, 2, 1}},
			},
			queries: [][4]int{
				{0, 2, 1, 0},
			},
			expected:    []int{-1},
			expectError: false,
		},
		{
			name: "multiple queries",
			N:    5,
			T:    4,
			snapshots: [][][]int{
				{{0, 1, 1}, {1, 2, 1}},
				{{2, 3, 1}, {3, 4, 1}},
				{{0, 4, 10}},
				{{1, 4, 4}},
			},
			queries: [][4]int{
				{0, 4, 0, 3},
				{1, 4, 1, 3},
				{0, 2, 0, 1},
			},
			expected:    []int{4, 4, 2},
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			results := make([]int, len(tt.queries))
			for i, query := range tt.queries {
				result := FindOptimalRoute(tt.N, tt.T, tt.snapshots, query[0], query[1], query[2], query[3])
				results[i] = result
			}

			for i, expected := range tt.expected {
				if results[i] != expected {
					t.Errorf("query %d: expected %d, got %d", i, expected, results[i])
				}
			}
		})
	}
}

func BenchmarkFindOptimalRoute(b *testing.B) {
	N := 100
	T := 10
	snapshots := make([][][]int, T)
	for i := 0; i < T; i++ {
		for j := 0; j < N/2; j++ {
			snapshots[i] = append(snapshots[i], []int{j, j + N/2, i + j + 1})
		}
	}
	query := [4]int{0, N - 1, 0, T - 1}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = FindOptimalRoute(N, T, snapshots, query[0], query[1], query[2], query[3])
	}
}