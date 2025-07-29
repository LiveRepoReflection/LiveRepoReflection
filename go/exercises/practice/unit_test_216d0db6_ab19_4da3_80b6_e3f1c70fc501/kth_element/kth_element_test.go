package kthelement

import (
	"fmt"
	"testing"
)

type testCase struct {
	n            int
	k            int
	hiddenArrays [][]int
	expected     int
}

// Mock implementation of queryNode for testing
func createQueryNodeFunc(hiddenArrays [][]int) func(int, int) int {
	return func(nodeID int, value int) int {
		count := 0
		for _, num := range hiddenArrays[nodeID] {
			if num <= value {
				count++
			}
		}
		return count
	}
}

var testCases = []testCase{
	{
		n: 3,
		k: 5,
		hiddenArrays: [][]int{
			{1, 5, 9},
			{2, 6, 10, 12},
			{3, 7, 11},
		},
		expected: 6,
	},
	{
		n: 2,
		k: 1,
		hiddenArrays: [][]int{
			{5, 10},
			{1, 2},
		},
		expected: 1,
	},
	{
		n: 4,
		k: 8,
		hiddenArrays: [][]int{
			{1, 3, 5},
			{2, 4, 6},
			{7, 9, 11},
			{8, 10, 12},
		},
		expected: 8,
	},
	{
		n: 1,
		k: 3,
		hiddenArrays: [][]int{
			{1, 2, 3, 4, 5},
		},
		expected: 3,
	},
	{
		n: 3,
		k: 1,
		hiddenArrays: [][]int{
			{5},
			{3},
			{1},
		},
		expected: 1,
	},
}

func TestFindKthElement(t *testing.T) {
	for i, tc := range testCases {
		t.Run(fmt.Sprintf("Test Case %d", i), func(t *testing.T) {
			queryNode := createQueryNodeFunc(tc.hiddenArrays)
			result := FindKthElement(tc.n, tc.k, queryNode)
			if result != tc.expected {
				t.Errorf("Test case %d: expected %d, got %d", i, tc.expected, result)
			}
		})
	}
}

func TestFindKthElementWithLargeDataset(t *testing.T) {
	// Create a large dataset
	n := 100
	k := 500
	hiddenArrays := make([][]int, n)
	for i := 0; i < n; i++ {
		hiddenArrays[i] = make([]int, 10)
		for j := 0; j < 10; j++ {
			hiddenArrays[i][j] = i*10 + j
		}
	}

	queryNode := createQueryNodeFunc(hiddenArrays)
	result := FindKthElement(n, k, queryNode)

	// Validate the result by counting elements less than or equal to result
	totalCount := 0
	for i := 0; i < n; i++ {
		totalCount += queryNode(i, result)
	}

	if totalCount < k {
		t.Errorf("Result %d is too small: only %d elements are less than or equal to it", result, totalCount)
	}

	// Check that result-1 has fewer than k elements
	totalCountMinus := 0
	for i := 0; i < n; i++ {
		totalCountMinus += queryNode(i, result-1)
	}

	if totalCountMinus >= k {
		t.Errorf("Result %d is too large: %d elements are less than or equal to %d", result, totalCountMinus, result-1)
	}
}

func TestEdgeCases(t *testing.T) {
	// Test with single element
	singleElement := [][]int{{1}}
	queryNode := createQueryNodeFunc(singleElement)
	result := FindKthElement(1, 1, queryNode)
	if result != 1 {
		t.Errorf("Single element test failed: expected 1, got %d", result)
	}

	// Test with identical elements
	identicalElements := [][]int{
		{5, 5, 5},
		{5, 5, 5},
		{5, 5, 5},
	}
	queryNode = createQueryNodeFunc(identicalElements)
	result = FindKthElement(3, 5, queryNode)
	if result != 5 {
		t.Errorf("Identical elements test failed: expected 5, got %d", result)
	}
}

func BenchmarkFindKthElement(b *testing.B) {
	// Create a large dataset for benchmarking
	n := 1000
	k := 5000
	hiddenArrays := make([][]int, n)
	for i := 0; i < n; i++ {
		hiddenArrays[i] = make([]int, 10)
		for j := 0; j < 10; j++ {
			hiddenArrays[i][j] = i*10 + j
		}
	}

	queryNode := createQueryNodeFunc(hiddenArrays)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindKthElement(n, k, queryNode)
	}
}