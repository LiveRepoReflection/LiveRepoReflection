package billboard_placement

func MaxRevenue(positions []int, revenue []int, minDistance int) int {
	n := len(positions)
	if n == 0 {
		return 0
	}

	dp := make([]int, n)
	dp[0] = revenue[0]

	for i := 1; i < n; i++ {
		candidate := revenue[i]
		idx := search(positions, i, positions[i]-minDistance)
		if idx != -1 {
			candidate += dp[idx]
		}
		if dp[i-1] > candidate {
			dp[i] = dp[i-1]
		} else {
			dp[i] = candidate
		}
	}
	return dp[n-1]
}

func search(positions []int, i int, target int) int {
	low := 0
	high := i - 1
	result := -1
	for low <= high {
		mid := low + (high-low)/2
		if positions[mid] < target {
			result = mid
			low = mid + 1
		} else {
			high = mid - 1
		}
	}
	return result
}