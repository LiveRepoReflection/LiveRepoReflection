package optimal_routing

import (
	"container/heap"
	"math"
	"sync"
	"time"
)

// FindOptimalRoute calculates the lowest latency path from startNode to endNode
// within the given time constraint (max_time)
func FindOptimalRoute(startNode, endNode int, adj [][]int, costs [][]int, maxTime int) int {
	// Edge case: if start and end are the same, return 0
	if startNode == endNode {
		return 0
	}

	// Create a timeout channel
	timeout := time.After(time.Duration(maxTime) * time.Millisecond)

	// Result channel for the Dijkstra algorithm
	resultChan := make(chan int, 1)

	// Run Dijkstra's algorithm in a goroutine to respect time constraint
	go func() {
		// Use a priority queue implementation for Dijkstra's algorithm
		result := dijkstra(startNode, endNode, adj, costs)
		resultChan <- result
	}()

	// Wait for either the result or timeout
	select {
	case result := <-resultChan:
		return result
	case <-timeout:
		// If timeout occurred, return -1
		return -1
	}
}

// dijkstra implements Dijkstra's algorithm to find the shortest path
func dijkstra(startNode, endNode int, adj [][]int, costs [][]int) int {
	n := len(adj)
	dist := make([]int, n)
	visited := make([]bool, n)

	// Initialize distances to infinity
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[startNode] = 0

	// Create a priority queue
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: startNode, priority: 0})

	// Process nodes in order of increasing distance
	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		u := item.node

		// Skip if we've already processed this node
		if visited[u] {
			continue
		}
		visited[u] = true

		// If we've reached the end node, return the distance
		if u == endNode {
			return dist[u]
		}

		// Check all neighbors of u
		for _, v := range adj[u] {
			if !visited[v] {
				newDist := dist[u] + costs[u][v]

				// Update distance if shorter path found
				if newDist < dist[v] {
					dist[v] = newDist
					heap.Push(pq, &Item{node: v, priority: newDist})
				}
			}
		}
	}

	// If we've explored all reachable nodes and haven't found endNode, no path exists
	return -1
}

// Item represents a node with its priority in the priority queue
type Item struct {
	node     int
	priority int
	index    int // used by the heap.Interface
}

// PriorityQueue implements the heap.Interface
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
	old[n-1] = nil  // avoid memory leak
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// More efficient version of Dijkstra with caching
type PathCache struct {
	mu    sync.RWMutex
	cache map[int]map[int]int       // maps startNode -> endNode -> cost
	adj   [][]int                   // last known adjacency list (for invalidation check)
	costs [][]int                   // last known costs (for invalidation check)
	valid bool                      // is cache valid?
}

var globalCache = &PathCache{
	cache: make(map[int]map[int]int),
	valid: false,
}

// findOptimalRouteWithCache uses caching to improve performance for repeated queries
func findOptimalRouteWithCache(startNode, endNode int, adj [][]int, costs [][]int, maxTime int) int {
	// Edge case: if start and end are the same, return 0
	if startNode == endNode {
		return 0
	}

	// Create a timeout channel
	timeout := time.After(time.Duration(maxTime) * time.Millisecond)

	// Result channel
	resultChan := make(chan int, 1)

	// Try using cache first
	go func() {
		globalCache.mu.RLock()
		if globalCache.valid && isNetworkSame(adj, costs, globalCache.adj, globalCache.costs) {
			// Network topology and costs are the same, cache might be valid
			if startMap, ok := globalCache.cache[startNode]; ok {
				if cost, ok := startMap[endNode]; ok {
					globalCache.mu.RUnlock()
					resultChan <- cost
					return
				}
			}
		}
		globalCache.mu.RUnlock()

		// Cache miss or invalid cache, compute path
		result := dijkstra(startNode, endNode, adj, costs)

		// Update cache
		globalCache.mu.Lock()
		defer globalCache.mu.Unlock()

		// Update network reference
		globalCache.adj = deepCopyAdj(adj)
		globalCache.costs = deepCopyCosts(costs)
		globalCache.valid = true

		// Store result in cache
		if _, ok := globalCache.cache[startNode]; !ok {
			globalCache.cache[startNode] = make(map[int]int)
		}
		globalCache.cache[startNode][endNode] = result

		resultChan <- result
	}()

	// Wait for either the result or timeout
	select {
	case result := <-resultChan:
		return result
	case <-timeout:
		// If timeout occurred, return -1
		return -1
	}
}

// isNetworkSame checks if the network topology and costs are the same
func isNetworkSame(adj1, costs1, adj2, costs2 [][]int) bool {
	if len(adj1) != len(adj2) {
		return false
	}

	// Quick check for reference equality
	if &adj1 == &adj2 && &costs1 == &costs2 {
		return true
	}

	// Check adjacency lists
	for i := 0; i < len(adj1); i++ {
		if len(adj1[i]) != len(adj2[i]) {
			return false
		}
		
		// Since adj contains node IDs, ordering matters
		for j := 0; j < len(adj1[i]); j++ {
			if adj1[i][j] != adj2[i][j] {
				return false
			}
		}
	}

	// Check costs matrix
	for i := 0; i < len(costs1); i++ {
		for j := 0; j < len(costs1[i]); j++ {
			if costs1[i][j] != costs2[i][j] {
				return false
			}
		}
	}

	return true
}

// deepCopyAdj creates a deep copy of the adjacency list
func deepCopyAdj(adj [][]int) [][]int {
	result := make([][]int, len(adj))
	for i, neighbors := range adj {
		result[i] = make([]int, len(neighbors))
		copy(result[i], neighbors)
	}
	return result
}

// deepCopyCosts creates a deep copy of the costs matrix
func deepCopyCosts(costs [][]int) [][]int {
	result := make([][]int, len(costs))
	for i, row := range costs {
		result[i] = make([]int, len(row))
		copy(result[i], row)
	}
	return result
}