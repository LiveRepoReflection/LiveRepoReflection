package routeoptim

import (
	"container/heap"
	"math"
	"sync"
	"time"
)

type routeOptimizer struct {
	nodes     int
	adj       [][]edge
	vehicles  int
	mu        sync.Mutex
	busyUntil []int64
}

type edge struct {
	to   int
	cost int
}

// PriorityQueue implementation for Dijkstra's algorithm
type Item struct {
	node     int
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

func NewRouteOptimizer(nodes int, edges []Edge, vehicles int) RouteOptimizer {
	optimizer := &routeOptimizer{
		nodes:     nodes,
		adj:       make([][]edge, nodes),
		vehicles:  vehicles,
		busyUntil: make([]int64, vehicles),
	}

	// Build adjacency list
	for _, e := range edges {
		optimizer.adj[e.From] = append(optimizer.adj[e.From], edge{to: e.To, cost: e.Cost})
	}

	return optimizer
}

func (r *routeOptimizer) ProcessRequest(request DeliveryRequest) bool {
	// Calculate shortest path cost using Dijkstra's algorithm
	cost := r.shortestPath(request.Start, request.End)
	if cost == math.MaxInt32 {
		return false // No path exists
	}

	// Check if path can be completed before deadline
	// Assume 1 cost unit = 1 second for simplicity
	currentTime := time.Now().Unix()
	if currentTime+int64(cost) > request.Deadline {
		return false
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	// Find earliest available vehicle
	earliestVehicle := -1
	earliestTime := int64(math.MaxInt64)
	for i := 0; i < r.vehicles; i++ {
		if r.busyUntil[i] < earliestTime {
			earliestTime = r.busyUntil[i]
			earliestVehicle = i
		}
	}

	// Check if we can complete delivery with earliest available vehicle
	if earliestTime > request.Deadline {
		return false
	}

	startTime := max(currentTime, earliestTime)
	if startTime+int64(cost) > request.Deadline {
		return false
	}

	// Assign vehicle and update its busy time
	r.busyUntil[earliestVehicle] = startTime + int64(cost)
	return true
}

func (r *routeOptimizer) shortestPath(start, end int) int {
	// Initialize distances
	dist := make([]int, r.nodes)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[start] = 0

	// Initialize priority queue
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: start, priority: 0})

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		if current.node == end {
			return current.priority
		}

		if current.priority > dist[current.node] {
			continue
		}

		for _, e := range r.adj[current.node] {
			newDist := dist[current.node] + e.cost
			if newDist < dist[e.to] {
				dist[e.to] = newDist
				heap.Push(&pq, &Item{node: e.to, priority: newDist})
			}
		}
	}

	return math.MaxInt32
}

func max(a, b int64) int64 {
	if a > b {
		return a
	}
	return b
}