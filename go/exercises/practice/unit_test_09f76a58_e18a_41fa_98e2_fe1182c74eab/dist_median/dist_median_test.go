package dist_median

import (
	"math"
	"testing"
)

func almostEqual(a, b float64) bool {
	const epsilon = 1e-9
	return math.Abs(a-b) < epsilon
}

func TestDistributedMedian(t *testing.T) {
	testCases := []struct {
		description string
		data        [][]int64
		expected    float64
	}{
		{
			description: "single node, single element",
			data:        [][]int64{{5}},
			expected:    5.0,
		},
		{
			description: "single node, two elements even count",
			data:        [][]int64{{1, 3}},
			expected:    2.0,
		},
		{
			description: "single node, odd count",
			data:        [][]int64{{1, 3, 5}},
			expected:    3.0,
		},
		{
			description: "multiple nodes, even total count",
			data: [][]int64{
				{1, 3, 5},
				{2, 4, 6},
			},
			// Combined sorted: [1,2,3,4,5,6], median = (3+4)/2 = 3.5
			expected: 3.5,
		},
		{
			description: "multiple nodes, odd total count",
			data: [][]int64{
				{1, 2},
				{3, 4, 5},
			},
			// Combined sorted: [1,2,3,4,5], median = 3
			expected: 3.0,
		},
		{
			description: "multiple nodes with duplicates",
			data: [][]int64{
				{1, 2, 2},
				{2, 3, 4},
			},
			// Combined sorted: [1,2,2,2,3,4], median = (2+2)/2 = 2
			expected: 2.0,
		},
		{
			description: "empty dataset (no worker nodes)",
			data:        [][]int64{},
			expected:    0.0,
		},
		{
			description: "empty node among nodes",
			data: [][]int64{
				{},
				{1, 2, 3, 4},
			},
			// Combined sorted: [1,2,3,4], median = (2+3)/2 = 2.5
			expected: 2.5,
		},
		{
			description: "all nodes empty",
			data: [][]int64{
				{},
				{},
			},
			// No elements, median is defined as 0.0
			expected: 0.0,
		},
	}

	for _, tc := range testCases {
		result := DistributedMedian(tc.data)
		if !almostEqual(result, tc.expected) {
			t.Errorf("Failed %q: Expected median %v, got %v", tc.description, tc.expected, result)
		}
	}
}

func BenchmarkDistributedMedian(b *testing.B) {
	// Create a sample workload with multiple nodes and many elements.
	// For simplicity, each node's data is a sorted slice of int64.
	numNodes := 1000
	data := make([][]int64, numNodes)
	for i := 0; i < numNodes; i++ {
		// Each node contains 100 sorted integers.
		nodeData := make([]int64, 100)
		for j := 0; j < 100; j++ {
			// Ensure sorted order by computing a predictable value.
			nodeData[j] = int64(i*100 + j)
		}
		data[i] = nodeData
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = DistributedMedian(data)
	}
}