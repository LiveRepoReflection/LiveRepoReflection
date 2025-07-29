package interplanetary_network

import (
	"container/heap"
	"math"
)

// pqItem represents an item in the priority queue
type pqItem struct {
	planet    int
	distance  float64
	priority  float64
}

// priorityQueue implements heap.Interface
type priorityQueue []*pqItem

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *priorityQueue) Push(x interface{}) {
	item := x.(*pqItem)
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// MinimumNetworkCost calculates the minimum cost to establish a connected network
// spanning all planets at the target time using Prim's algorithm with optimizations
// to minimize distance function calls
func MinimumNetworkCost(n int, targetTime int64, distance func(planet1, planet2 int, time int64) float64) float64 {
	if n <= 1 {
		return 0
	}

	// Initialize visited array and total cost
	visited := make([]bool, n)
	totalCost := 0.0

	// Create priority queue for Prim's algorithm
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	// Start with planet 0
	visited[0] = true

	// Add all edges from planet 0 to priority queue
	for i := 1; i < n; i++ {
		dist := distance(0, i, targetTime)
		heap.Push(&pq, &pqItem{
			planet:    i,
			distance:  dist,
			priority:  dist,
		})
	}

	// Track number of planets connected
	connectedCount := 1

	// Process until all planets are connected
	for connectedCount < n && pq.Len() > 0 {
		item := heap.Pop(&pq).(*pqItem)
		planet := item.planet

		if visited[planet] {
			continue
		}

		// Add this edge to our minimum spanning tree
		visited[planet] = true
		totalCost += item.distance
		connectedCount++

		// Add all edges from this planet to unvisited planets
		for i := 0; i < n; i++ {
			if !visited[i] {
				dist := distance(planet, i, targetTime)
				heap.Push(&pq, &pqItem{
					planet:    i,
					distance:  dist,
					priority:  dist,
				})
			}
		}
	}

	// Check if we have a fully connected network
	if connectedCount < n {
		return math.Inf(1)
	}

	return totalCost
}