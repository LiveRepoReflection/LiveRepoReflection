package network_optimizer

import (
	"math"
	"sort"
)

type Edge struct {
	u, v   int
	cost   int
	latency int
}

func OptimizeNetwork(n int, cost [][]int, budget int) [][]int {
	if n <= 1 {
		return [][]int{}
	}

	// Generate all possible edges
	var edges []Edge
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if cost[i][j] != -1 {
				edges = append(edges, Edge{u: i, v: j, cost: cost[i][j], latency: 1})
			}
		}
	}

	// Sort edges by cost then by potential latency reduction
	sort.Slice(edges, func(i, j int) bool {
		if edges[i].cost == edges[j].cost {
			return edges[i].latency < edges[j].latency
		}
		return edges[i].cost < edges[j].cost
	})

	// Krusky's algorithm with budget constraint
	parent := make([]int, n)
	for i := range parent {
		parent[i] = i
	}

	var result [][]int
	totalCost := 0

	var find func(int) int
	find = func(u int) int {
		if parent[u] != u {
			parent[u] = find(parent[u])
		}
		return parent[u]
	}

	for _, edge := range edges {
		if totalCost+edge.cost > budget {
			continue
		}

		rootU := find(edge.u)
		rootV := find(edge.v)

		if rootU != rootV {
			parent[rootV] = rootU
			result = append(result, []int{edge.u, edge.v})
			totalCost += edge.cost
		}
	}

	// Calculate current latency matrix
	latency := make([][]int, n)
	for i := range latency {
		latency[i] = make([]int, n)
		for j := range latency[i] {
			if i == j {
				latency[i][j] = 0
			} else {
				latency[i][j] = n * n // infinity
			}
		}
	}

	for _, edge := range result {
		u, v := edge[0], edge[1]
		latency[u][v] = 1
		latency[v][u] = 1
	}

	// Floyd-Warshall to compute all pairs shortest paths
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				if latency[i][k]+latency[k][j] < latency[i][j] {
					latency[i][j] = latency[i][k] + latency[k][j]
				}
			}
		}
	}

	// Try to add remaining edges that can improve latency
	remainingBudget := budget - totalCost
	for _, edge := range edges {
		if edge.cost > remainingBudget {
			continue
		}

		u, v := edge.u, edge.v
		if latency[u][v] > 1 {
			result = append(result, []int{u, v})
			totalCost += edge.cost
			remainingBudget -= edge.cost

			// Update latency matrix
			for i := 0; i < n; i++ {
				for j := 0; j < n; j++ {
					if latency[i][u]+1+latency[v][j] < latency[i][j] {
						latency[i][j] = latency[i][u] + 1 + latency[v][j]
					}
					if latency[i][v]+1+latency[u][j] < latency[i][j] {
						latency[i][j] = latency[i][v] + 1 + latency[u][j]
					}
				}
			}
		}
	}

	return result
}

func calculateAverageLatency(n int, edges [][]int) float64 {
	if n <= 1 {
		return 0
	}

	// Initialize latency matrix
	latency := make([][]int, n)
	for i := range latency {
		latency[i] = make([]int, n)
		for j := range latency[i] {
			if i == j {
				latency[i][j] = 0
			} else {
				latency[i][j] = n * n // infinity
			}
		}
	}

	// Set direct connections
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		latency[u][v] = 1
		latency[v][u] = 1
	}

	// Floyd-Warshall algorithm
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				if latency[i][k]+latency[k][j] < latency[i][j] {
					latency[i][j] = latency[i][k] + latency[k][j]
				}
			}
		}
	}

	// Calculate average
	total := 0
	count := 0
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if latency[i][j] < n*n {
				total += latency[i][j]
			}
			count++
		}
	}

	if count == 0 {
		return math.Inf(1)
	}
	return float64(total) / float64(count)
}