package intergalactic_network

import (
	"math"
	"testing"
)

// approxEqual checks if two float64 values are equal within a small tolerance.
func approxEqual(a, b float64) bool {
	return math.Abs(a-b) < 1e-6
}

type testCase struct {
	description string
	N           int
	K           int
	coordinates [][]int
	cost        [][]float64
	expected    float64
}

func TestMinimumCost(t *testing.T) {
	testCases := []testCase{
		{
			description: "Single planet, no cost",
			N:           1,
			K:           0,
			coordinates: [][]int{
				{0, 0},
			},
			cost: [][]float64{
				{0},
			},
			expected: 0,
		},
		{
			description: "Three planets, no wormhole",
			N:           3,
			K:           0,
			coordinates: [][]int{
				{0, 0},
				{0, 3},
				{4, 0},
			},
			cost: [][]float64{
				{0, 3, 4},
				{3, 0, 5},
				{4, 5, 0},
			},
			expected: 7, // MST: edge (0,1)=3 and (0,2)=4
		},
		{
			description: "Three planets, one wormhole",
			N:           3,
			K:           1,
			coordinates: [][]int{
				{0, 0},
				{0, 3},
				{4, 0},
			},
			cost: [][]float64{
				{0, 3, 4},
				{3, 0, 5},
				{4, 5, 0},
			},
			expected: 3, // Use wormhole to skip the edge with cost 4 (or 5) and only pay 3.
		},
		{
			description: "Four planets (square), no wormhole",
			N:           4,
			K:           0,
			coordinates: [][]int{
				{0, 0},
				{0, 2},
				{2, 0},
				{2, 2},
			},
			cost: [][]float64{
				{0, 2, 2, 2.828427},
				{2, 0, 2.828427, 2},
				{2, 2.828427, 0, 2},
				{2.828427, 2, 2, 0},
			},
			expected: 6, // MST: three edges each of weight 2.
		},
		{
			description: "Four planets (square), one wormhole",
			N:           4,
			K:           1,
			coordinates: [][]int{
				{0, 0},
				{0, 2},
				{2, 0},
				{2, 2},
			},
			cost: [][]float64{
				{0, 2, 2, 2.828427},
				{2, 0, 2.828427, 2},
				{2, 2.828427, 0, 2},
				{2.828427, 2, 2, 0},
			},
			expected: 4, // MST: use wormhole to remove one edge of weight 2.
		},
		{
			description: "Four planets (square), two wormholes",
			N:           4,
			K:           2,
			coordinates: [][]int{
				{0, 0},
				{0, 2},
				{2, 0},
				{2, 2},
			},
			cost: [][]float64{
				{0, 2, 2, 2.828427},
				{2, 0, 2.828427, 2},
				{2, 2.828427, 0, 2},
				{2.828427, 2, 2, 0},
			},
			expected: 2, // Only one edge cost remains in the MST.
		},
		{
			description: "Four planets, mixed configuration with wormholes variations",
			N:           4,
			// Coordinates: (0,0), (3,4), (6,8), (3,0)
			// Distances: 0-1:5, 0-2:10, 0-3:3, 1-2:5, 1-3:4, 2-3:8.5440037
			K: 0,
			coordinates: [][]int{
				{0, 0},
				{3, 4},
				{6, 8},
				{3, 0},
			},
			cost: [][]float64{
				{0, 5, 10, 3},
				{5, 0, 5, 4},
				{10, 5, 0, 8.5440037},
				{3, 4, 8.5440037, 0},
			},
			expected: 12, // MST: edges 0-3 (3), 1-3 (4), 1-2 (5)
		},
		{
			description: "Four planets, mixed configuration with one wormhole",
			N:           4,
			// Same coordinates as above.
			K: 1,
			coordinates: [][]int{
				{0, 0},
				{3, 4},
				{6, 8},
				{3, 0},
			},
			cost: [][]float64{
				{0, 5, 10, 3},
				{5, 0, 5, 4},
				{10, 5, 0, 8.5440037},
				{3, 4, 8.5440037, 0},
			},
			expected: 7, // With one wormhole, subtract the highest edge (5) from MST total (12-5=7).
		},
		{
			description: "Four planets, mixed configuration with two wormholes",
			N:           4,
			// Same coordinates as above.
			K: 2,
			coordinates: [][]int{
				{0, 0},
				{3, 4},
				{6, 8},
				{3, 0},
			},
			cost: [][]float64{
				{0, 5, 10, 3},
				{5, 0, 5, 4},
				{10, 5, 0, 8.5440037},
				{3, 4, 8.5440037, 0},
			},
			expected: 3, // With two wormholes, MST cost reduces to the smallest edge which is 3.
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := MinimumCost(tc.N, tc.K, tc.coordinates, tc.cost)
			if !approxEqual(actual, tc.expected) {
				t.Fatalf("Failed %s: for N=%d, K=%d, expected %v but got %v", tc.description, tc.N, tc.K, tc.expected, actual)
			}
		})
	}
}

func BenchmarkMinimumCost(b *testing.B) {
	// A moderate benchmark case using 4 planets, repeated b.N times.
	N := 4
	K := 1
	coordinates := [][]int{
		{0, 0},
		{3, 4},
		{6, 8},
		{3, 0},
	}
	cost := [][]float64{
		{0, 5, 10, 3},
		{5, 0, 5, 4},
		{10, 5, 0, 8.5440037},
		{3, 4, 8.5440037, 0},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = MinimumCost(N, K, coordinates, cost)
	}
}