package optimal_router

import (
	"container/heap"
	"math"
)

type Edge struct {
	to      int
	latency int
}

type Node struct {
	id       int
	distance int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].distance < pq[j].distance }
func (pq PriorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*Node))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func OptimalRouter(N int, M int, links [][]int, queries [][]int) []int {
	// Build adjacency list
	adj := make([][]Edge, N)
	for _, link := range links {
		u, v, latency := link[0], link[1], link[2]
		adj[u] = append(adj[u], Edge{v, latency})
		adj[v] = append(adj[v], Edge{u, latency})
	}

	results := make([]int, len(queries))
	for i, query := range queries {
		start, end, deadline := query[0], query[1], query[2]
		results[i] = findMaxBandwidth(N, adj, start, end, deadline)
	}
	return results
}

func findMaxBandwidth(N int, adj [][]Edge, start, end, deadline int) int {
	// Binary search for maximum bandwidth
	low := 1
	high := 1000000
	best := 0

	for low <= high {
		mid := (low + high) / 2
		if isPathPossible(N, adj, start, end, deadline, mid) {
			best = mid
			low = mid + 1
		} else {
			high = mid - 1
		}
	}

	return best
}

func isPathPossible(N int, adj [][]Edge, start, end, deadline, bandwidth int) bool {
	dist := make([]int, N)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[start] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Node{id: start, distance: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)
		if current.id == end {
			break
		}

		if current.distance > dist[current.id] {
			continue
		}

		for _, edge := range adj[current.id] {
			// Only consider edges with sufficient bandwidth
			if edge.latency < 0 {
				continue
			}

			newDist := current.distance + edge.latency
			if newDist < dist[edge.to] && newDist <= deadline {
				dist[edge.to] = newDist
				heap.Push(&pq, &Node{id: edge.to, distance: newDist})
			}
		}
	}

	return dist[end] <= deadline
}