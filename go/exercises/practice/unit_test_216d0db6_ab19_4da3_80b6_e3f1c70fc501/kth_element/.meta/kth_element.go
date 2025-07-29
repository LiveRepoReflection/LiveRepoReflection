package kthelement

import "math"

// FindKthElement finds the k-th smallest element across all data nodes
func FindKthElement(n int, k int, queryNode func(int, int) int) int {
	// Define the search range
	left := math.MinInt32
	right := math.MaxInt32

	// Binary search for the k-th element
	for left < right {
		mid := left + (right-left)/2

		// Count total elements less than or equal to mid across all nodes
		count := 0
		for i := 0; i < n; i++ {
			count += queryNode(i, mid)
		}

		// Adjust search range based on count
		if count < k {
			left = mid + 1
		} else {
			right = mid
		}
	}

	return left
}

// Helper function to check if a value is valid k-th element
func isValidKthElement(n int, k int, value int, queryNode func(int, int) int) bool {
	// Count elements less than or equal to value
	count := 0
	for i := 0; i < n; i++ {
		count += queryNode(i, value)
	}

	// Count elements less than value
	countLess := 0
	for i := 0; i < n; i++ {
		countLess += queryNode(i, value-1)
	}

	// Value is valid k-th element if:
	// 1. There are at least k elements <= value
	// 2. There are less than k elements < value
	return count >= k && countLess < k
}