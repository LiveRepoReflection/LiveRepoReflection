package partition

import (
	"math"
)

// OptimalPartition finds the optimal partitioning of services into k clusters
func OptimalPartition(n, k int, serviceCosts []int, edges [][]int, maxClusterSize int, maxInterClusterLatency int) int {
	// Create adjacency matrix for latencies
	latency := make([][]int, n)
	for i := range latency {
		latency[i] = make([]int, n)
		for j := range latency[i] {
			latency[i][j] = 0
		}
	}
	
	// Fill latency matrix
	for _, edge := range edges {
		u, v, l := edge[0], edge[1], edge[2]
		latency[u][v] = l
		latency[v][u] = l
	}

	// dp[mask][numClusters] represents minimum cost for subset mask split into numClusters
	dp := make(map[int]map[int]int)
	
	// Initialize dp
	for i := 0; i < (1 << n); i++ {
		dp[i] = make(map[int]int)
		for j := 0; j <= k; j++ {
			dp[i][j] = math.MaxInt32
		}
	}
	dp[0][0] = 0

	// Helper function to count bits
	countBits := func(mask int) int {
		count := 0
		for mask > 0 {
			count += mask & 1
			mask >>= 1
		}
		return count
	}

	// Helper function to calculate cluster cost and check constraints
	isValidCluster := func(cluster int) (int, bool) {
		// Check size constraint
		if countBits(cluster) > maxClusterSize {
			return 0, false
		}

		cost := 0
		// Calculate service costs
		for i := 0; i < n; i++ {
			if (cluster & (1 << i)) != 0 {
				cost += serviceCosts[i]
			}
		}
		return cost, true
	}

	// Helper function to calculate inter-cluster latency
	calculateInterClusterLatency := func(mask, cluster int) int {
		totalLatency := 0
		for i := 0; i < n; i++ {
			if (cluster & (1 << i)) == 0 {
				continue
			}
			for j := 0; j < n; j++ {
				if (mask & (1 << j)) != 0 && (cluster & (1 << j)) == 0 {
					totalLatency += latency[i][j]
				}
			}
		}
		return totalLatency
	}

	// Main DP loop
	for mask := 0; mask < (1 << n); mask++ {
		for numClusters := 0; numClusters < k; numClusters++ {
			if dp[mask][numClusters] == math.MaxInt32 {
				continue
			}

			// Try to add one more cluster
			remaining := ((1 << n) - 1) ^ mask
			subset := remaining
			for subset > 0 {
				clusterCost, valid := isValidCluster(subset)
				if !valid {
					subset = (subset - 1) & remaining
					continue
				}

				interClusterLatency := calculateInterClusterLatency(mask, subset)
				if interClusterLatency <= maxInterClusterLatency {
					newMask := mask | subset
					newCost := dp[mask][numClusters] + clusterCost
					dp[newMask][numClusters+1] = min(dp[newMask][numClusters+1], newCost)
				}
				subset = (subset - 1) & remaining
			}
		}
	}

	// Find minimum cost for valid solution
	finalMask := (1 << n) - 1
	if dp[finalMask][k] == math.MaxInt32 {
		return -1
	}
	return dp[finalMask][k]
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}