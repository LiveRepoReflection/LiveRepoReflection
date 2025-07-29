package energium_allocation

import (
	"math"
)

type planet struct {
	resourceProd    int
	energiumNeed    int
	stabilityCoeff  float64
	allocation      int
	tradePartners   []int
	tradeEfficiency []float64
}

func OptimalAllocation(
	N int,
	M int,
	resourceProduction []int,
	energiumNeed []int,
	stabilityCoefficient []float64,
	tradePartners [][]int,
	tradeEfficiency [][]float64,
) []int {
	// Initialize planets
	planets := make([]planet, N)
	for i := 0; i < N; i++ {
		planets[i] = planet{
			resourceProd:    resourceProduction[i],
			energiumNeed:    energiumNeed[i],
			stabilityCoeff:  stabilityCoefficient[i],
			tradePartners:   tradePartners[i],
			tradeEfficiency: tradeEfficiency[i],
		}
	}

	// Initialize DP table
	dp := make([][]float64, N+1)
	for i := range dp {
		dp[i] = make([]float64, M+1)
	}

	// Initialize allocation tracking
	allocations := make([][][]int, N+1)
	for i := range allocations {
		allocations[i] = make([][]int, M+1)
		for j := range allocations[i] {
			allocations[i][j] = make([]int, N)
		}
	}

	// Dynamic programming approach
	for i := 1; i <= N; i++ {
		for j := 0; j <= M; j++ {
			maxStability := -1.0
			bestAlloc := 0
			var bestPrevAlloc []int

			// Try all possible allocations for current planet
			for k := 0; k <= min(j, planets[i-1].energiumNeed); k++ {
				currentStability := planets[i-1].stabilityCoeff * float64(planets[i-1].resourceProd) * math.Pow(float64(k), 2)
				remaining := j - k
				totalStability := dp[i-1][remaining] + currentStability

				if totalStability > maxStability {
					maxStability = totalStability
					bestAlloc = k
					bestPrevAlloc = make([]int, N)
					copy(bestPrevAlloc, allocations[i-1][remaining])
				}
			}

			dp[i][j] = maxStability
			if bestPrevAlloc != nil {
				copy(allocations[i][j], bestPrevAlloc)
				allocations[i][j][i-1] = bestAlloc
			}
		}
	}

	// Find the best allocation for total M energium
	maxStability := -1.0
	bestAllocation := make([]int, N)
	for j := 0; j <= M; j++ {
		if dp[N][j] > maxStability {
			maxStability = dp[N][j]
			copy(bestAllocation, allocations[N][j])
		}
	}

	// Apply trade optimization
	optimizedAllocation := optimizeWithTrade(planets, bestAllocation, M)

	return optimizedAllocation
}

func optimizeWithTrade(planets []planet, allocation []int, M int) []int {
	// This is a placeholder for trade optimization logic
	// In a complete solution, this would implement the trade optimization
	// For now, we just return the initial allocation
	result := make([]int, len(allocation))
	copy(result, allocation)
	return result
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}