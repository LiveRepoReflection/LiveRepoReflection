package network_split

import (
	"math"
	"sort"
)

// SplitNetwork implements the network partitioning algorithm
func SplitNetwork(n, m, M, k int, resilience []int, edges [][]float64) []int {
	// Create adjacency list representation
	adj := make(map[int][]edge)
	for _, e := range edges {
		u, v := int(e[0]), int(e[1])
		reliability := e[2]
		adj[u] = append(adj[u], edge{to: v, reliability: reliability})
		adj[v] = append(adj[v], edge{to: u, reliability: reliability})
	}

	// Initialize best solution tracking
	bestPartition := make([]int, n)
	bestScore := math.MaxFloat64
	found := false

	// Try different initial partitions using a greedy approach
	for start := 0; start < n; start++ {
		partition := make([]int, n)
		for i := range partition {
			partition[i] = -1
		}

		if tryPartition(n, m, M, k, resilience, adj, partition, start) {
			score := evaluatePartition(n, k, resilience, edges, partition)
			if !found || score < bestScore {
				copy(bestPartition, partition)
				bestScore = score
				found = true
			}
		}
	}

	if !found {
		return nil
	}
	return bestPartition
}

type edge struct {
	to          int
	reliability float64
}

// tryPartition attempts to create a valid partitioning starting from a given node
func tryPartition(n, m, M, k int, resilience []int, adj map[int][]edge, partition []int, start int) bool {
	// Initialize clusters with balanced sizes
	targetSize := n / k
	remaining := make([]int, k)
	for i := range remaining {
		remaining[i] = targetSize
		if i < n%k {
			remaining[i]++
		}
	}

	// Start with the first cluster
	return assignClusters(n, m, M, k, resilience, adj, partition, remaining, start)
}

// assignClusters recursively assigns nodes to clusters
func assignClusters(n, m, M, k int, resilience []int, adj map[int][]edge, partition []int, remaining []int, node int) bool {
	if node >= n {
		return isValidPartition(n, m, M, k, resilience, adj, partition)
	}

	if partition[node] != -1 {
		return assignClusters(n, m, M, k, resilience, adj, partition, remaining, node+1)
	}

	// Try assigning the current node to each possible cluster
	candidates := getPriorityClusters(n, node, k, adj, partition, remaining)
	for _, cluster := range candidates {
		if remaining[cluster] > 0 && remaining[cluster] <= M {
			partition[node] = cluster
			remaining[cluster]--

			if assignClusters(n, m, M, k, resilience, adj, partition, remaining, node+1) {
				return true
			}

			partition[node] = -1
			remaining[cluster]++
		}
	}

	return false
}

// getPriorityClusters returns clusters sorted by priority for assignment
func getPriorityClusters(n, node, k int, adj map[int][]edge, partition []int, remaining []int) []int {
	type clusterScore struct {
		cluster int
		score   float64
	}
	scores := make([]clusterScore, 0, k)

	for c := 0; c < k; c++ {
		if remaining[c] <= 0 {
			continue
		}

		// Calculate connectivity score
		connectivity := 0.0
		for _, e := range adj[node] {
			if partition[e.to] == c {
				connectivity += e.reliability
			}
		}
		scores = append(scores, clusterScore{c, connectivity})
	}

	sort.Slice(scores, func(i, j int) bool {
		return scores[i].score > scores[j].score
	})

	result := make([]int, len(scores))
	for i, s := range scores {
		result[i] = s.cluster
	}
	return result
}

// isValidPartition checks if the current partitioning is valid
func isValidPartition(n, m, M, k int, resilience []int, adj map[int][]edge, partition []int) bool {
	// Check cluster sizes
	sizes := make([]int, k)
	for _, c := range partition {
		if c < 0 || c >= k {
			return false
		}
		sizes[c]++
	}
	for _, size := range sizes {
		if size < m || size > M {
			return false
		}
	}

	// Check connectivity within clusters
	for cluster := 0; cluster < k; cluster++ {
		if !isConnected(n, adj, partition, cluster) {
			return false
		}
	}

	return true
}

// isConnected checks if nodes in a cluster form a connected component
func isConnected(n int, adj map[int][]edge, partition []int, cluster int) bool {
	// Find first node in cluster
	start := -1
	for i := 0; i < n; i++ {
		if partition[i] == cluster {
			start = i
			break
		}
	}
	if start == -1 {
		return true
	}

	// BFS to check connectivity
	visited := make(map[int]bool)
	queue := []int{start}
	visited[start] = true

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]

		for _, e := range adj[curr] {
			if partition[e.to] == cluster && !visited[e.to] {
				visited[e.to] = true
				queue = append(queue, e.to)
			}
		}
	}

	// Check if all nodes in cluster are visited
	for i := 0; i < n; i++ {
		if partition[i] == cluster && !visited[i] {
			return false
		}
	}

	return true
}

// evaluatePartition calculates the score for a partition
func evaluatePartition(n, k int, resilience []int, edges [][]float64, partition []int) float64 {
	// Calculate resilience balance
	clusterResilience := make([]float64, k)
	for i := 0; i < n; i++ {
		clusterResilience[partition[i]] += float64(resilience[i])
	}

	maxDiff := 0.0
	for i := 0; i < k; i++ {
		for j := i + 1; j < k; j++ {
			diff := math.Abs(clusterResilience[i] - clusterResilience[j])
			if diff > maxDiff {
				maxDiff = diff
			}
		}
	}

	// Calculate inter-cluster reliability
	interReliability := 0.0
	for _, e := range edges {
		u, v := int(e[0]), int(e[1])
		if partition[u] != partition[v] {
			interReliability += e[2]
		}
	}

	// Combine scores (lower is better)
	return maxDiff - interReliability
}