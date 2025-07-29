package network_profit

// MaxNetworkProfit computes the maximum profit obtainable by selecting a connected network (spanning tree)
// over a subset of cities (with size between minCities and maxCities) such that the total cost does not exceed budget.
// The profit of the network is the sum of profits for every chosen cable (edge) used in the spanning tree.
// If no valid network exists under the given constraints, it returns -1.
//
// This implementation uses a bitmask dynamic programming approach over subsets of the cities. Each DP state
// represents a connected spanning tree built over a subset of cities, with a last added city. To ease transitions,
// we store a set of Pareto-optimal (cost, profit) pairs for each state. The DP transitions add a new city
// by “attaching” it from the current connected tree through an available cable.
func MaxNetworkProfit(N int, profits [][]int, minCities, maxCities, budget int, costs [][]int) int {
	// Define a struct to hold (cost, profit) pair.
	type pair struct {
		cost   int
		profit int
	}
	// Number of DP states: 1<<N * N.
	dp := make([][]([]pair), 1<<N)
	for m := 0; m < (1 << N); m++ {
		dp[m] = make([][]pair, N)
	}

	// Helper: add a new pair to a slice and maintain Pareto-optimality.
	// A new pair is added if it is not dominated by an existing pair.
	// Also, remove any pairs that are dominated by the new pair.
	addPair := func(slice []pair, newPair pair) []pair {
		// Skip if newPair is strictly worse than an existing pair.
		for _, p := range slice {
			if p.cost <= newPair.cost && p.profit >= newPair.profit {
				return slice
			}
		}
		// Remove pairs that are dominated by newPair.
		newSlice := make([]pair, 0, len(slice)+1)
		for _, p := range slice {
			if !(newPair.cost <= p.cost && newPair.profit >= p.profit) {
				newSlice = append(newSlice, p)
			}
		}
		newSlice = append(newSlice, newPair)
		return newSlice
	}

	// Initialization: for each single city, a connected network with cost 0 and profit 0.
	for i := 0; i < N; i++ {
		mask := 1 << i
		dp[mask][i] = append(dp[mask][i], pair{cost: 0, profit: 0})
	}

	// dp over subsets
	for mask := 0; mask < (1 << N); mask++ {
		// For every city i included in mask, try to add a new city j not in mask.
		for i := 0; i < N; i++ {
			if (mask & (1 << i)) == 0 {
				continue
			}
			state := dp[mask][i]
			if len(state) == 0 {
				continue
			}
			// Try to add a new city j not in mask which is adjacent (allowed edge)
			for j := 0; j < N; j++ {
				if mask&(1<<j) != 0 {
					continue
				}
				// Only consider the edge if connection is possible (cost less than 1000000)
				if costs[i][j] >= 1000000 {
					continue
				}
				newMask := mask | (1 << j)
				for _, p := range state {
					newCost := p.cost + costs[i][j]
					// If the running cost already exceeds the maximum budget, skip.
					if newCost > budget {
						continue
					}
					newProfit := p.profit + profits[i][j]
					// Update dp[newMask][j] with (newCost, newProfit) while keeping Pareto-optimal pairs.
					dp[newMask][j] = addPair(dp[newMask][j], pair{cost: newCost, profit: newProfit})
				}
			}
		}
	}

	// Now, search over all dp states corresponding to a connected network with size in [minCities, maxCities]
	best := -1
	for mask := 0; mask < (1 << N); mask++ {
		// Count the number of nodes in mask.
		cnt := 0
		for m := mask; m > 0; m &= m - 1 {
			cnt++
		}
		if cnt < minCities || cnt > maxCities {
			continue
		}
		// For every ending city in this mask, check the Pareto pairs.
		for i := 0; i < N; i++ {
			if mask&(1<<i) == 0 {
				continue
			}
			for _, p := range dp[mask][i] {
				if p.cost <= budget && p.profit > best {
					best = p.profit
				}
			}
		}
	}
	return best
}