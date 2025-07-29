package dist_median

import (
	"sort"
)

func DistributedMedian(data [][]int64) float64 {
	// First, calculate total number of elements, and determine the global minimum and maximum values.
	totalCount := int64(0)
	var globalMin, globalMax int64
	globalMin = 0
	globalMax = 0
	first := true
	for _, node := range data {
		if len(node) == 0 {
			continue
		}
		totalCount += int64(len(node))
		if first {
			globalMin = node[0]
			globalMax = node[len(node)-1]
			first = false
		} else {
			if node[0] < globalMin {
				globalMin = node[0]
			}
			if node[len(node)-1] > globalMax {
				globalMax = node[len(node)-1]
			}
		}
	}

	// If there are no elements in any node, return 0.0 as median.
	if totalCount == 0 {
		return 0.0
	}

	// kth returns the kth smallest element from the combined datasets.
	// k is 1-indexed.
	kth := func(k int64) int64 {
		low := globalMin
		high := globalMax
		var answer int64 = high

		// binary search on value range [low, high]
		for low <= high {
			mid := low + (high-low)/2
			count := int64(0)
			for _, node := range data {
				// Count elements in node that are <= mid using binary search.
				count += int64(sort.Search(len(node), func(i int) bool {
					return node[i] > mid
				}))
			}
			if count >= k {
				answer = mid
				high = mid - 1
			} else {
				low = mid + 1
			}
		}
		return answer
	}

	if totalCount%2 == 1 {
		median := kth(totalCount/2 + 1)
		return float64(median)
	}

	left := kth(totalCount / 2)
	right := kth(totalCount/2 + 1)
	return float64(left+right) / 2.0
}