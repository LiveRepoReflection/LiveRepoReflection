package network

import (
	"sort"
	"sync"
)

// ReachableNodes returns all nodes that are reachable from the sourceNode in the given graph.
// The returned slice contains node IDs in sorted order.
func ReachableNodes(graph map[int][]int, sourceNode int) []int {
	// If the source node is not in the graph, return an empty slice
	if _, exists := graph[sourceNode]; !exists {
		return []int{}
	}

	// Use a map to track visited nodes for O(1) lookups
	visited := make(map[int]bool)
	
	// Use a slice to collect the reachable nodes
	var reachable []int

	// Use depth-first search to find all reachable nodes
	var dfs func(node int)
	dfs = func(node int) {
		// If this node has already been visited, return
		if visited[node] {
			return
		}

		// Mark this node as visited
		visited[node] = true

		// If this is not the source node, add it to the reachable nodes list
		if node != sourceNode {
			reachable = append(reachable, node)
		}

		// Visit all adjacent nodes
		for _, neighbor := range graph[node] {
			dfs(neighbor)
		}
	}

	// Start DFS from the source node
	dfs(sourceNode)

	// Sort the reachable nodes slice for consistent output
	sort.Ints(reachable)
	return reachable
}

// AverageLatency calculates the average latency across all edges in the network
// using the provided latency function and limiting concurrency to the specified level.
func AverageLatency(edges [][]int, latencyFunction func(int, int) int, concurrency int) float64 {
	// Handle empty edge list
	if len(edges) == 0 {
		return 0.0
	}

	// Limit concurrency to the number of edges if specified concurrency is higher
	if concurrency > len(edges) {
		concurrency = len(edges)
	}

	// Channel to distribute work
	edgeChan := make(chan []int, concurrency)
	
	// Channel to collect results
	resultChan := make(chan int, concurrency)

	// Create a WaitGroup to wait for all workers to finish
	var wg sync.WaitGroup

	// Start worker goroutines
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for edge := range edgeChan {
				// Calculate latency for this edge
				latency := latencyFunction(edge[0], edge[1])
				resultChan <- latency
			}
		}()
	}

	// Send edges to the workers
	go func() {
		for _, edge := range edges {
			edgeChan <- edge
		}
		// Close the channel when all edges have been sent
		close(edgeChan)
	}()

	// Close the result channel when all workers finish
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	// Collect and aggregate results
	totalLatency := 0
	count := 0
	for latency := range resultChan {
		totalLatency += latency
		count++
	}

	// Calculate and return the average latency
	return float64(totalLatency) / float64(count)
}