package service_chains

import (
	"math"
)

func FindMinCost(C [][]float64, requiredServices []int, N int) float64 {
	// Validate requiredServices indices.
	for _, s := range requiredServices {
		if s < 0 || s >= N {
			return -1.0
		}
	}
	m := len(requiredServices)
	if m == 0 {
		return 0.0
	}

	// Initialize DP array: dp[mask][i] represents the minimum cost to visit
	// the set of required services represented by mask ending with requiredServices[i].
	size := 1 << m
	dp := make([][]float64, size)
	for i := 0; i < size; i++ {
		dp[i] = make([]float64, m)
		for j := 0; j < m; j++ {
			dp[i][j] = math.Inf(1)
		}
	}

	// Base case: starting with each service.
	for i := 0; i < m; i++ {
		dp[1<<i][i] = C[0][requiredServices[i]]
	}

	// DP over bitmask states.
	for mask := 0; mask < size; mask++ {
		for i := 0; i < m; i++ {
			if mask&(1<<i) == 0 {
				continue
			}
			// Current cost ending at service requiredServices[i].
			for j := 0; j < m; j++ {
				if mask&(1<<j) != 0 {
					continue
				}
				nextMask := mask | (1 << j)
				cost := dp[mask][i] + C[requiredServices[i]+1][requiredServices[j]]
				if cost < dp[nextMask][j] {
					dp[nextMask][j] = cost
				}
			}
		}
	}

	// Find minimum cost from states where all required services have been visited.
	res := math.Inf(1)
	allMask := size - 1
	for i := 0; i < m; i++ {
		if dp[allMask][i] < res {
			res = dp[allMask][i]
		}
	}
	return res
}