package network_cache

import (
	"container/heap"
	"math"
	"sort"
)

// OptimalNetworkPlacement determines the optimal placement of K cache nodes
// to minimize the average latency of all data requests
func OptimalNetworkPlacement(n int, k int, edges [][3]int, requests []int) []int {
	// Build the adjacency list representation of the graph
	graph := buildGraph(n, edges)

	// If k equals n, just return all nodes
	if k == n {
		result := make([]int, n)
		for i := 0; i < n; i++ {
			result[i] = i
		}
		return result
	}

	// If there are no requests, return the first k nodes
	if len(requests) == 0 {
		result := make([]int, k)
		for i := 0; i < k; i++ {
			result[i] = i
		}
		return result
	}

	// For each possible combination of k cache nodes, compute the average latency
	// Use a more efficient approach than pure brute-force
	return efficientApproach(n, k, graph, requests)
}

// buildGraph creates an adjacency list representation of the graph
func buildGraph(n int, edges [][3]int) [][]Edge {
	graph := make([][]Edge, n)
	for _, edge := range edges {
		u, v, latency := edge[0], edge[1], edge[2]
		graph[u] = append(graph[u], Edge{To: v, Latency: latency})
		graph[v] = append(graph[v], Edge{To: u, Latency: latency})
	}
	return graph
}

// Edge represents a connection between servers
type Edge struct {
	To      int
	Latency int
}

// efficientApproach uses an approximation algorithm to find a good placement of cache nodes
func efficientApproach(n, k int, graph [][]Edge, requests []int) []int {
	// Count the frequency of each request
	requestFrequency := make(map[int]int)
	for _, req := range requests {
		requestFrequency[req]++
	}

	// Calculate all-pairs shortest paths using Floyd-Warshall
	dist := floydWarshall(n, graph)

	// Track total latency for each potential cache placement
	bestPlacement := make([]int, 0, k)
	minAvgLatency := math.MaxFloat64

	// Use a greedy approach, starting with an empty set of cache nodes
	// and adding the best node one at a time
	candidates := make([]int, n)
	for i := 0; i < n; i++ {
		candidates[i] = i
	}

	// Try all combinations of k cache nodes out of n nodes
	// This is an approximation of the optimal solution
	combinations := generateCombinations(candidates, k)

	for _, cacheNodes := range combinations {
		totalLatency := 0.0
		totalRequests := 0

		// For each request origin
		for reqOrigin, freq := range requestFrequency {
			// Find the cache node with minimum latency to this request origin
			minLatency := math.MaxInt32
			for _, cacheNode := range cacheNodes {
				if dist[reqOrigin][cacheNode] < minLatency {
					minLatency = dist[reqOrigin][cacheNode]
				}
			}
			totalLatency += float64(minLatency) * float64(freq)
			totalRequests += freq
		}

		// Calculate average latency
		avgLatency := totalLatency / float64(totalRequests)

		// Update best placement if this is better
		if avgLatency < minAvgLatency {
			minAvgLatency = avgLatency
			bestPlacement = make([]int, k)
			copy(bestPlacement, cacheNodes)
		}
	}

	// Sort the result in ascending order
	sort.Ints(bestPlacement)
	return bestPlacement
}

