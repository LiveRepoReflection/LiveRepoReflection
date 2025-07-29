package resource_alloc

import (
	"math"
)

// OptimalResourceAllocation finds the minimum cost allocation of services to machines
func OptimalResourceAllocation(N, M int, serviceRequirements [][]int, machineCapacities [][]int, costMatrix [][]int, instanceCount []int) int {
	// Use dynamic programming with bitmask to solve
	// dp[mask][machine] represents minimum cost to allocate services in mask to machines 0 to machine
	K := len(serviceRequirements[0]) // number of resource types
	numStates := 1 << N
	dp := make([][]int, numStates)
	for i := range dp {
		dp[i] = make([]int, M)
		for j := range dp[i] {
			dp[i][j] = math.MaxInt32
		}
	}
	dp[0][0] = 0

	// Helper function to check if allocation is feasible for a machine
	isFeasible := func(serviceMask int, machine int) bool {
		resources := make([]int, K)
		// Calculate total resources needed for selected services
		for service := 0; service < N; service++ {
			if (serviceMask & (1 << service)) != 0 {
				for k := 0; k < K; k++ {
					resources[k] += serviceRequirements[service][k] * instanceCount[service]
				}
			}
		}
		// Check if machine has enough capacity
		for k := 0; k < K; k++ {
			if resources[k] > machineCapacities[machine][k] {
				return false
			}
		}
		return true
	}

	// Calculate cost for allocating services to a machine
	calculateCost := func(serviceMask int, machine int) int {
		cost := 0
		for service := 0; service < N; service++ {
			if (serviceMask & (1 << service)) != 0 {
				cost += costMatrix[service][machine] * instanceCount[service]
			}
		}
		return cost
	}

	// Main DP loop
	for machine := 0; machine < M; machine++ {
		for mask := 0; mask < numStates; mask++ {
			if dp[mask][machine] == math.MaxInt32 {
				continue
			}

			// Try allocating remaining services to next machine
			if machine == M-1 {
				// On last machine, must allocate all remaining services
				remainingMask := numStates - 1 - mask
				if isFeasible(remainingMask, machine) {
					cost := calculateCost(remainingMask, machine)
					dp[numStates-1][machine] = min(dp[numStates-1][machine], dp[mask][machine]+cost)
				}
			} else {
				// Try different combinations of remaining services
				remainingMask := numStates - 1 - mask
				for submask := remainingMask; ; submask = (submask - 1) & remainingMask {
					if isFeasible(submask, machine) {
						cost := calculateCost(submask, machine)
						newMask := mask | submask
						dp[newMask][machine+1] = min(dp[newMask][machine+1], dp[mask][machine]+cost)
					}
					if submask == 0 {
						break
					}
				}
			}
		}
	}

	// Check if we found a valid solution
	if dp[numStates-1][M-1] == math.MaxInt32 {
		return -1
	}
	return dp[numStates-1][M-1]
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}