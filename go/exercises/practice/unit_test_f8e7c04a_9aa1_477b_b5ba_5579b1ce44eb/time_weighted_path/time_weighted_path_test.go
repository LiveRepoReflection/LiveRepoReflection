package time_weighted_path

import (
	"testing"
)

func TestFindMinTime(t *testing.T) {
	tests := []struct {
		name      string
		n         int
		edges     [][]int
		start     int
		end       int
		k         int
		maxTime   int
		want      int
	}{
		{
			name:    "simple path",
			n:       3,
			edges:   [][]int{{0, 1, 5}, {1, 2, 3}},
			start:   0,
			end:     2,
			k:        2,
			maxTime: 10,
			want:    8,
		},
		{
			name:    "no path exists",
			n:       3,
			edges:   [][]int{{0, 1, 5}, {2, 1, 3}},
			start:   0,
			end:     2,
			k:        2,
			maxTime: 10,
			want:    -1,
		},
		{
			name:    "multiple paths with different times",
			n:       4,
			edges:   [][]int{{0, 1, 1}, {0, 2, 5}, {1, 3, 2}, {2, 3, 1}},
			start:   0,
			end:     3,
			k:        3,
			maxTime: 6,
			want:    3,
		},
		{
			name:    "path exceeds max time",
			n:       3,
			edges:   [][]int{{0, 1, 5}, {1, 2, 6}},
			start:   0,
			end:     2,
			k:        2,
			maxTime: 10,
			want:    -1,
		},
		{
			name:    "path exceeds edge limit",
			n:       4,
			edges:   [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}, {0, 3, 5}},
			start:   0,
			end:     3,
			k:        2,
			maxTime: 10,
			want:    5,
		},
		{
			name:    "duplicate edges with different weights",
			n:       2,
			edges:   [][]int{{0, 1, 3}, {0, 1, 5}, {0, 1, 2}},
			start:   0,
			end:     1,
			k:        1,
			maxTime: 10,
			want:    2,
		},
		{
			name:    "start equals end",
			n:       3,
			edges:   [][]int{{0, 1, 5}, {1, 2, 3}},
			start:   0,
			end:     0,
			k:        2,
			maxTime: 10,
			want:    0,
		},
		{
			name:    "cycle in graph",
			n:       3,
			edges:   [][]int{{0, 1, 2}, {1, 2, 3}, {2, 0, 1}},
			start:   0,
			end:     2,
			k:        3,
			maxTime: 10,
			want:    5,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := FindMinTime(tt.n, tt.edges, tt.start, tt.end, tt.k, tt.maxTime); got != tt.want {
				t.Errorf("FindMinTime() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkFindMinTime(b *testing.B) {
	n := 50
	edges := make([][]int, 0)
	for i := 0; i < 49; i++ {
		edges = append(edges, []int{i, i + 1, 1})
	}
	start := 0
	end := 49
	k := 50
	maxTime := 100

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindMinTime(n, edges, start, end, k, maxTime)
	}
}