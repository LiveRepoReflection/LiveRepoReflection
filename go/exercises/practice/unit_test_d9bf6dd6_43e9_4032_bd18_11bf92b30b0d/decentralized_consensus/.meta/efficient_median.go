package decentralized_consensus

// Note: This file contains an alternative implementation for median calculation
// that uses the quickselect algorithm for better performance when the number
// of nodes and values gets large. The main implementation uses a simple sort-based
// approach for clarity, but this implementation would be more efficient for large datasets.

// efficientMedian calculates the median using quickselect algorithm
// which has O(n) average time complexity instead of O(n log n) for sort-based approach
func efficientMedian(values []int64) int64 {
	length := len(values)
	if length == 0 {
		return 0
	}
	
	// Make a copy to avoid modifying the original
	valuesCopy := make([]int64, length)
	copy(valuesCopy, values)
	
	if length%2 == 1 {
		// Odd number of elements
		k := length / 2
		return quickSelect(valuesCopy, 0, length-1, k)
	} else {
		// Even number of elements: take the smaller of the two middle values
		k := (length / 2) - 1
		return quickSelect(valuesCopy, 0, length-1, k)
	}
}

// quickSelect finds the k-th smallest element in the slice
func quickSelect(arr []int64, left, right, k int) int64 {
	if left == right {
		return arr[left]
	}
	
	// Partition the array around a pivot
	pivotIndex := partition(arr, left, right)
	
	if k == pivotIndex {
		return arr[k]
	} else if k < pivotIndex {
		return quickSelect(arr, left, pivotIndex-1, k)
	} else {
		return quickSelect(arr, pivotIndex+1, right, k)
	}
}

// partition rearranges elements in the slice and returns the pivot index
func partition(arr []int64, left, right int) int {
	// Choose right as pivot
	pivot := arr[right]
	i := left
	
	for j := left; j < right; j++ {
		if arr[j] <= pivot {
			arr[i], arr[j] = arr[j], arr[i]
			i++
		}
	}
	
	arr[i], arr[right] = arr[right], arr[i]
	return i
}