package data_replication

import (
	"math"
	"testing"
)

func floatEqual(a, b float64) bool {
	const eps = 1e-6
	return math.Abs(a-b) < eps
}

type testCase struct {
	N                 int
	dataCenterCosts   []int
	bandwidthMatrix   [][]int
	dataSize          int
	primaryDataCenter int
	expected          float64
}

func TestOptimalReplicationCost(t *testing.T) {
	testCases := []testCase{
		{
			N:               3,
			dataCenterCosts: []int{10, 20, 30},
			bandwidthMatrix: [][]int{
				{0, 5, 10},
				{5, 0, 5},
				{10, 5, 0},
			},
			dataSize:          100,
			primaryDataCenter: 0,
			expected:          5020.0,
		},
		{
			N:               2,
			dataCenterCosts: []int{5, 10},
			bandwidthMatrix: [][]int{
				{0, 10},
				{10, 0},
			},
			dataSize:          50,
			primaryDataCenter: 1,
			// For replica index 0: Direct replication from 1 -> 0: 50/10 = 5 seconds.
			// Storage cost on index 0: 50 * 5 = 250.
			// Total = 5 + 250 = 255.
			expected: 255.0,
		},
		{
			N:               4,
			dataCenterCosts: []int{10, 5, 7, 20},
			bandwidthMatrix: [][]int{
				{0, 5, 0, 0},
				{0, 0, 50, 0},
				{0, 0, 0, 10},
				{0, 0, 0, 0},
			},
			dataSize:          100,
			primaryDataCenter: 0,
			// For replica index 1: Direct from 0->1: 100/5 = 20 seconds.
			// For replica index 2: Path 0->1->2: bottleneck = min(5,50)=5, time = 100/5 = 20 seconds.
			// For replica index 3: Path 0->1->2->3: bottleneck = min(5,50,10)=5, time = 100/5 = 20 seconds.
			// Max replication time = 20 seconds.
			// Storage cost for indices 1,2,3: (100*5) + (100*7) + (100*20) = 500 + 700 + 2000 = 3200.
			// Total = 20 + 3200 = 3220.
			expected: 3220.0,
		},
		{
			N:               4,
			dataCenterCosts: []int{15, 20, 5, 10},
			bandwidthMatrix: [][]int{
				{0, 0, 100, 0},
				{0, 0, 25, 50},
				{100, 25, 0, 75},
				{0, 50, 75, 0},
			},
			dataSize:          200,
			primaryDataCenter: 2,
			// For replica index 0: Direct from 2->0: 200/100 = 2 seconds.
			// For replica index 1: Best path is 2->3->1: bottleneck = min(75,50)=50, time = 200/50 = 4 seconds.
			// For replica index 3: Direct from 2->3: 200/75 ≈ 2.666667 seconds.
			// Replication time = max(2, 4, 2.666667) = 4 seconds.
			// Storage cost for replicas: cost[0] 15 + cost[1] 20 + cost[3] 10 = 45 * 200 = 9000.
			// Total = 4 + 9000 = 9004.
			expected: 9004.0,
		},
	}

	for _, tc := range testCases {
		result := OptimalReplicationCost(tc.N, tc.dataCenterCosts, tc.bandwidthMatrix, tc.dataSize, tc.primaryDataCenter)
		if !floatEqual(result, tc.expected) {
			t.Errorf("OptimalReplicationCost(%d, %v, %v, %d, %d) = %v; expected %v",
				tc.N, tc.dataCenterCosts, tc.bandwidthMatrix, tc.dataSize, tc.primaryDataCenter, result, tc.expected)
		}
	}
}

func BenchmarkOptimalReplicationCost(b *testing.B) {
	// Using a moderately sized test case for benchmarking
	N := 10
	dataCenterCosts := make([]int, N)
	bandwidthMatrix := make([][]int, N)
	for i := 0; i < N; i++ {
		dataCenterCosts[i] = (i + 1) * 5
		bandwidthMatrix[i] = make([]int, N)
		for j := 0; j < N; j++ {
			if i != j {
				bandwidthMatrix[i][j] = ((i + j) % 10 + 1) * 10
			} else {
				bandwidthMatrix[i][j] = 0
			}
		}
	}
	dataSize := 500
	primaryDataCenter := 0

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalReplicationCost(N, dataCenterCosts, bandwidthMatrix, dataSize, primaryDataCenter)
	}
}