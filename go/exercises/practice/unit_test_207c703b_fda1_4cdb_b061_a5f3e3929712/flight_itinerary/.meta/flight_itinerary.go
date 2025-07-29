package flight_itinerary

import (
	"math/bits"
)

const INF = 1 << 60

// OptimalItinerary computes the minimum cost of an itinerary starting at city 0,
// visiting all cities exactly once, and returning to city 0.
// N is the total number of cities.
// price is a function that returns the cost of moving from city i to city j given that
// k cities have already been visited (excluding the starting city 0).
// k ranges from 0 (for the first flight from city 0) to N-1 (for the last flight before returning to city 0).
func OptimalItinerary(N int, price func(i, j, k int) int) int {
	if N <= 1 {
		return 0
	}

	// total states for bitmasking: state mask will have bit i set if city i is visited.
	fullMask := 1 << N

	// dp[mask][i]: min cost to reach city i with visited mask = mask.
	dp := make([][]int, fullMask)
	for m := 0; m < fullMask; m++ {
		dp[m] = make([]int, N)
		for i := 0; i < N; i++ {
			dp[m][i] = INF
		}
	}
	// Start at city 0; count of flights taken so far is 0.
	dp[1<<0][0] = 0

	// Iterate over all states.
	for mask := 0; mask < fullMask; mask++ {
		// Determine the number of flights already taken (equals visited count - 1).
		// bits.OnesCount(uint(mask)) returns count of visited cities.
		flights := bits.OnesCount(uint(mask)) - 1
		for u := 0; u < N; u++ {
			// Check if city u is visited in this mask.
			if mask&(1<<u) == 0 {
				continue
			}
			// If current cost is INF, skip this state.
			if dp[mask][u] == INF {
				continue
			}
			// Try to visit a new city v which is not yet visited.
			for v := 0; v < N; v++ {
				if mask&(1<<v) != 0 {
					continue
				}
				nextMask := mask | (1 << v)
				cost := dp[mask][u] + price(u, v, flights)
				if cost < dp[nextMask][v] {
					dp[nextMask][v] = cost
				}
			}
		}
	}

	// All cities visited mask.
	finalMask := fullMask - 1
	ans := INF
	// For each city u that could be the last visited city (excluding city 0 as intermediate last city)
	// add the cost of returning to city 0 with k = N-1 flights already taken.
	for u := 0; u < N; u++ {
		if dp[finalMask][u] == INF {
			continue
		}
		totalCost := dp[finalMask][u] + price(u, 0, N-1)
		if totalCost < ans {
			ans = totalCost
		}
	}
	return ans
}