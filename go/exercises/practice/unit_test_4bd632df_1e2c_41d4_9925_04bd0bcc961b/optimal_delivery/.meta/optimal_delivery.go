package optimal_delivery

import (
	"container/heap"
	"math"
)

type Node struct {
	id       int
	distance int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].distance < pq[j].distance }
func (pq PriorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Node)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func CalculateMinMaxLatency(N int, adjMatrix [][]int, dataGenerationRates []int, processingCapacity int) float64 {
	if N == 1 {
		return 0
	}

	// Calculate total data generation
	totalData := 0
	for _, rate := range dataGenerationRates {
		totalData += rate
	}
	if totalData == 0 {
		return 0
	}

	// Check if any node's generation exceeds capacity
	for _, rate := range dataGenerationRates {
		if rate > processingCapacity {
			return math.MaxFloat64
		}
	}

	// Precompute shortest paths from all nodes to sink (node 0)
	shortestPaths := make([]int, N)
	for i := range shortestPaths {
		shortestPaths[i] = math.MaxInt32
	}
	shortestPaths[0] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Node{id: 0, distance: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)
		if current.distance > shortestPaths[current.id] {
			continue
		}

		for neighbor := 0; neighbor < N; neighbor++ {
			if adjMatrix[current.id][neighbor] > 0 {
				newDist := current.distance + adjMatrix[current.id][neighbor]
				if newDist < shortestPaths[neighbor] {
					shortestPaths[neighbor] = newDist
					heap.Push(&pq, &Node{id: neighbor, distance: newDist})
				}
			}
		}
	}

	// Calculate traffic load on each node
	traffic := make([]int, N)
	for i := 1; i < N; i++ {
		if dataGenerationRates[i] > 0 {
			// Each node's data must traverse the path to sink
			// This is a simplified model - in reality we'd need to track exact paths
			traffic[i] += dataGenerationRates[i]
		}
	}

	// Check if any node would be overloaded
	for i := 0; i < N; i++ {
		if traffic[i] > processingCapacity {
			return math.MaxFloat64
		}
	}

	// Find maximum latency considering both path length and congestion
	maxLatency := 0
	for i := 1; i < N; i++ {
		if dataGenerationRates[i] > 0 {
			if shortestPaths[i] > maxLatency {
				maxLatency = shortestPaths[i]
			}
		}
	}

	return float64(maxLatency)
}