package optimal_placement

import (
	"math"
	"sort"
)

// OptimalPlacement returns the optimal placement of k servers in a network of n nodes
func OptimalPlacement(n int, latency [][]int, k int) []int {
	validateInput(n, latency, k)

	// Calculate all-pairs shortest paths using Floyd-Warshall algorithm
	dist := floydWarshall(n, latency)

	// Generate all possible combinations of k servers
	bestPlacement := make([]int, 0)
	minMaxLatency := math.MaxInt32
	minTotalLatency := math.MaxInt32

	// Use backtracking to try all valid combinations
	current := make([]int, 0, k)
	findBestPlacement(n, k, dist, 0, current, &bestPlacement, &minMaxLatency, &minTotalLatency)

	sort.Ints(bestPlacement)
	return bestPlacement
}

// validateInput checks if the input parameters are valid
func validateInput(n int, latency [][]int, k int) {
	if n < 1 || n > 100 {
		panic("Invalid number of nodes")
	}
	if k < 1 || k > 10 || k > n {
		panic("Invalid number of servers")
	}
	if len(latency) != n {
		panic("Invalid latency matrix dimensions")
	}
	for i := 0; i < n; i++ {
		if len(latency[i]) != n {
			panic("Invalid latency matrix dimensions")
		}
		for j := 0; j < n; j++ {
			if i == j && latency[i][j] != 0 {
				panic("Invalid diagonal values in latency matrix")
			}
			if latency[i][j] != -1 && (latency[i][j] < 0 || latency[i][j] > 1000) {
				panic("Invalid latency values")
			}
		}
	}
}

// floydWarshall implements the Floyd-Warshall algorithm for all-pairs shortest paths
func floydWarshall(n int, latency [][]int) [][]int {
	dist := make([][]int, n)
	for i := range dist {
		dist[i] = make([]int, n)
		for j := range dist[i] {
			if i == j {
				dist[i][j] = 0
			} else if latency[i][j] != -1 {
				dist[i][j] = latency[i][j]
			} else {
				dist[i][j] = math.MaxInt32
			}
		}
	}

	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				if dist[i][k] != math.MaxInt32 && dist[k][j] != math.MaxInt32 {
					newDist := dist[i][k] + dist[k][j]
					if newDist < dist[i][j] {
						dist[i][j] = newDist
					}
				}
			}
		}
	}

	return dist
}

// findBestPlacement uses backtracking to find the optimal server placement
func findBestPlacement(n, k int, dist [][]int, start int, current []int,
	bestPlacement *[]int, minMaxLatency, minTotalLatency *int) {
	if len(current) == k {
		maxLatency, totalLatency := evaluatePlacement(n, dist, current)
		if maxLatency < *minMaxLatency || (maxLatency == *minMaxLatency && totalLatency < *minTotalLatency) {
			*minMaxLatency = maxLatency
			*minTotalLatency = totalLatency
			*bestPlacement = make([]int, k)
			copy(*bestPlacement, current)
		}
		return
	}

	for i := start; i < n; i++ {
		current = append(current, i)
		findBestPlacement(n, k, dist, i+1, current, bestPlacement, minMaxLatency, minTotalLatency)
		current = current[:len(current)-1]
	}
}

// evaluatePlacement calculates the maximum and total latency for a given server placement
func evaluatePlacement(n int, dist [][]int, servers []int) (int, int) {
	maxLatency := 0
	totalLatency := 0

	for node := 0; node < n; node++ {
		minDistToServer := math.MaxInt32
		for _, server := range servers {
			if dist[node][server] < minDistToServer {
				minDistToServer = dist[node][server]
			}
		}
		if minDistToServer == math.MaxInt32 {
			return math.MaxInt32, math.MaxInt32 // Disconnected component
		}
		maxLatency = max(maxLatency, minDistToServer)
		totalLatency += minDistToServer
	}

	return maxLatency, totalLatency
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}