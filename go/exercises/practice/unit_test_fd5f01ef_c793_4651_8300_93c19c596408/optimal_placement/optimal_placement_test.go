package optimal_placement

import (
	"reflect"
	"testing"
)

func TestOptimalPlacement(t *testing.T) {
	tests := []struct {
		name    string
		n       int
		latency [][]int
		k       int
		want    []int
	}{
		{
			name: "Single server",
			n:    4,
			latency: [][]int{
				{0, 1, -1, 2},
				{1, 0, 1, -1},
				{-1, 1, 0, 1},
				{2, -1, 1, 0},
			},
			k:    1,
			want: []int{1},
		},
		{
			name: "Two servers",
			n:    5,
			latency: [][]int{
				{0, 1, -1, -1, 2},
				{1, 0, 1, -1, -1},
				{-1, 1, 0, 1, -1},
				{-1, -1, 1, 0, 1},
				{2, -1, -1, 1, 0},
			},
			k:    2,
			want: []int{0, 3},
		},
		{
			name: "All nodes as servers",
			n:    3,
			latency: [][]int{
				{0, 1, 2},
				{1, 0, 3},
				{2, 3, 0},
			},
			k:    3,
			want: []int{0, 1, 2},
		},
		{
			name: "Disconnected components",
			n:    6,
			latency: [][]int{
				{0, 1, -1, -1, -1, -1},
				{1, 0, -1, -1, -1, -1},
				{-1, -1, 0, 1, -1, -1},
				{-1, -1, 1, 0, -1, -1},
				{-1, -1, -1, -1, 0, 1},
				{-1, -1, -1, -1, 1, 0},
			},
			k:    3,
			want: []int{0, 2, 4},
		},
		{
			name: "Complex network",
			n:    7,
			latency: [][]int{
				{0, 1, -1, 2, -1, -1, -1},
				{1, 0, 1, -1, -1, -1, -1},
				{-1, 1, 0, 1, 2, -1, -1},
				{2, -1, 1, 0, -1, -1, 3},
				{-1, -1, 2, -1, 0, 1, -1},
				{-1, -1, -1, -1, 1, 0, 2},
				{-1, -1, -1, 3, -1, 2, 0},
			},
			k:    2,
			want: []int{1, 5},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalPlacement(tt.n, tt.latency, tt.k)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("OptimalPlacement() = %v, want %v", got, tt.want)
			}

			// Verify the result is sorted
			for i := 1; i < len(got); i++ {
				if got[i] <= got[i-1] {
					t.Errorf("Result not sorted: %v", got)
				}
			}

			// Verify all indices are valid
			for _, idx := range got {
				if idx < 0 || idx >= tt.n {
					t.Errorf("Invalid node index: %d", idx)
				}
			}

			// Verify no duplicate indices
			seen := make(map[int]bool)
			for _, idx := range got {
				if seen[idx] {
					t.Errorf("Duplicate node index: %d", idx)
				}
				seen[idx] = true
			}

			// Verify correct number of servers
			if len(got) != tt.k {
				t.Errorf("Wrong number of servers: got %d, want %d", len(got), tt.k)
			}
		})
	}
}

func TestInputValidation(t *testing.T) {
	tests := []struct {
		name    string
		n       int
		latency [][]int
		k       int
	}{
		{
			name:    "Invalid n",
			n:       0,
			latency: [][]int{{0}},
			k:       1,
		},
		{
			name:    "Invalid k",
			n:       5,
			latency: [][]int{{0}},
			k:       0,
		},
		{
			name: "Invalid latency matrix size",
			n:    3,
			latency: [][]int{
				{0, 1},
				{1, 0},
			},
			k: 1,
		},
		{
			name: "Invalid latency values",
			n:    2,
			latency: [][]int{
				{0, 1001},
				{1001, 0},
			},
			k: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			defer func() {
				if r := recover(); r == nil {
					t.Errorf("Expected panic for invalid input")
				}
			}()
			OptimalPlacement(tt.n, tt.latency, tt.k)
		})
	}
}

// Benchmark for performance testing
func BenchmarkOptimalPlacement(b *testing.B) {
	n := 10
	latency := make([][]int, n)
	for i := range latency {
		latency[i] = make([]int, n)
		for j := range latency[i] {
			if i == j {
				latency[i][j] = 0
			} else if i < j {
				latency[i][j] = (i + j) % 5 + 1
				latency[j][i] = latency[i][j]
			}
		}
	}
	k := 3

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalPlacement(n, latency, k)
	}
}