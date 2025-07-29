package adaptive_routing

import (
	"container/heap"
	"errors"
	"fmt"
	"sync"
)

// AdaptiveRouter interface defines the methods required for the adaptive routing system
type AdaptiveRouter interface {
	// AddNode adds a node with the given ID to the network
	AddNode(nodeID int)
	
	// RemoveNode removes the node with the given ID from the network
	RemoveNode(nodeID int)
	
	// AddLink establishes a directed link from source to destination
	AddLink(source, destination int)
	
	// RemoveLink removes the directed link from source to destination
	RemoveLink(source, destination int)
	
	// FindShortestPath finds the shortest path from source to destination
	// Returns the path as a slice of node IDs and an error if no path exists
	FindShortestPath(source, destination int) ([]int, error)
}

// router implements the AdaptiveRouter interface
type router struct {
	// adjacencyList represents the network graph (node -> neighbors)
	adjacencyList map[int]map[int]bool
	// nodeMutex protects the graph structure during concurrent operations
	nodeMutex sync.RWMutex
	// pathCache caches frequently requested paths
	pathCache     map[pathKey][]int
	pathCacheMu   sync.RWMutex
	cacheCapacity int
}

// pathKey is used as a key for caching paths
type pathKey struct {
	source, destination int
}

// NewAdaptiveRouter creates and returns a new instance of AdaptiveRouter
func NewAdaptiveRouter() AdaptiveRouter {
	return &router{
		adjacencyList: make(map[int]map[int]bool),
		pathCache:     make(map[pathKey][]int),
		cacheCapacity: 1000, // Can be adjusted based on requirements
	}
}

// AddNode adds a node with the given ID to the network
func (r *router) AddNode(nodeID int) {
	r.nodeMutex.Lock()
	defer r.nodeMutex.Unlock()
	
	// If the node doesn't exist, add it
	if _, exists := r.adjacencyList[nodeID]; !exists {
		r.adjacencyList[nodeID] = make(map[int]bool)
	}
	
	// Clear cache as topology has changed
	r.clearCache()
}

// RemoveNode removes the node with the given ID from the network
func (r *router) RemoveNode(nodeID int) {
	r.nodeMutex.Lock()
	defer r.nodeMutex.Unlock()
	
	// Remove the node from the adjacency list
	delete(r.adjacencyList, nodeID)
	
	// Remove any links to this node from other nodes
	for node, neighbors := range r.adjacencyList {
		delete(neighbors, nodeID)
		r.adjacencyList[node] = neighbors
	}
	
	// Clear cache as topology has changed
	r.clearCache()
}

// AddLink establishes a directed link from source to destination
func (r *router) AddLink(source, destination int) {
	r.nodeMutex.Lock()
	defer r.nodeMutex.Unlock()
	
	// Ensure nodes exist
	if _, exists := r.adjacencyList[source]; !exists {
		r.adjacencyList[source] = make(map[int]bool)
	}
	if _, exists := r.adjacencyList[destination]; !exists {
		r.adjacencyList[destination] = make(map[int]bool)
	}
	
	// Add the link
	r.adjacencyList[source][destination] = true
	
	// Clear cache as topology has changed
	r.clearCache()
}

// RemoveLink removes the directed link from source to destination
func (r *router) RemoveLink(source, destination int) {
	r.nodeMutex.Lock()
	defer r.nodeMutex.Unlock()
	
	// Check if source exists
	if neighbors, exists := r.adjacencyList[source]; exists {
		// Remove the link
		delete(neighbors, destination)
	}
	
	// Clear cache as topology has changed
	r.clearCache()
}

// FindShortestPath finds the shortest path from source to destination
func (r *router) FindShortestPath(source, destination int) ([]int, error) {
	// Check cache first
	if path, found := r.getCachedPath(source, destination); found {
		return path, nil
	}
	
	r.nodeMutex.RLock()
	defer r.nodeMutex.RUnlock()
	
	// Check if source and destination exist
	if _, exists := r.adjacencyList[source]; !exists {
		return nil, errors.New("source node does not exist")
	}
	if _, exists := r.adjacencyList[destination]; !exists {
		return nil, errors.New("destination node does not exist")
	}
	
	// Use Dijkstra's algorithm to find the shortest path
	path, err := r.findPathDijkstra(source, destination)
	if err != nil {
		return nil, err
	}
	
	// Cache the result
	r.cachePathResult(source, destination, path)
	
	return path, nil
}

// Item is an element in the priority queue
type Item struct {
	node     int
	distance int
	index    int // for priority queue functionality
}

// PriorityQueue implements heap.Interface and holds Items
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
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

// findPathDijkstra uses Dijkstra's algorithm to find the shortest path
func (r *router) findPathDijkstra(source, destination int) ([]int, error) {
	// Initialize distances map and previous node map
	distances := make(map[int]int)
	previous := make(map[int]int)
	
	// Initialize priority queue
	pq := make(PriorityQueue, 0)
	
	// Initialize with source node
	sourceItem := &Item{node: source, distance: 0}
	heap.Push(&pq, sourceItem)
	distances[source] = 0
	
	// Visit all nodes
	for pq.Len() > 0 {
		// Get the node with the smallest distance
		current := heap.Pop(&pq).(*Item)
		
		// If we've reached the destination, we can stop
		if current.node == destination {
			break
		}
		
		// Check if this is the best distance to this node
		if dist, exists := distances[current.node]; exists && current.distance > dist {
			continue
		}
		
		// Visit all neighbors
		for neighbor := range r.adjacencyList[current.node] {
			// Calculate distance to neighbor
			newDist := distances[current.node] + 1 // Each hop has a cost of 1
			
			// If we've found a shorter path to the neighbor
			if dist, exists := distances[neighbor]; !exists || newDist < dist {
				distances[neighbor] = newDist
				previous[neighbor] = current.node
				
				// Add neighbor to priority queue
				heap.Push(&pq, &Item{node: neighbor, distance: newDist})
			}
		}
	}
	
	// If destination is not reachable
	if _, exists := distances[destination]; !exists {
		return nil, fmt.Errorf("no path from %d to %d", source, destination)
	}
	
	// Reconstruct the path from source to destination
	path := []int{}
	for at := destination; at != source; at = previous[at] {
		path = append([]int{at}, path...)
	}
	path = append([]int{source}, path...)
	
	return path, nil
}

// getCachedPath attempts to retrieve a path from the cache
func (r *router) getCachedPath(source, destination int) ([]int, bool) {
	r.pathCacheMu.RLock()
	defer r.pathCacheMu.RUnlock()
	
	key := pathKey{source: source, destination: destination}
	path, found := r.pathCache[key]
	if found {
		// Return a copy to prevent modification
		pathCopy := make([]int, len(path))
		copy(pathCopy, path)
		return pathCopy, true
	}
	return nil, false
}

// cachePathResult stores a path in the cache
func (r *router) cachePathResult(source, destination int, path []int) {
	r.pathCacheMu.Lock()
	defer r.pathCacheMu.Unlock()
	
	// Check if cache is full and needs cleanup
	if len(r.pathCache) >= r.cacheCapacity {
		// Simple strategy: clear the entire cache
		r.pathCache = make(map[pathKey][]int)
	}
	
	// Store a copy of the path
	key := pathKey{source: source, destination: destination}
	pathCopy := make([]int, len(path))
	copy(pathCopy, path)
	r.pathCache[key] = pathCopy
}

// clearCache clears the path cache
func (r *router) clearCache() {
	r.pathCacheMu.Lock()
	defer r.pathCacheMu.Unlock()
	r.pathCache = make(map[pathKey][]int)
}