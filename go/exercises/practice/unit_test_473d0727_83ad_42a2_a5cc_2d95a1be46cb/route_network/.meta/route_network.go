package route

import (
	"container/heap"
	"math"
	"strconv"
	"strings"
)

// Network represents the network topology and operations
type Network struct {
	n     int
	links map[int]map[int]int // adjacency map: from -> to -> latency
}

// New creates a new Network instance
func New(n int) *Network {
	return &Network{
		n:     n,
		links: make(map[int]map[int]int),
	}
}

// AddLink adds a bidirectional link between two nodes
func (n *Network) AddLink(u, v, latency int) {
	// Initialize maps if they don't exist
	if n.links[u] == nil {
		n.links[u] = make(map[int]int)
	}
	if n.links[v] == nil {
		n.links[v] = make(map[int]int)
	}

	// Add bidirectional link if it doesn't exist
	if _, exists := n.links[u][v]; !exists {
		n.links[u][v] = latency
		n.links[v][u] = latency
	}
}

// RemoveLink removes a bidirectional link between two nodes
func (n *Network) RemoveLink(u, v int) {
	if n.links[u] != nil {
		delete(n.links[u], v)
	}
	if n.links[v] != nil {
		delete(n.links[v], u)
	}
}

// findShortestPath finds the shortest path between source and destination using Dijkstra's algorithm
func (n *Network) findShortestPath(source, destination int) int {
	// Initialize distances
	dist := make([]int, n.n)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[source] = 0

	// Priority queue for Dijkstra's algorithm
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: source, priority: 0})

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		
		if current.node == destination {
			return current.priority
		}

		// If we've found a longer path to current node, skip
		if current.priority > dist[current.node] {
			continue
		}

		// Check all neighbors
		for neighbor, latency := range n.links[current.node] {
			newDist := dist[current.node] + latency

			if newDist < dist[neighbor] {
				dist[neighbor] = newDist
				heap.Push(pq, &Item{node: neighbor, priority: newDist})
			}
		}
	}

	return -1 // No path found
}

// ProcessQuery processes a single query and returns the result if it's a route query
func (n *Network) ProcessQuery(query string) *int {
	parts := strings.Split(query, " ")
	command := parts[0]

	switch command {
	case "add":
		u, _ := strconv.Atoi(parts[1])
		v, _ := strconv.Atoi(parts[2])
		latency, _ := strconv.Atoi(parts[3])
		n.AddLink(u, v, latency)
		return nil

	case "remove":
		u, _ := strconv.Atoi(parts[1])
		v, _ := strconv.Atoi(parts[2])
		n.RemoveLink(u, v)
		return nil

	case "route":
		source, _ := strconv.Atoi(parts[1])
		destination, _ := strconv.Atoi(parts[2])
		result := n.findShortestPath(source, destination)
		return &result

	default:
		return nil
	}
}

// Item represents an item in the priority queue
type Item struct {
	node     int
	priority int
	index    int
}

// PriorityQueue implements heap.Interface and holds Items
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