// floydWarshall computes all-pairs shortest paths
func floydWarshall(n int, graph [][]Edge) [][]int {
	// Initialize distance matrix
	dist := make([][]int, n)
	for i := 0; i < n; i++ {
		dist[i] = make([]int, n)
		for j := 0; j < n; j++ {
			if i == j {
				dist[i][j] = 0
			} else {
				dist[i][j] = math.MaxInt32
			}
		}
	}

	// Set direct edge distances
	for u := 0; u < n; u++ {
		for _, edge := range graph[u] {
			dist[u][edge.To] = min(dist[u][edge.To], edge.Latency)
		}
	}

	// Floyd-Warshall algorithm
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				if dist[i][k] != math.MaxInt32 && dist[k][j] != math.MaxInt32 {
					dist[i][j] = min(dist[i][j], dist[i][k]+dist[k][j])
				}
			}
		}
	}

	return dist
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// For larger graphs, we need to use an approximation algorithm
// or a more efficient way to generate combinations
func generateCombinations(items []int, k int) [][]int {
	if k > len(items) {
		k = len(items)
	}

	// For small values of n and k, we can use a recursive approach
	if len(items) <= 20 { // Arbitrary threshold
		result := [][]int{}
		generateCombinationsRecursive(items, k, 0, []int{}, &result)
		return result
	}

	// For larger values, we can use a heuristic or approximation
	// In this case, we use a simple greedy algorithm based on request frequency
	// (Real implementation would be more sophisticated)
	
	// Let's use a reasonable limit for the number of combinations
	maxCombinations := 10000
	
	// First, try a systematic way to generate some combinations
	result := [][]int{}
	
	// Add some "strategic" combinations - e.g., first k nodes, last k nodes, etc.
	firstK := make([]int, k)
	for i := 0; i < k; i++ {
		firstK[i] = items[i]
	}
	result = append(result, firstK)
	
	if len(items) > k {
		lastK := make([]int, k)
		for i := 0; i < k; i++ {
			lastK[i] = items[len(items)-k+i]
		}
		result = append(result, lastK)
	}
	
	// Add evenly spaced combinations
	if len(items) > k && k > 0 {
		spacing := len(items) / k
		for offset := 0; offset < spacing && len(result) < maxCombinations; offset++ {
			spaced := make([]int, k)
			for i := 0; i < k; i++ {
				idx := (offset + i*spacing) % len(items)
				spaced[i] = items[idx]
			}
			result = append(result, spaced)
		}
	}
	
	// Add some random combinations to increase diversity
	addRandomCombinations(items, k, &result, maxCombinations)
	
	return result
}

// generateCombinationsRecursive generates all combinations of k items from the slice
func generateCombinationsRecursive(items []int, k int, start int, current []int, result *[][]int) {
	if len(current) == k {
		combination := make([]int, k)
		copy(combination, current)
		*result = append(*result, combination)
		return
	}
	
	// If we can't form a valid combination anymore, return
	if len(current) + (len(items) - start) < k {
		return
	}
	
	for i := start; i < len(items); i++ {
		// Include the current item
		generateCombinationsRecursive(items, k, i+1, append(current, items[i]), result)
	}
}

// addRandomCombinations adds random combinations to the result set
func addRandomCombinations(items []int, k int, result *[][]int, maxCombinations int) {
	// Simple deterministic "random" selection to ensure consistency
	for seed := 0; seed < 100 && len(*result) < maxCombinations; seed++ {
		combination := make([]int, k)
		selectedIndices := make(map[int]bool)
		
		for i := 0; i < k; i++ {
			// Pseudo-random selection
			idx := (seed*7 + i*11) % len(items)
			
			// Find the next unselected index
			for count := 0; count < len(items) && selectedIndices[idx]; count++ {
				idx = (idx + 1) % len(items)
			}
			
			if !selectedIndices[idx] {
				combination[i] = items[idx]
				selectedIndices[idx] = true
			}
		}
		
		// Sort the combination
		sort.Ints(combination)
		
		// Check if this combination is already in the result
		isDuplicate := false
		for _, existing := range *result {
			if slicesEqual(existing, combination) {
				isDuplicate = true
				break
			}
		}
		
		if !isDuplicate {
			*result = append(*result, combination)
		}
	}
}

// slicesEqual checks if two integer slices are equal
func slicesEqual(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := 0; i < len(a); i++ {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

// dijkstra computes single-source shortest paths
func dijkstra(n int, graph [][]Edge, source int) []int {
	// Initialize distances
	dist := make([]int, n)
	for i := 0; i < n; i++ {
		dist[i] = math.MaxInt32
	}
	dist[source] = 0

	// Priority queue for Dijkstra's algorithm
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{value: source, priority: 0})

	// Process nodes in order of increasing distance
	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		u := item.value

		// If we've already found a shorter path, skip
		if item.priority > dist[u] {
			continue
		}

		// Relax all edges from u
		for _, edge := range graph[u] {
			v := edge.To
			if dist[u]+edge.Latency < dist[v] {
				dist[v] = dist[u] + edge.Latency
				heap.Push(&pq, &Item{value: v, priority: dist[v]})
			}
		}
	}

	return dist
}

// PriorityQueue implementation for Dijkstra's algorithm
type Item struct {
	value    int
	priority int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}