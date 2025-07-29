package network_partitioning

import (
	"math"
	"testing"
)

type testCase struct {
	name string
	N    int
	K    int
	L    []int
	C    [][]int
}

func checkValidAssignment(t *testing.T, assignment []int, N int, K int) {
	if len(assignment) != N {
		t.Fatalf("expected assignment length %d, got %d", N, len(assignment))
	}
	for idx, part := range assignment {
		if part < 0 || part >= K {
			t.Errorf("node %d has invalid partition value: %d", idx, part)
		}
	}
}

func TestPartitionNetwork(t *testing.T) {
	tests := []testCase{
		{
			name: "Single node",
			N:    1,
			K:    1,
			L:    []int{50},
			C: [][]int{
				{0},
			},
		},
		{
			name: "Fully connected small network",
			N:    4,
			K:    2,
			L:    []int{10, 20, 30, 40},
			C: [][]int{
				{0, 5, 10, 15},
				{5, 0, 7, 12},
				{10, 7, 0, 3},
				{15, 12, 3, 0},
			},
		},
		{
			name: "Uniform loads, no communication cost",
			N:    5,
			K:    3,
			L:    []int{10, 10, 10, 10, 10},
			C: [][]int{
				{0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0},
				{0, 0, 0, 0, 0},
			},
		},
		{
			name: "Sparse network random scenario",
			N:    6,
			K:    3,
			L:    []int{20, 30, 40, 50, 60, 70},
			C: [][]int{
				{0, 3, 0, 0, 5, 0},
				{3, 0, 7, 0, 0, 8},
				{0, 7, 0, 2, 0, 0},
				{0, 0, 2, 0, 4, 6},
				{5, 0, 0, 4, 0, 1},
				{0, 8, 0, 6, 1, 0},
			},
		},
		{
			name: "Edge case: Multiple nodes with K less than N",
			N:    10,
			K:    4,
			L:    []int{2, 3, 5, 7, 11, 13, 17, 19, 23, 29},
			C: func() [][]int {
				m := make([][]int, 10)
				for i := 0; i < 10; i++ {
					m[i] = make([]int, 10)
					for j := 0; j < 10; j++ {
						if i == j {
							m[i][j] = 0
						} else {
							// Use a deterministic function to generate a cost.
							m[i][j] = int(math.Abs(float64(i-j)))*2 + ((i + j) % 5)
						}
					}
				}
				return m
			}(),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			assignment := PartitionNetwork(tc.N, tc.K, tc.L, tc.C)
			checkValidAssignment(t, assignment, tc.N, tc.K)
		})
	}
}

func BenchmarkPartitionNetwork(b *testing.B) {
	N := 50
	K := 5
	L := make([]int, N)
	C := make([][]int, N)
	for i := 0; i < N; i++ {
		L[i] = (i * 3) % 100
		C[i] = make([]int, N)
		for j := 0; j < N; j++ {
			if i == j {
				C[i][j] = 0
			} else {
				C[i][j] = (i+j)%50 + 1
			}
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		assignment := PartitionNetwork(N, K, L, C)
		if len(assignment) != N {
			b.Fatalf("invalid partition length: got %d, want %d", len(assignment), N)
		}
		for _, part := range assignment {
			if part < 0 || part >= K {
				b.Fatalf("invalid partition value: %d", part)
			}
		}
	}
}