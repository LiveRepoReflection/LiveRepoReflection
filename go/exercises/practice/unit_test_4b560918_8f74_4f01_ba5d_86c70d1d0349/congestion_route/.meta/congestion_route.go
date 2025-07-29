package congestion_route

import (
	"math"
)

type edge struct {
	to     int
	latency int
}

func FindOptimalRoute(n int, edges [][]int, congestion []int, M int, S int, D int, K int) []int {
	// If source equals destination, return immediately.
	if S == D {
		return []int{S}
	}

	// Build graph as adjancency list.
	graph := make([][]edge, n)
	for _, e := range edges {
		u, v, latency := e[0], e[1], e[2]
		graph[u] = append(graph[u], edge{to: v, latency: latency})
	}

	// dp[k][v] = minimal cost to reach node v with exactly k hops.
	// parent[k][v] = previous node u that leads to v at hop count k.
	dp := make([][]float64, K+1)
	parent := make([][]int, K+1)
	for i := 0; i <= K; i++ {
		dp[i] = make([]float64, n)
		parent[i] = make([]int, n)
		for j := 0; j < n; j++ {
			dp[i][j] = math.Inf(1)
			parent[i][j] = -1
		}
	}
	dp[0][S] = 0

	// Relax edges for each hop count.
	for hop := 0; hop < K; hop++ {
		for u := 0; u < n; u++ {
			if dp[hop][u] == math.Inf(1) {
				continue
			}
			for _, ed := range graph[u] {
				// Calculate effective cost: latency * (1 + congestion[v]/M)
				// Since M and congestion[v] are integers, we compute as a float.
				effCost := float64(ed.latency) * (1.0 + float64(congestion[ed.to])/float64(M))
				newCost := dp[hop][u] + effCost
				if newCost < dp[hop+1][ed.to] {
					dp[hop+1][ed.to] = newCost
					parent[hop+1][ed.to] = u
				}
			}
		}
	}

	// Find the best route to destination within 1 to K hops.
	bestCost := math.Inf(1)
	bestHop := -1
	for hop := 1; hop <= K; hop++ {
		if dp[hop][D] < bestCost {
			bestCost = dp[hop][D]
			bestHop = hop
		}
	}

	if bestHop == -1 {
		return []int{}
	}

	// Reconstruct the path from destination back to source.
	path := make([]int, 0, bestHop+1)
	curr := D
	hop := bestHop
	for hop > 0 {
		path = append(path, curr)
		curr = parent[hop][curr]
		hop--
	}
	path = append(path, S)
	
	// Reverse the path to get correct order.
	for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
		path[i], path[j] = path[j], path[i]
	}
	return path
}