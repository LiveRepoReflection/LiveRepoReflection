package dynamicrouter

import (
	"container/heap"
	"math"
	"sync"
)

// Router represents a network router that can handle dynamic edge changes
// and compute shortest paths efficiently
type Router struct {
	n           int
	graph       map[int]map[int]int
	mu          sync.RWMutex
	invalidated bool
	distances   map[int]map[int]int
}

// NewRouter initializes a new router with n nodes
func NewRouter(n int) *Router {
	return &Router{
		n:           n,
		graph:       make(map[int]map[int]int),
		invalidated: true,
		distances:   make(map[int]map[int]int),
	}
}

// AddEdge adds an undirected edge between node1 and node2 with the given weight
// If the edge already exists, its weight is updated
func (r *Router) AddEdge(node1, node2, weight int) {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Initialize adjacency maps if they don't exist
	if _, exists := r.graph[node1]; !exists {
		r.graph[node1] = make(map[int]int)
	}
	if _, exists := r.graph[node2]; !exists {
		r.graph[node2] = make(map[int]int)
	}

	// Add/update the edge in both directions (undirected graph)
	r.graph[node1][node2] = weight
	r.graph[node2][node1] = weight

	// Mark the graph as changed so we know to recalculate distances
	r.invalidated = true
}

// RemoveEdge removes the undirected edge between node1 and node2
// If the edge doesn't exist, nothing happens
func (r *Router) RemoveEdge(node1, node2 int) {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Check if nodes exist in the graph
	if _, exists := r.graph[node1]; !exists {
		return
	}
	if _, exists := r.graph[node2]; !exists {
		return
	}

	// Remove edges in both directions
	delete(r.graph[node1], node2)
	delete(r.graph[node2], node1)

	// Mark the graph as changed
	r.invalidated = true
}

// GetShortestPath returns the shortest path weight between startNode and endNode
// Returns -1 if no path exists
func (r *Router) GetShortestPath(startNode, endNode int) int {
	// Special case: same node
	if startNode == endNode {
		return 0
	}

	r.mu.RLock()
	// Check if we can use cached distances
	if !r.invalidated {
		if distMap, ok := r.distances[startNode]; ok {
			if dist, exists := distMap[endNode]; exists {
				r.mu.RUnlock()
				return dist
			}
		}
	}
	r.mu.RUnlock()

	// Need to compute the shortest path
	return r.computeShortestPath(startNode, endNode)
}

// computeShortestPath implements Dijkstra's algorithm to find the shortest path
func (r *Router) computeShortestPath(startNode, endNode int) int {
	r.mu.Lock()
	defer r.mu.Unlock()

	// Initialize distance map for the source node if it doesn't exist
	if _, exists := r.distances[startNode]; !exists {
		r.distances[startNode] = make(map[int]int)
	}

	// Create a priority queue for Dijkstra's algorithm
	pq := make(PriorityQueue, 0)
	dist := make(map[int]int)
	
	// Initialize distances to infinity except for the start node
	for i := 0; i < r.n; i++ {
		dist[i] = math.MaxInt32
	}
	dist[startNode] = 0

	// Add start node to priority queue
	heap.Push(&pq, &Item{
		node:     startNode,
		priority: 0,
	})

	// Run Dijkstra's algorithm
	for pq.Len() > 0 {
		// Get the node with the minimum distance
		item := heap.Pop(&pq).(*Item)
		u := item.node
		
		// If we've reached the destination, we're done
		if u == endNode {
			// Cache the result
			r.distances[startNode][endNode] = dist[endNode]
			if dist[endNode] == math.MaxInt32 {
				return -1 // No path exists
			}
			return dist[endNode]
		}

		// Skip if we've already found a better path
		if item.priority > dist[u] {
			continue
		}

		// Check all neighbors of the current node
		if neighbors, exists := r.graph[u]; exists {
			for v, weight := range neighbors {
				// Calculate new distance
				newDist := dist[u] + weight
				
				// If we found a shorter path to v
				if newDist < dist[v] {
					dist[v] = newDist
					heap.Push(&pq, &Item{
						node:     v,
						priority: newDist,
					})
				}
			}
		}
	}

	// If we reach here, there's no path to the destination
	r.distances[startNode][endNode] = math.MaxInt32
	return -1
}

// PriorityQueue implementation for Dijkstra's algorithm
// Item represents a node and its priority (distance)
type Item struct {
	node     int
	priority int
	index    int
}

// PriorityQueue implements heap.Interface
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