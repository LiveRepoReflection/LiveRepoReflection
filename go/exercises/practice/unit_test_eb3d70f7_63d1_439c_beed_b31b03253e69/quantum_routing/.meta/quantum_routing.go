package quantum

import (
	"container/heap"
	"math"
)

// Edge represents a quantum communication channel between two nodes
type Edge struct {
	To       int     // The destination node of the edge
	Fidelity float64 // The fidelity of the quantum channel (0 < Fidelity <= 1)
}

// FindMostReliablePath finds the most reliable path from source to destination
// Returns the path as a slice of node IDs
func FindMostReliablePath(n int, graph [][]Edge, source, destination int) []int {
	// Handle special case: source equals destination
	if source == destination {
		return []int{source}
	}

	// Initialize data structures for Dijkstra's algorithm
	// We use negated log-fidelity as the "distance" (minimizing -log(f) is equivalent to maximizing f)
	// prev[i] will store the previous node on the most reliable path to node i
	logFidelity := make([]float64, n) // stores -log(fidelity) to the node
	prev := make([]int, n)            // Previous node in the most reliable path
	visited := make([]bool, n)        // Nodes that have been processed

	// Initialize all nodes with "infinite" distance (log(0) would be -∞, but we use a very large value)
	for i := 0; i < n; i++ {
		logFidelity[i] = math.Inf(1) // Positive infinity
		prev[i] = -1                 // No previous node yet
	}

	// Distance to the source node is 0 (log(1) = 0)
	logFidelity[source] = 0

	// Priority queue for Dijkstra's algorithm
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: source, priority: 0})

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		// Extract the node with the smallest negative log fidelity
		item := heap.Pop(pq).(*Item)
		u := item.node

		// Skip if we've already processed this node
		if visited[u] {
			continue
		}
		visited[u] = true

		// If we've reached the destination, we can break early
		if u == destination {
			break
		}

		// Explore all neighbors of u
		for _, edge := range graph[u] {
			v := edge.To

			// Skip if we've already processed this neighbor
			if visited[v] {
				continue
			}

			// Calculate the negative log fidelity for this path
			// Note: Since we're working with probabilities, we add logarithms to get the log of the product
			negLogFid := -math.Log(edge.Fidelity)
			newLogFidelity := logFidelity[u] + negLogFid

			// If this path is more reliable (smaller negative log fidelity)
			if newLogFidelity < logFidelity[v] {
				logFidelity[v] = newLogFidelity
				prev[v] = u
				heap.Push(pq, &Item{node: v, priority: newLogFidelity})
			}
		}
	}

	// If destination is unreachable, return empty path
	if !visited[destination] || math.IsInf(logFidelity[destination], 1) {
		return []int{}
	}

	// Reconstruct the path by working backwards from destination
	path := []int{}
	for at := destination; at != -1; at = prev[at] {
		path = append([]int{at}, path...) // Prepend to get the correct order
	}

	return path
}

// Item represents a node and its priority in the priority queue
type Item struct {
	node     int
	priority float64 // Priority is -log(fidelity)
	index    int     // Index in the heap (used by heap.Interface)
}

// PriorityQueue implements heap.Interface and holds Items
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	// We want a min-heap based on -log(fidelity)
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